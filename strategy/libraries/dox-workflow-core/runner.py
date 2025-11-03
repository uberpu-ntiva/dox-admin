"""
Workflow execution engine.

Coordinates workflow execution, step processing, and state management.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import requests
from pathlib import Path

from .state import WorkflowState, StateManager
from .rules import WorkflowRule, WorkflowStep, ActionType, RuleRegistry
from .validation import FileValidator
from .exceptions import WorkflowError, ValidationError, IntegrationError, StateError


class WorkflowRunner:
    """Main workflow execution engine."""

    def __init__(self, service_name: str, memory_bank_path: str = None):
        """Initialize workflow runner."""
        self.service_name = service_name
        self.state_manager = StateManager()
        self.rule_registry = RuleRegistry()
        self.memory_bank_path = memory_bank_path or "strategy/memory-banks"
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    def load_rules_from_directory(self, workflow_directory: str) -> int:
        """Load workflow rules from directory."""
        return self.rule_registry.load_rules_from_directory(workflow_directory)

    def start_workflow(self, rule_name: str, context: Dict[str, Any],
                      workflow_id: Optional[str] = None) -> str:
        """Start a new workflow execution."""
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())

        # Get workflow rule
        rule = self.rule_registry.get_rule(rule_name)
        if not rule:
            raise WorkflowError(f"Workflow rule '{rule_name}' not found")

        # Validate conditions
        if not self._validate_conditions(rule, context):
            raise WorkflowError(f"Workflow conditions not met for '{rule_name}'")

        # Create workflow
        if not self.state_manager.create_workflow(workflow_id):
            raise WorkflowError(f"Workflow '{workflow_id}' already exists")

        # Store workflow metadata
        self.active_workflows[workflow_id] = {
            "rule_name": rule_name,
            "service": self.service_name,
            "start_time": datetime.utcnow().isoformat(),
            "context": context.copy(),
            "current_step": None,
            "step_results": {},
            "status": WorkflowState.RUNNING.value
        }

        # Transition to running state
        self.state_manager.transition_state(workflow_id, WorkflowState.RUNNING, "workflow_started")

        # Execute first step
        self._execute_next_step(workflow_id, rule)

        return workflow_id

    def _execute_next_step(self, workflow_id: str, rule: WorkflowRule,
                          current_step_name: Optional[str] = None) -> None:
        """Execute the next step in workflow."""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            raise WorkflowError(f"Workflow '{workflow_id}' not found")

        # Determine next step
        if current_step_name is None:
            # Start with first step
            next_step = rule.steps[0]
        else:
            # Find the step that follows current step
            current_step = next((s for s in rule.steps if s.name == current_step_name), None)
            if not current_step:
                raise WorkflowError(f"Step '{current_step_name}' not found in workflow")

            if current_step.on_success:
                next_step = next((s for s in rule.steps if s.name == current_step.on_success), None)
            else:
                # No next step, workflow complete
                self._complete_workflow(workflow_id, rule)
                return

            if not next_step:
                # Workflow complete
                self._complete_workflow(workflow_id, rule)
                return

        # Execute step
        try:
            workflow_info["current_step"] = next_step.name
            result = self._execute_step(workflow_id, next_step, workflow_info["context"])
            workflow_info["step_results"][next_step.name] = result

            # Continue to next step
            self._execute_next_step(workflow_id, rule, next_step.name)

        except Exception as e:
            # Handle step failure
            self._handle_step_failure(workflow_id, rule, next_step, e)

    def _execute_step(self, workflow_id: str, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_start_time = datetime.utcnow()

        try:
            if step.action == ActionType.API_CALL:
                result = self._execute_api_call(step, context)
            elif step.action == ActionType.DATA_TRANSFORM:
                result = self._execute_data_transform(step, context)
            elif step.action == ActionType.STORE_RESULT:
                result = self._execute_store_result(step, context)
            elif step.action == ActionType.PUBLISH_EVENT:
                result = self._execute_publish_event(step, context)
            elif step.action == ActionType.UPDATE_MEMORY:
                result = self._execute_update_memory(step, context)
            elif step.action == ActionType.CUSTOM_LOGIC:
                result = self._execute_custom_logic(step, context)
            elif step.action == ActionType.CONDITIONAL_BRANCH:
                result = self._execute_conditional_branch(step, context)
            elif step.action == ActionType.MANUAL_INTERVENTION:
                result = self._execute_manual_intervention(step, context)
            else:
                raise WorkflowError(f"Unsupported action type: {step.action}")

            # Log step execution
            step_duration = (datetime.utcnow() - step_start_time).total_seconds()
            self._log_step_execution(workflow_id, step, "success", step_duration, result)

            return result

        except Exception as e:
            # Log step failure
            step_duration = (datetime.utcnow() - step_start_time).total_seconds()
            self._log_step_execution(workflow_id, step, "failed", step_duration, {"error": str(e)})
            raise

    def _execute_api_call(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call step."""
        params = step.params.copy()

        # Substitute context variables
        service = self._substitute_variables(params.get("service", ""), context)
        method = params.get("method", "GET")
        endpoint = self._substitute_variables(params.get("endpoint", ""), context)
        body = params.get("body", {})

        # Handle body substitution
        if isinstance(body, str):
            body = self._substitute_variables(body, context)
        elif isinstance(body, dict):
            body = self._substitute_dict_variables(body, context)

        url = f"http://{service}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=body if method in ["POST", "PUT", "PATCH"] else None,
                params=body if method == "GET" else None,
                timeout=step.timeout_seconds
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise IntegrationError(
                f"API call failed: {e}",
                service_name=service,
                http_status=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )

    def _execute_data_transform(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transform step."""
        # For now, return transformed data based on params
        # In real implementation, this would use transformation logic
        return {
            "transformed": True,
            "transformation_type": step.params.get("type", "unknown"),
            "input_data": context
        }

    def _execute_store_result(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute store result step."""
        # Mock implementation - would store to database
        return {
            "stored": True,
            "table": step.params.get("table", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _execute_publish_event(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute publish event step."""
        # Mock implementation - would publish to message queue
        return {
            "event_published": True,
            "event_type": step.params.get("event", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _execute_update_memory(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory bank update step."""
        try:
            updates = step.params.get("updates", [])
            for update in updates:
                self._update_memory_bank(update, context)
            return {"memory_updated": True, "updates_count": len(updates)}
        except Exception as e:
            raise WorkflowError(f"Memory bank update failed: {e}")

    def _execute_custom_logic(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom logic step."""
        # Mock implementation - would call custom Python function
        return {
            "custom_logic_executed": True,
            "logic": step.params.get("logic", "unknown"),
            "result": "mock_result"
        }

    def _execute_conditional_branch(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conditional branch step."""
        condition = step.params.get("condition", "")
        true_branch = step.params.get("true_branch", "")
        false_branch = step.params.get("false_branch", "")

        # Mock condition evaluation
        condition_result = True  # Would actually evaluate condition

        return {
            "condition_evaluated": True,
            "condition": condition,
            "result": condition_result,
            "next_step": true_branch if condition_result else false_branch
        }

    def _execute_manual_intervention(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute manual intervention step."""
        # Set workflow state to waiting_for_human
        # Would create UI task for human operator
        return {
            "manual_intervention_required": True,
            "interface": step.params.get("interface", "dashboard"),
            "timeout_minutes": step.params.get("timeout_minutes", 30)
        }

    def _handle_step_failure(self, workflow_id: str, rule: WorkflowRule,
                           step: WorkflowStep, error: Exception) -> None:
        """Handle workflow step failure."""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            return

        # Determine error handling strategy
        error_handling = rule.error_handling.get("general_failure", "escalate")

        if error_handling == "retry":
            # Retry logic would go here
            self.state_manager.transition_state(workflow_id, WorkflowState.RETRY, "step_failed", {"error": str(error)})
        elif error_handling == "skip_step":
            # Continue to next step
            if step.on_failure:
                self._execute_next_step(workflow_id, rule, step.on_failure)
            else:
                self._complete_workflow(workflow_id, rule, failed=True)
        else:
            # Escalate
            self.state_manager.transition_state(workflow_id, WorkflowState.ESCALATED, "step_failed", {"error": str(error)})
            self._complete_workflow(workflow_id, rule, failed=True)

    def _complete_workflow(self, workflow_id: str, rule: WorkflowRule, failed: bool = False) -> None:
        """Complete workflow execution."""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            return

        workflow_info["end_time"] = datetime.utcnow().isoformat()
        workflow_info["status"] = WorkflowState.FAILED.value if failed else WorkflowState.SUCCESS.value

        # Update workflow state
        final_state = WorkflowState.FAILED if failed else WorkflowState.SUCCESS
        self.state_manager.transition_state(workflow_id, final_state, "workflow_completed")

        # Update memory banks with final status
        self._update_workflow_memory_banks(workflow_id, rule, workflow_info, failed)

        # Clean up active workflow
        del self.active_workflows[workflow_id]

    def _validate_conditions(self, rule: WorkflowRule, context: Dict[str, Any]) -> bool:
        """Validate workflow execution conditions."""
        # Mock implementation - would actually validate conditions
        return True

    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Substitute variables in text with context values."""
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            text = text.replace(placeholder, str(value))
        return text

    def _substitute_dict_variables(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute variables in dictionary with context values."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._substitute_variables(value, context)
            elif isinstance(value, dict):
                result[key] = self._substitute_dict_variables(value, context)
            else:
                result[key] = value
        return result

    def _update_memory_bank(self, update_spec: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Update memory bank file."""
        # Mock implementation - would update JSON files in memory-banks directory
        pass

    def _update_workflow_memory_banks(self, workflow_id: str, rule: WorkflowRule,
                                      workflow_info: Dict[str, Any], failed: bool) -> None:
        """Update memory banks with workflow completion status."""
        # Update workflow execution log
        log_entry = {
            "workflow_id": workflow_id,
            "workflow_name": rule.name,
            "service": self.service_name,
            "start_time": workflow_info["start_time"],
            "end_time": workflow_info["end_time"],
            "status": workflow_info["status"],
            "steps_executed": len(workflow_info["step_results"]),
            "failed": failed
        }

        # Mock update to WORKFLOW_EXECUTION_LOG.json
        print(f"Would update WORKFLOW_EXECUTION_LOG.json with: {log_entry}")

    def _log_step_execution(self, workflow_id: str, step: WorkflowStep,
                          status: str, duration: float, result: Dict[str, Any]) -> None:
        """Log step execution details."""
        log_entry = {
            "workflow_id": workflow_id,
            "step_name": step.name,
            "step_action": step.action.value,
            "status": status,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "result_summary": {k: v for k, v in result.items() if k != "error"}
        }
        print(f"Step execution: {log_entry}")

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status."""
        workflow_info = self.active_workflows.get(workflow_id)
        if workflow_info:
            return {
                "workflow_id": workflow_id,
                "status": workflow_info["status"],
                "current_step": workflow_info["current_step"],
                "start_time": workflow_info["start_time"],
                "steps_completed": len(workflow_info["step_results"])
            }

        # Check state manager for completed workflows
        state = self.state_manager.get_state(workflow_id)
        if state:
            return {
                "workflow_id": workflow_id,
                "status": state.value,
                "current_step": None,
                "start_time": None,
                "steps_completed": None
            }

        return None