"""
DOX Workflow Orchestrator Service

Centralized orchestration service for complex multi-service workflows.
Coordinates cross-service workflows, manages state, and handles team synchronization.
"""

from .app import create_app
from .engine import OrchestrationEngine
from .state_manager import StateManager
from .event_publisher import EventPublisher
from .service_connector import ServiceConnector

__version__ = "1.0.0"
__author__ = "DOX Automation Team"

__all__ = [
    "create_app",
    "OrchestrationEngine",
    "StateManager",
    "EventPublisher",
    "ServiceConnector"
]