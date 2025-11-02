"""
Orchestration Engine Core.

Manages complex multi-service workflows, state transitions, and coordination.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

from ..libraries.dox_workflow_core import WorkflowRunner, WorkflowState
from .state_manager import StateManager
from .event_publisher import EventPublisher
from .service_connector import ServiceConnector


class OrchestrationEngine:
    """Core orchestration engine for multi-service workflows."""

    def __init__(self, workflow_runner: WorkflowRunner, state_manager: StateManager,
                 event_publisher: EventPublisher, service_connector: ServiceConnector):
        """Initialize orchestration engine."""
        self.workflow_runner = workflow_runner
        self.state_manager = state_manager
        self.event_publisher = event_publisher
        self.service_connector = service_connector
        self.active_orchestrations: Dict[str, Dict[str, Any]] = {}

    def start_workflow(self, rule_name: str, context: Dict[str, Any],
                      workflow_id: Optional[str] = None) -> str:
        """Start a new orchestrated workflow."""
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())

        # Create orchestration record
        self.active_orchestrations[workflow_id] = {
            "workflow_id": workflow_id,
            "rule_name": rule_name,
            "context": context.copy(),
            "start_time": datetime.utcnow().isoformat(),
            "status": WorkflowState.RUNNING.value,
            "orchestration_type": "simple",
            "sub_workflows": []
        }

        try:
            # Start the workflow
            actual_workflow_id = self.workflow_runner.start_workflow(
                rule_name=rule_name,
                context=context,
                workflow_id=workflow_id
            )

            # Publish workflow started event
            self.event_publisher.publish_event(
                event_type="workflow_started",
                data={
                    "workflow_id": workflow_id,
                    "rule_name": rule_name,
                    "service": self.workflow_runner.service_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            return workflow_id

        except Exception as e:
            # Update orchestration status
            if workflow_id in self.active_orchestrations:
                self.active_orchestrations[workflow_id]["status"] = WorkflowState.FAILED.value
                self.active_orchestrations[workflow_id]["error"] = str(e)

            raise

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive workflow status."""
        # Check active orchestrations first
        orchestration = self.active_orchestrations.get(workflow_id)
        if orchestration:
            # Get workflow runner status
            runner_status = self.workflow_runner.get_workflow_status(workflow_id)
            if runner_status:
                orchestration.update(runner_status)
            return orchestration

        # Check state manager for completed workflows
        state = self.workflow_runner.state_manager.get_state(workflow_id)
        if state:
            history = self.workflow_runner.state_manager.get_state_history(workflow_id)
            return {
                "workflow_id": workflow_id,
                "status": state.value,
                "state_history": history,
                "completed": True
            }

        return None

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        try:
            success = self.workflow_runner.state_manager.transition_state(
                workflow_id,
                WorkflowState.WAITING_FOR_HUMAN,
                "manual_pause"
            )

            if success:
                # Publish workflow paused event
                self.event_publisher.publish_event(
                    event_type="workflow_paused",
                    data={
                        "workflow_id": workflow_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            return success

        except Exception:
            return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        try:
            success = self.workflow_runner.state_manager.transition_state(
                workflow_id,
                WorkflowState.RUNNING,
                "manual_resume"
            )

            if success:
                # Publish workflow resumed event
                self.event_publisher.publish_event(
                    event_type="workflow_resumed",
                    data={
                        "workflow_id": workflow_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            return success

        except Exception:
            return False

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow execution."""
        try:
            success = self.workflow_runner.state_manager.transition_state(
                workflow_id,
                WorkflowState.CANCELLED,
                "manual_cancellation"
            )

            if success:
                # Remove from active orchestrations
                if workflow_id in self.active_orchestrations:
                    del self.active_orchestrations[workflow_id]

                # Publish workflow cancelled event
                self.event_publisher.publish_event(
                    event_type="workflow_cancelled",
                    data={
                        "workflow_id": workflow_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            return success

        except Exception:
            return False

    def list_workflows(self, status_filter: Optional[str] = None,
                      service_filter: Optional[str] = None,
                      limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List workflows with filtering."""
        workflows = []

        # Get active workflows
        for workflow_id, orchestration in self.active_orchestrations.items():
            status = orchestration.get("status")
            service = orchestration.get("service", self.workflow_runner.service_name)

            # Apply filters
            if status_filter and status != status_filter:
                continue
            if service_filter and service != service_filter:
                continue

            workflows.append({
                "workflow_id": workflow_id,
                "rule_name": orchestration.get("rule_name"),
                "status": status,
                "service": service,
                "start_time": orchestration.get("start_time"),
                "active": True
            })

        # Get completed workflows from state manager
        for workflow_id, state in self.workflow_runner.state_manager.current_states.items():
            if workflow_id in self.active_orchestrations:
                continue  # Already included

            if state in [WorkflowState.SUCCESS, WorkflowState.FAILED, WorkflowState.CANCELLED]:
                # Apply filters
                if status_filter and state.value != status_filter:
                    continue
                if service_filter:  # Would need to track service per workflow
                    continue

                history = self.workflow_runner.state_manager.get_state_history(workflow_id)
                start_time = history[0]["timestamp"] if history else None

                workflows.append({
                    "workflow_id": workflow_id,
                    "status": state.value,
                    "service": "unknown",  # Would need to be tracked
                    "start_time": start_time,
                    "active": False,
                    "completed": True
                })

        # Apply pagination
        return workflows[offset:offset + limit]

    def trigger_team_coordination(self) -> Dict[str, Any]:
        """Trigger manual team coordination workflow."""
        sync_id = str(uuid.uuid4())

        # Create sync context
        context = {
            "sync_id": sync_id,
            "trigger_type": "manual",
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # Start coordination workflow
            workflow_id = self.start_workflow(
                rule_name="sync_team_coordination",
                context=context
            )

            return {
                "sync_id": sync_id,
                "workflow_id": workflow_id,
                "teams_updated": 7,  # Based on workflow definition
                "status": "started"
            }

        except Exception as e:
            return {
                "sync_id": sync_id,
                "status": "failed",
                "error": str(e)
            }

    def list_rules(self) -> List[Dict[str, Any]]:
        """List all available workflow rules."""
        rules_info = []
        for rule_name in self.workflow_runner.rule_registry.list_rules():
            rule = self.workflow_runner.rule_registry.get_rule(rule_name)
            if rule:
                rules_info.append({
                    "name": rule.name,
                    "service": rule.service,
                    "version": rule.version,
                    "priority": rule.priority,
                    "description": rule.description,
                    "steps_count": len(rule.steps),
                    "trigger_type": rule.trigger.type.value
                })

        return rules_info

    def check_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all connected services."""
        services = [
            "dox-tmpl-pdf-upload",
            "dox-tmpl-pdf-recognizer",
            "dox-pact-manual-upload",
            "dox-rtns-manual-upload",
            "dox-core-store",
            "dox-core-auth",
            "dox-tmpl-service",
            "dox-validation-service"
        ]

        health_results = {}

        for service in services:
            try:
                health_status = self.service_connector.check_service_health(service)
                health_results[service] = {
                    "status": "healthy" if health_status else "unhealthy",
                    "last_check": datetime.utcnow().isoformat(),
                    "response_time_ms": health_status.get("response_time_ms", 0) if isinstance(health_status, dict) else 0
                }
            except Exception as e:
                health_results[service] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }

        return health_results

    def cleanup_completed_workflows(self, older_than_hours: int = 24) -> int:
        """Clean up old completed workflows."""
        return self.workflow_runner.state_manager.cleanup_completed_workflows(older_than_hours)

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestration engine metrics."""
        state_counts = {}
        for state in WorkflowState:
            count = len(self.workflow_runner.state_manager.get_workflows_by_state(state))
            state_counts[state.value] = count

        return {
            "active_orchestrations": len(self.active_orchestrations),
            "workflow_states": state_counts,
            "total_rules": len(self.workflow_runner.rule_registry.list_rules()),
            "services_connected": len(self.check_services_health()),
            "timestamp": datetime.utcnow().isoformat()
        }