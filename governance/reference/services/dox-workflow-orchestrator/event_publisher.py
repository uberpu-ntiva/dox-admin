"""
Event Publisher for Workflow Orchestrator.

Publishes workflow events to Redis pub/sub and other notification systems.
"""

import json
import redis
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class EventPublisher:
    """Publishes workflow events to various channels."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize event publisher."""
        self.config = config
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection for pub/sub."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.get("REDIS_HOST", "localhost"),
                port=self.config.get("REDIS_PORT", 6379),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info("✅ Event publisher Redis connection established")

        except Exception as e:
            self.logger.error(f"❌ Event publisher Redis connection failed: {e}")
            self.redis_client = None

    def publish_event(self, event_type: str, event_data: Dict[str, Any],
                     channels: Optional[list] = None) -> bool:
        """Publish event to specified channels."""
        event = {
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.utcnow().isoformat(),
            "publisher": "dox-workflow-orchestrator"
        }

        # Default channels if not specified
        if channels is None:
            channels = self._get_default_channels(event_type)

        success = True

        # Publish to Redis pub/sub
        if self.redis_client:
            for channel in channels:
                try:
                    message = json.dumps(event)
                    self.redis_client.publish(channel, message)
                    self.logger.debug(f"Published event {event_type} to channel {channel}")

                except Exception as e:
                    self.logger.error(f"Failed to publish to Redis channel {channel}: {e}")
                    success = False
        else:
            self.logger.warning("Redis not available, event not published")
            success = False

        # Store event in memory bank if applicable
        if event_type in ["workflow_started", "workflow_completed", "workflow_failed"]:
            self._store_in_memory_bank(event)

        return success

    def _get_default_channels(self, event_type: str) -> list:
        """Get default channels for event type."""
        channel_mapping = {
            "workflow_started": ["workflows", "workflows:started"],
            "workflow_completed": ["workflows", "workflows:completed"],
            "workflow_failed": ["workflows", "workflows:failed"],
            "workflow_paused": ["workflows", "workflows:paused"],
            "workflow_resumed": ["workflows", "workflows:resumed"],
            "workflow_cancelled": ["workflows", "workflows:cancelled"],
            "step_completed": ["workflows:steps"],
            "step_failed": ["workflows:steps"],
            "team_coordination_started": ["coordination", "teams"],
            "team_coordination_completed": ["coordination", "teams"],
            "memory_bank_updated": ["memory_banks"],
            "blocking_issue_created": ["alerts", "teams"],
            "service_health_changed": ["services", "alerts"]
        }

        return channel_mapping.get(event_type, ["workflows"])

    def _store_in_memory_bank(self, event: Dict[str, Any]):
        """Store significant events in memory bank."""
        try:
            from pathlib import Path
            memory_bank_path = Path(self.config.get("MEMORY_BANK_PATH", "strategy/memory-banks"))
            events_log_path = memory_bank_path / "WORKFLOW_EVENTS.json"

            # Load existing events log
            events_log = {"events": []}
            if events_log_path.exists():
                with open(events_log_path, 'r') as f:
                    try:
                        events_log = json.load(f)
                    except json.JSONDecodeError:
                        events_log = {"events": []}

            # Add new event
            events_log["events"].append({
                "event_id": f"evt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                "event_type": event["event_type"],
                "event_data": event["event_data"],
                "timestamp": event["timestamp"],
                "publisher": event["publisher"]
            })

            # Keep only last 1000 events
            if len(events_log["events"]) > 1000:
                events_log["events"] = events_log["events"][-1000:]

            # Save updated log
            with open(events_log_path, 'w') as f:
                json.dump(events_log, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to store event in memory bank: {e}")

    def publish_workflow_lifecycle_event(self, workflow_id: str, status: str,
                                        context: Dict[str, Any] = None) -> bool:
        """Publish workflow lifecycle event."""
        event_data = {
            "workflow_id": workflow_id,
            "status": status,
            "context": context or {}
        }

        return self.publish_event(f"workflow_{status}", event_data)

    def publish_step_event(self, workflow_id: str, step_name: str,
                          step_status: str, result: Dict[str, Any] = None,
                          error_message: str = None) -> bool:
        """Publish workflow step execution event."""
        event_data = {
            "workflow_id": workflow_id,
            "step_name": step_name,
            "step_status": step_status,
            "result": result,
            "error_message": error_message
        }

        event_type = f"step_{step_status}"
        return self.publish_event(event_type, event_data)

    def publish_team_coordination_event(self, coordination_id: str,
                                       teams_updated: list, status: str) -> bool:
        """Publish team coordination event."""
        event_data = {
            "coordination_id": coordination_id,
            "teams_updated": teams_updated,
            "status": status
        }

        event_type = f"team_coordination_{status}"
        return self.publish_event(event_type, event_data)

    def publish_service_health_event(self, service_name: str, health_status: str,
                                   response_time_ms: int = 0) -> bool:
        """Publish service health change event."""
        event_data = {
            "service_name": service_name,
            "health_status": health_status,
            "response_time_ms": response_time_ms
        }

        return self.publish_event("service_health_changed", event_data)

    def publish_blocking_issue_event(self, issue_id: str, service_name: str,
                                   severity: str, description: str) -> bool:
        """Publish blocking issue event."""
        event_data = {
            "issue_id": issue_id,
            "service_name": service_name,
            "severity": severity,
            "description": description
        }

        return self.publish_event("blocking_issue_created", event_data)

    def publish_memory_bank_update_event(self, file_name: str, update_type: str,
                                        update_data: Dict[str, Any]) -> bool:
        """Publish memory bank update event."""
        event_data = {
            "file_name": file_name,
            "update_type": update_type,
            "update_data": update_data
        }

        return self.publish_event("memory_bank_updated", event_data)

    def get_recent_events(self, event_type: Optional[str] = None,
                         limit: int = 50) -> list:
        """Get recent events from memory bank."""
        try:
            from pathlib import Path
            memory_bank_path = Path(self.config.get("MEMORY_BANK_PATH", "strategy/memory-banks"))
            events_log_path = memory_bank_path / "WORKFLOW_EVENTS.json"

            if not events_log_path.exists():
                return []

            with open(events_log_path, 'r') as f:
                events_log = json.load(f)

            events = events_log.get("events", [])

            # Filter by event type if specified
            if event_type:
                events = [e for e in events if e["event_type"] == event_type]

            # Sort by timestamp (newest first) and limit
            events.sort(key=lambda x: x["timestamp"], reverse=True)
            return events[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get recent events: {e}")
            return []

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event publishing statistics."""
        try:
            from pathlib import Path
            memory_bank_path = Path(self.config.get("MEMORY_BANK_PATH", "strategy/memory-banks"))
            events_log_path = memory_bank_path / "WORKFLOW_EVENTS.json"

            if not events_log_path.exists():
                return {"total_events": 0, "event_types": {}}

            with open(events_log_path, 'r') as f:
                events_log = json.load(f)

            events = events_log.get("events", [])
            event_types = {}

            for event in events:
                event_type = event["event_type"]
                event_types[event_type] = event_types.get(event_type, 0) + 1

            return {
                "total_events": len(events),
                "event_types": event_types,
                "latest_event": events[-1]["timestamp"] if events else None
            }

        except Exception as e:
            self.logger.error(f"Failed to get event statistics: {e}")
            return {"error": str(e)}

    def health_check(self) -> str:
        """Check health of event publisher."""
        if self.redis_client:
            try:
                # Test Redis connection
                self.redis_client.ping()
                return "healthy"
            except:
                return "unhealthy"
        else:
            return "degraded"  # Can store events locally but not publish