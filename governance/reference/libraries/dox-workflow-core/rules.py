"""
Workflow rule definitions and registry.

Defines workflow rules structure and provides rule loading/management.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
from pathlib import Path

from .exceptions import RuleError, ConfigurationError


class TriggerType(Enum):
    """Workflow trigger types."""
    API_REQUEST = "api_request"
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    CASCADE = "cascade"


class ActionType(Enum):
    """Workflow step action types."""
    API_CALL = "api_call"
    DATA_TRANSFORM = "data_transform"
    STORE_RESULT = "store_result"
    PUBLISH_EVENT = "publish_event"
    UPDATE_MEMORY = "update_memory"
    NOTIFY_TEAM = "notify_team"
    VALIDATE_DATA = "validate_data"
    CUSTOM_LOGIC = "custom_logic"
    CONDITIONAL_BRANCH = "conditional_branch"
    MANUAL_INTERVENTION = "manual_intervention"


class ErrorHandlingType(Enum):
    """Error handling strategies."""
    RETRY = "retry"
    SKIP_STEP = "skip_step"
    ESCALATE = "escalate"
    ROLLBACK = "rollback"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class WorkflowStep:
    """Individual workflow step definition."""
    name: str
    action: ActionType
    params: Dict[str, Any] = field(default_factory=dict)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    error_message: Optional[str] = None
    timeout_seconds: int = 30
    retry_attempts: int = 0


@dataclass
class WorkflowCondition:
    """Workflow execution condition."""
    type: str
    check: str


@dataclass
class WorkflowTrigger:
    """Workflow trigger definition."""
    type: TriggerType
    source: str


@dataclass
class WorkflowRule:
    """Complete workflow rule definition."""
    name: str
    service: str
    version: str
    description: str
    priority: str
    trigger: WorkflowTrigger
    conditions: List[WorkflowCondition] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    error_handling: Dict[str, ErrorHandlingType] = field(default_factory=dict)
    memory_bank_updates: List[Dict[str, Any]] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate workflow rule structure."""
        if not self.name:
            raise ConfigurationError("Workflow name is required")

        if not self.service:
            raise ConfigurationError("Workflow service is required")

        if not self.trigger:
            raise ConfigurationError("Workflow trigger is required")

        if not self.steps:
            raise ConfigurationError("Workflow must have at least one step")

        # Validate step names are unique
        step_names = [step.name for step in self.steps]
        if len(step_names) != len(set(step_names)):
            raise ConfigurationError("Step names must be unique within workflow")

        # Validate on_success/on_failure references
        step_names_set = set(step_names)
        for step in self.steps:
            if step.on_success and step.on_success not in step_names_set:
                raise ConfigurationError(f"Step '{step.name}' references unknown success step: {step.on_success}")
            if step.on_failure and step.on_failure not in step_names_set:
                raise ConfigurationError(f"Step '{step.name}' references unknown failure step: {step.on_failure}")


class RuleRegistry:
    """Registry for managing workflow rules."""

    def __init__(self):
        self.rules: Dict[str, WorkflowRule] = {}
        self.rules_by_service: Dict[str, List[str]] = {}

    def register_rule(self, rule: WorkflowRule) -> None:
        """Register a workflow rule."""
        rule.validate()

        if rule.name in self.rules:
            raise RuleError(f"Rule '{rule.name}' already registered")

        self.rules[rule.name] = rule

        if rule.service not in self.rules_by_service:
            self.rules_by_service[rule.service] = []
        self.rules_by_service[rule.service].append(rule.name)

    def get_rule(self, name: str) -> Optional[WorkflowRule]:
        """Get workflow rule by name."""
        return self.rules.get(name)

    def get_rules_for_service(self, service: str) -> List[WorkflowRule]:
        """Get all rules for a specific service."""
        rule_names = self.rules_by_service.get(service, [])
        return [self.rules[name] for name in rule_names]

    def list_rules(self) -> List[str]:
        """List all registered rule names."""
        return list(self.rules.keys())

    def load_rules_from_yaml(self, yaml_path: str) -> int:
        """Load workflow rules from YAML file."""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)

            rule = self._parse_yaml_rule(yaml_data)
            self.register_rule(rule)
            return 1

        except FileNotFoundError:
            raise ConfigurationError(f"YAML file not found: {yaml_path}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {yaml_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading rule from {yaml_path}: {e}")

    def load_rules_from_directory(self, directory: str) -> int:
        """Load all workflow rules from YAML files in directory."""
        loaded_count = 0
        yaml_files = Path(directory).glob("*.yaml")

        for yaml_file in yaml_files:
            try:
                loaded_count += self.load_rules_from_yaml(str(yaml_file))
            except Exception as e:
                print(f"Warning: Failed to load rule from {yaml_file}: {e}")

        return loaded_count

    def _parse_yaml_rule(self, yaml_data: Dict[str, Any]) -> WorkflowRule:
        """Parse YAML data into WorkflowRule object."""
        try:
            # Parse trigger
            trigger_data = yaml_data["trigger"]
            trigger = WorkflowTrigger(
                type=TriggerType(trigger_data["type"]),
                source=trigger_data["source"]
            )

            # Parse conditions
            conditions = []
            for cond_data in yaml_data.get("conditions", []):
                conditions.append(WorkflowCondition(
                    type=cond_data["type"],
                    check=cond_data["check"]
                ))

            # Parse steps
            steps = []
            for step_data in yaml_data["steps"]:
                step = WorkflowStep(
                    name=step_data["name"],
                    action=ActionType(step_data["action"]),
                    params=step_data.get("params", {}),
                    on_success=step_data.get("on_success"),
                    on_failure=step_data.get("on_failure"),
                    error_message=step_data.get("error_message"),
                    timeout_seconds=step_data.get("timeout_seconds", 30),
                    retry_attempts=step_data.get("retry_attempts", 0)
                )
                steps.append(step)

            # Parse error handling
            error_handling = {}
            for error_type, strategy in yaml_data.get("error_handling", {}).items():
                error_handling[error_type] = ErrorHandlingType(strategy)

            return WorkflowRule(
                name=yaml_data["name"],
                service=yaml_data["service"],
                version=yaml_data["version"],
                description=yaml_data["description"],
                priority=yaml_data["priority"],
                trigger=trigger,
                conditions=conditions,
                steps=steps,
                error_handling=error_handling,
                memory_bank_updates=yaml_data.get("memory_bank_updates", []),
                configuration=yaml_data.get("configuration", {})
            )

        except KeyError as e:
            raise ConfigurationError(f"Missing required field in workflow rule: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error parsing workflow rule: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "rules_count": len(self.rules),
            "rules": {name: {
                "name": rule.name,
                "service": rule.service,
                "version": rule.version,
                "priority": rule.priority,
                "steps_count": len(rule.steps)
            } for name, rule in self.rules.items()},
            "services": list(self.rules_by_service.keys())
        }