"""
DOX Workflow Core Library

Embedded workflow library for all DOX services.
Provides workflow execution, state management, and integration patterns.
"""

from .runner import WorkflowRunner
from .state import WorkflowState
from .rules import WorkflowRule, RuleRegistry
from .validation import FileValidator
from .exceptions import WorkflowError, ValidationError, StateError

__version__ = "1.0.0"
__author__ = "DOX Infrastructure Team"

__all__ = [
    "WorkflowRunner",
    "WorkflowState",
    "WorkflowRule",
    "RuleRegistry",
    "FileValidator",
    "WorkflowError",
    "ValidationError",
    "StateError"
]