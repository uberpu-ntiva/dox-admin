"""
State Manager for Orchestrator.

Handles persistent state storage and retrieval for orchestrated workflows.
"""

import json
import redis
import psycopg2
from psycopg2.extras import Json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import contextmanager


class StateManager:
    """Persistent state management for orchestration engine."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize state manager with configuration."""
        self.config = config
        self.redis_client = None
        self.postgres_conn = None
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize Redis and PostgreSQL connections."""
        try:
            # Redis connection
            self.redis_client = redis.Redis(
                host=self.config.get("REDIS_HOST", "localhost"),
                port=self.config.get("REDIS_PORT", 6379),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connection established")

        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None

        try:
            # PostgreSQL connection
            self.postgres_conn = psycopg2.connect(
                host=self.config.get("POSTGRES_HOST", "localhost"),
                port=self.config.get("POSTGRES_PORT", 5432),
                database=self.config.get("POSTGRES_DB", "dox_workflows"),
                user=self.config.get("POSTGRES_USER", "dox_user"),
                password=self.config.get("POSTGRES_PASSWORD", "dox_password"),
                connect_timeout=5
            )
            # Test connection
            with self.postgres_conn.cursor() as cur:
                cur.execute("SELECT 1")
            print("✅ PostgreSQL connection established")

        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            self.postgres_conn = None

        # Initialize database tables
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database tables if they don't exist."""
        if not self.postgres_conn:
            return

        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS workflow_states (
            workflow_id VARCHAR(255) PRIMARY KEY,
            rule_name VARCHAR(255) NOT NULL,
            service VARCHAR(255) NOT NULL,
            current_state VARCHAR(50) NOT NULL,
            context JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE
        );

        CREATE TABLE IF NOT EXISTS workflow_step_results (
            id SERIAL PRIMARY KEY,
            workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
            step_name VARCHAR(255) NOT NULL,
            step_action VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            result JSONB,
            error_message TEXT,
            duration_ms INTEGER,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS workflow_events (
            id SERIAL PRIMARY KEY,
            workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
            event_type VARCHAR(255) NOT NULL,
            event_data JSONB,
            published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_workflow_states_status ON workflow_states(current_state);
        CREATE INDEX IF NOT EXISTS idx_workflow_states_updated ON workflow_states(updated_at);
        CREATE INDEX IF NOT EXISTS idx_step_results_workflow ON workflow_step_results(workflow_id);
        CREATE INDEX IF NOT EXISTS idx_events_workflow ON workflow_events(workflow_id);
        """

        try:
            with self.postgres_conn.cursor() as cur:
                cur.execute(create_tables_sql)
            self.postgres_conn.commit()
            print("✅ Database tables initialized")

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")

    def store_workflow_state(self, workflow_id: str, rule_name: str, service: str,
                           current_state: str, context: Dict[str, Any]) -> bool:
        """Store workflow state in persistent storage."""
        if not self.postgres_conn:
            return self._store_workflow_state_fallback(workflow_id, rule_name, service, current_state, context)

        try:
            with self.postgres_conn.cursor() as cur:
                # UPSERT workflow state
                cur.execute("""
                    INSERT INTO workflow_states (workflow_id, rule_name, service, current_state, context, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (workflow_id)
                    DO UPDATE SET
                        current_state = EXCLUDED.current_state,
                        context = EXCLUDED.context,
                        updated_at = NOW(),
                        completed_at = CASE
                            WHEN EXCLUDED.current_state IN ('success', 'failed', 'cancelled')
                            THEN NOW()
                            ELSE workflow_states.completed_at
                        END
                """, (workflow_id, rule_name, service, current_state, Json(context)))

            self.postgres_conn.commit()

            # Also cache in Redis for fast access
            if self.redis_client:
                cache_key = f"workflow_state:{workflow_id}"
                self.redis_client.setex(
                    cache_key,
                    timedelta(hours=24),
                    json.dumps({
                        "workflow_id": workflow_id,
                        "rule_name": rule_name,
                        "service": service,
                        "current_state": current_state,
                        "context": context,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )

            return True

        except Exception as e:
            print(f"Failed to store workflow state: {e}")
            return False

    def _store_workflow_state_fallback(self, workflow_id: str, rule_name: str, service: str,
                                     current_state: str, context: Dict[str, Any]) -> bool:
        """Fallback storage using only Redis."""
        if not self.redis_client:
            return False

        try:
            cache_key = f"workflow_state:{workflow_id}"
            state_data = {
                "workflow_id": workflow_id,
                "rule_name": rule_name,
                "service": service,
                "current_state": current_state,
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.redis_client.setex(cache_key, timedelta(days=7), json.dumps(state_data))
            return True

        except Exception as e:
            print(f"Failed to store workflow state in fallback: {e}")
            return False

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow state from storage."""
        # Try Redis cache first
        if self.redis_client:
            try:
                cache_key = f"workflow_state:{workflow_id}"
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis cache read failed: {e}")

        # Fallback to PostgreSQL
        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor() as cur:
                    cur.execute("""
                        SELECT workflow_id, rule_name, service, current_state, context,
                               created_at, updated_at, completed_at
                        FROM workflow_states
                        WHERE workflow_id = %s
                    """, (workflow_id,))
                    row = cur.fetchone()
                    if row:
                        return {
                            "workflow_id": row[0],
                            "rule_name": row[1],
                            "service": row[2],
                            "current_state": row[3],
                            "context": row[4],
                            "created_at": row[5].isoformat() if row[5] else None,
                            "updated_at": row[6].isoformat() if row[6] else None,
                            "completed_at": row[7].isoformat() if row[7] else None
                        }
            except Exception as e:
                print(f"PostgreSQL read failed: {e}")

        return None

    def store_step_result(self, workflow_id: str, step_name: str, step_action: str,
                         status: str, result: Dict[str, Any] = None,
                         error_message: str = None, duration_ms: int = 0) -> bool:
        """Store workflow step execution result."""
        if not self.postgres_conn:
            return False

        try:
            with self.postgres_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO workflow_step_results
                    (workflow_id, step_name, step_action, status, result, error_message, duration_ms)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (workflow_id, step_name, step_action, status,
                      Json(result) if result else None, error_message, duration_ms))

            self.postgres_conn.commit()
            return True

        except Exception as e:
            print(f"Failed to store step result: {e}")
            return False

    def store_workflow_event(self, workflow_id: str, event_type: str,
                           event_data: Dict[str, Any]) -> bool:
        """Store workflow event."""
        if not self.postgres_conn:
            return False

        try:
            with self.postgres_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO workflow_events (workflow_id, event_type, event_data)
                    VALUES (%s, %s, %s)
                """, (workflow_id, event_type, Json(event_data)))

            self.postgres_conn.commit()
            return True

        except Exception as e:
            print(f"Failed to store workflow event: {e}")
            return False

    def get_workflows_by_state(self, state: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflows in specific state."""
        if not self.postgres_conn:
            return []

        try:
            with self.postgres_conn.cursor() as cur:
                cur.execute("""
                    SELECT workflow_id, rule_name, service, current_state, context,
                           created_at, updated_at
                    FROM workflow_states
                    WHERE current_state = %s
                    ORDER BY updated_at DESC
                    LIMIT %s
                """, (state, limit))
                rows = cur.fetchall()

                return [{
                    "workflow_id": row[0],
                    "rule_name": row[1],
                    "service": row[2],
                    "current_state": row[3],
                    "context": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "updated_at": row[6].isoformat() if row[6] else None
                } for row in rows]

        except Exception as e:
            print(f"Failed to get workflows by state: {e}")
            return []

    def cleanup_old_workflows(self, days: int = 30) -> int:
        """Clean up old completed workflows."""
        if not self.postgres_conn:
            return 0

        try:
            with self.postgres_conn.cursor() as cur:
                # Delete old completed workflows
                cur.execute("""
                    DELETE FROM workflow_states
                    WHERE current_state IN ('success', 'failed', 'cancelled')
                    AND completed_at < NOW() - INTERVAL '%s days'
                    RETURNING workflow_id
                """, (days,))
                deleted_count = len(cur.fetchall())

                # Clean up orphaned step results and events
                cur.execute("""
                    DELETE FROM workflow_step_results
                    WHERE executed_at < NOW() - INTERVAL '%s days'
                """, (days,))
                cur.execute("""
                    DELETE FROM workflow_events
                    WHERE published_at < NOW() - INTERVAL '%s days'
                """, (days,))

            self.postgres_conn.commit()
            return deleted_count

        except Exception as e:
            print(f"Failed to cleanup old workflows: {e}")
            return 0

    def health_check(self) -> str:
        """Check health of state manager components."""
        redis_healthy = False
        postgres_healthy = False

        # Check Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                redis_healthy = True
            except:
                pass

        # Check PostgreSQL
        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor() as cur:
                    cur.execute("SELECT 1")
                postgres_healthy = True
            except:
                pass

        if redis_healthy and postgres_healthy:
            return "healthy"
        elif postgres_healthy:
            return "degraded"  # PostgreSQL working, Redis not
        else:
            return "unhealthy"

    def get_metrics(self) -> Dict[str, Any]:
        """Get state manager metrics."""
        metrics = {
            "redis_connected": self.redis_client is not None,
            "postgres_connected": self.postgres_conn is not None,
            "health": self.health_check()
        }

        if self.redis_client:
            try:
                info = self.redis_client.info()
                metrics["redis_memory"] = info.get("used_memory_human", "unknown")
                metrics["redis_keys"] = info.get("db0", {}).get("keys", 0)
            except:
                pass

        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor() as cur:
                    # Count workflows by state
                    cur.execute("""
                        SELECT current_state, COUNT(*)
                        FROM workflow_states
                        GROUP BY current_state
                    """)
                    state_counts = dict(cur.fetchall())
                    metrics["workflow_counts"] = state_counts

                    # Count recent activity
                    cur.execute("""
                        SELECT COUNT(*) FROM workflow_states
                        WHERE updated_at > NOW() - INTERVAL '1 hour'
                    """)
                    metrics["recent_workflows"] = cur.fetchone()[0]

            except Exception as e:
                metrics["postgres_error"] = str(e)

        return metrics