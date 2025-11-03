"""
Workflow exception classes.

Custom exceptions for workflow execution, validation, and state management.
"""

from typing import Optional, Dict, Any


class WorkflowError(Exception):
    """Base exception for workflow-related errors."""

    def __init__(self, message: str, workflow_id: Optional[str] = None,
                 step_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.workflow_id = workflow_id
        self.step_name = step_name
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.message,
            "workflow_id": self.workflow_id,
            "step_name": self.step_name,
            "details": self.details,
            "exception_type": self.__class__.__name__
        }


class ValidationError(WorkflowError):
    """Exception raised during file validation steps."""

    def __init__(self, message: str, validation_type: str = "unknown",
                 status_code: int = 400, **kwargs):
        self.validation_type = validation_type
        self.status_code = status_code
        super().__init__(message, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "validation_type": self.validation_type,
            "status_code": self.status_code
        })
        return base


class StateError(WorkflowError):
    """Exception raised during workflow state management."""
    pass


class RuleError(WorkflowError):
    """Exception raised when workflow rule validation fails."""
    pass


class IntegrationError(WorkflowError):
    """Exception raised during external service integration."""

    def __init__(self, message: str, service_name: Optional[str] = None,
                 http_status: Optional[int] = None, **kwargs):
        self.service_name = service_name
        self.http_status = http_status
        super().__init__(message, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "service_name": self.service_name,
            "http_status": self.http_status
        })
        return base


class ConfigurationError(WorkflowError):
    """Exception raised when workflow configuration is invalid."""
    pass


class MemoryBankError(WorkflowError):
    """Exception raised during memory bank operations."""
    pass