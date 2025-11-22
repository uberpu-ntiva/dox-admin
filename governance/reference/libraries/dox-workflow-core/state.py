"""
Workflow state management.

Defines workflow states and provides state transition logic.
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import json


class WorkflowState(Enum):
    """Workflow execution states."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    WAITING_FOR_HUMAN = "waiting_for_human"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class StateManager:
    """Manages workflow state transitions and persistence."""

    def __init__(self):
        self.state_history: Dict[str, list] = {}
        self.current_states: Dict[str, WorkflowState] = {}

    def create_workflow(self, workflow_id: str, initial_state: WorkflowState = WorkflowState.PENDING) -> bool:
        """Create a new workflow instance."""
        if workflow_id in self.current_states:
            return False

        self.current_states[workflow_id] = initial_state
        self.state_history[workflow_id] = [{
            "state": initial_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "workflow_created"
        }]
        return True

    def transition_state(self, workflow_id: str, new_state: WorkflowState,
                        reason: str = "state_change", details: Optional[Dict[str, Any]] = None) -> bool:
        """Transition workflow to a new state."""
        if workflow_id not in self.current_states:
            raise StateError(f"Workflow {workflow_id} not found")

        current_state = self.current_states[workflow_id]

        # Validate state transition
        if not self._is_valid_transition(current_state, new_state):
            raise StateError(
                f"Invalid state transition from {current_state.value} to {new_state.value}",
                workflow_id=workflow_id
            )

        # Update state
        self.current_states[workflow_id] = new_state

        # Record state change
        state_entry = {
            "state": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "details": details or {}
        }
        self.state_history[workflow_id].append(state_entry)

        return True

    def _is_valid_transition(self, from_state: WorkflowState, to_state: WorkflowState) -> bool:
        """Check if state transition is valid."""
        valid_transitions = {
            WorkflowState.PENDING: [WorkflowState.RUNNING, WorkflowState.CANCELLED],
            WorkflowState.RUNNING: [WorkflowState.SUCCESS, WorkflowState.FAILED,
                                   WorkflowState.RETRY, WorkflowState.WAITING_FOR_HUMAN,
                                   WorkflowState.ESCALATED, WorkflowState.CANCELLED],
            WorkflowState.RETRY: [WorkflowState.RUNNING, WorkflowState.FAILED,
                                 WorkflowState.ESCALATED, WorkflowState.CANCELLED],
            WorkflowState.WAITING_FOR_HUMAN: [WorkflowState.RUNNING, WorkflowState.SUCCESS,
                                             WorkflowState.FAILED, WorkflowState.CANCELLED],
            WorkflowState.ESCALATED: [WorkflowState.RUNNING, WorkflowState.FAILED,
                                     WorkflowState.CANCELLED],
            WorkflowState.SUCCESS: [],  # Terminal state
            WorkflowState.FAILED: [],   # Terminal state
            WorkflowState.CANCELLED: []  # Terminal state
        }

        return to_state in valid_transitions.get(from_state, [])

    def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get current state of workflow."""
        return self.current_states.get(workflow_id)

    def get_state_history(self, workflow_id: str) -> list:
        """Get full state history for workflow."""
        return self.state_history.get(workflow_id, [])

    def get_workflows_by_state(self, state: WorkflowState) -> list:
        """Get all workflows in a specific state."""
        return [wf_id for wf_id, wf_state in self.current_states.items() if wf_state == state]

    def cleanup_completed_workflows(self, older_than_hours: int = 24) -> int:
        """Remove completed workflows older than specified hours."""
        cutoff_time = datetime.utcnow().timestamp() - (older_than_hours * 3600)
        removed_count = 0

        for workflow_id in list(self.current_states.keys()):
            state = self.current_states[workflow_id]
            if state in [WorkflowState.SUCCESS, WorkflowState.FAILED, WorkflowState.CANCELLED]:
                history = self.state_history[workflow_id]
                last_update = datetime.fromisoformat(history[-1]["timestamp"]).timestamp()

                if last_update < cutoff_time:
                    del self.current_states[workflow_id]
                    del self.state_history[workflow_id]
                    removed_count += 1

        return removed_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert state manager to dictionary for persistence."""
        return {
            "current_states": {k: v.value for k, v in self.current_states.items()},
            "state_history": self.state_history,
            "workflow_count": len(self.current_states)
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore state manager from dictionary."""
        self.current_states = {
            k: WorkflowState(v) for k, v in data.get("current_states", {}).items()
        }
        self.state_history = data.get("state_history", {})


class StateError(Exception):
    """Exception raised for state management errors."""
    pass