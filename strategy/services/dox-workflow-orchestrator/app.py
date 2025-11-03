"""
Flask application for DOX Workflow Orchestrator.

Provides REST API endpoints for workflow orchestration, state management,
and team coordination.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add the workflow core library to Python path
workflow_core_path = Path(__file__).parent.parent.parent / "libraries"
sys.path.insert(0, str(workflow_core_path))

from dox_workflow_core import WorkflowRunner, WorkflowState, RuleRegistry
from .engine import OrchestrationEngine
from .state_manager import StateManager as OrchestratorStateManager
from .event_publisher import EventPublisher
from .service_connector import ServiceConnector


def create_app(config_name: str = "default"):
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config.update({
        "SERVICE_NAME": "dox-workflow-orchestrator",
        "SERVICE_PORT": int(os.environ.get("SERVICE_PORT", 5000)),
        "MEMORY_BANK_PATH": os.environ.get("MEMORY_BANK_PATH", "strategy/memory-banks"),
        "WORKFLOW_RULES_PATH": os.environ.get("WORKFLOW_RULES_PATH", "strategy/workflows"),
        "REDIS_HOST": os.environ.get("REDIS_HOST", "localhost"),
        "REDIS_PORT": int(os.environ.get("REDIS_PORT", 6379)),
        "POSTGRES_HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "POSTGRES_PORT": int(os.environ.get("POSTGRES_PORT", 5432)),
        "POSTGRES_DB": os.environ.get("POSTGRES_DB", "dox_workflows"),
        "POSTGRES_USER": os.environ.get("POSTGRES_USER", "dox_user"),
        "POSTGRES_PASSWORD": os.environ.get("POSTGRES_PASSWORD", "dox_password"),
        "DEBUG": os.environ.get("DEBUG", "false").lower() == "true"
    })

    # Enable CORS
    CORS(app)

    # Initialize components
    workflow_runner = WorkflowRunner(
        service_name=app.config["SERVICE_NAME"],
        memory_bank_path=app.config["MEMORY_BANK_PATH"]
    )

    state_manager = OrchestratorStateManager(app.config)
    event_publisher = EventPublisher(app.config)
    service_connector = ServiceConnector(app.config)
    orchestration_engine = OrchestrationEngine(
        workflow_runner=workflow_runner,
        state_manager=state_manager,
        event_publisher=event_publisher,
        service_connector=service_connector
    )

    # Load workflow rules
    rules_path = Path(__file__).parent.parent.parent / app.config["WORKFLOW_RULES_PATH"]
    loaded_rules = workflow_runner.load_rules_from_directory(str(rules_path))
    app.logger.info(f"Loaded {loaded_rules} workflow rules from {rules_path}")

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad request",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": app.config["SERVICE_NAME"],
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "workflow_engine": "healthy",
                "state_manager": state_manager.health_check(),
                "event_publisher": event_publisher.health_check(),
                "service_connector": service_connector.health_check()
            }
        })

    # API Routes
    @app.route('/api/v1/workflows', methods=['POST'])
    def start_workflow():
        """Start a new workflow execution."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "error": "Request body is required",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            rule_name = data.get("rule_name")
            context = data.get("context", {})
            workflow_id = data.get("workflow_id")

            if not rule_name:
                return jsonify({
                    "error": "rule_name is required",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            # Start workflow
            workflow_id = orchestration_engine.start_workflow(
                rule_name=rule_name,
                context=context,
                workflow_id=workflow_id
            )

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "rule_name": rule_name,
                "status": "started",
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to start workflow: {e}")
            return jsonify({
                "error": "Failed to start workflow",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/workflows/<workflow_id>', methods=['GET'])
    def get_workflow_status(workflow_id):
        """Get workflow execution status."""
        try:
            status = orchestration_engine.get_workflow_status(workflow_id)
            if not status:
                return jsonify({
                    "error": "Workflow not found",
                    "workflow_id": workflow_id,
                    "timestamp": datetime.utcnow().isoformat()
                }), 404

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                **status,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to get workflow status: {e}")
            return jsonify({
                "error": "Failed to get workflow status",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/workflows/<workflow_id>/pause', methods=['POST'])
    def pause_workflow(workflow_id):
        """Pause a running workflow."""
        try:
            success = orchestration_engine.pause_workflow(workflow_id)
            if not success:
                return jsonify({
                    "error": "Cannot pause workflow",
                    "workflow_id": workflow_id,
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "status": "paused",
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to pause workflow: {e}")
            return jsonify({
                "error": "Failed to pause workflow",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/workflows/<workflow_id>/resume', methods=['POST'])
    def resume_workflow(workflow_id):
        """Resume a paused workflow."""
        try:
            success = orchestration_engine.resume_workflow(workflow_id)
            if not success:
                return jsonify({
                    "error": "Cannot resume workflow",
                    "workflow_id": workflow_id,
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "status": "resumed",
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to resume workflow: {e}")
            return jsonify({
                "error": "Failed to resume workflow",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/workflows/<workflow_id>', methods=['DELETE'])
    def cancel_workflow(workflow_id):
        """Cancel a workflow execution."""
        try:
            success = orchestration_engine.cancel_workflow(workflow_id)
            if not success:
                return jsonify({
                    "error": "Cannot cancel workflow",
                    "workflow_id": workflow_id,
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "status": "cancelled",
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to cancel workflow: {e}")
            return jsonify({
                "error": "Failed to cancel workflow",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/workflows', methods=['GET'])
    def list_workflows():
        """List all workflows with optional filtering."""
        try:
            status_filter = request.args.get("status")
            service_filter = request.args.get("service")
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))

            workflows = orchestration_engine.list_workflows(
                status_filter=status_filter,
                service_filter=service_filter,
                limit=limit,
                offset=offset
            )

            return jsonify({
                "success": True,
                "workflows": workflows,
                "count": len(workflows),
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to list workflows: {e}")
            return jsonify({
                "error": "Failed to list workflows",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/coordination/sync', methods=['POST'])
    def trigger_team_coordination():
        """Trigger manual team coordination sync."""
        try:
            sync_result = orchestration_engine.trigger_team_coordination()
            return jsonify({
                "success": True,
                "sync_id": sync_result["sync_id"],
                "teams_updated": sync_result["teams_updated"],
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to trigger team coordination: {e}")
            return jsonify({
                "error": "Failed to trigger team coordination",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/rules', methods=['GET'])
    def list_workflow_rules():
        """List all available workflow rules."""
        try:
            rules = orchestration_engine.list_rules()
            return jsonify({
                "success": True,
                "rules": rules,
                "count": len(rules),
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to list workflow rules: {e}")
            return jsonify({
                "error": "Failed to list workflow rules",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/services/health', methods=['GET'])
    def check_services_health():
        """Check health of all connected services."""
        try:
            services_health = orchestration_engine.check_services_health()
            return jsonify({
                "success": True,
                "services": services_health,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            app.logger.error(f"Failed to check services health: {e}")
            return jsonify({
                "error": "Failed to check services health",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config.get("SERVICE_PORT", 5000)
    debug = app.config.get("DEBUG", False)

    print(f"Starting DOX Workflow Orchestrator on port {port}")
    print(f"Debug mode: {debug}")

    app.run(host="0.0.0.0", port=port, debug=debug)