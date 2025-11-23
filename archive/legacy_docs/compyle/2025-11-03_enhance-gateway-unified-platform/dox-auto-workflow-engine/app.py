"""
DOX Auto Workflow Engine
Visual automation builder with workflow DSL interpreter
"""

import os
import logging
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import threading
import queue
from typing import Dict, List, Optional, Any
import anthropic
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configuration
app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
    'REDIS_HOST': os.environ.get('REDIS_HOST', 'localhost'),
    'REDIS_PORT': int(os.environ.get('REDIS_PORT', 6379)),
    'DATABASE_URL': os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/dox_auto_workflow'),
    'API_VERSION': 'v1'
})

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://dox-platform.com"]
    }
})

# Redis client
redis_client = redis.Redis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    decode_responses=True
)

# Workflow execution queue
workflow_queue = queue.Queue(maxsize=100)

# Database connection
def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(app.config['DATABASE_URL'])

# HTML Template for Workflow Builder UI
WORKFLOW_BUILDER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOX Workflow Builder</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .workflow-canvas { border: 2px dashed #ddd; min-height: 400px; padding: 20px; margin: 20px 0; border-radius: 4px; background: #fafafa; }
        .component-palette { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
        .component { padding: 10px; border: 1px solid #ddd; border-radius: 4px; text-align: center; cursor: move; background: white; }
        .component.trigger { border-left: 4px solid #007bff; }
        .component.condition { border-left: 4px solid #ffc107; }
        .component.action { border-left: 4px solid #28a745; }
        .workflow-node { padding: 15px; margin: 10px; border: 2px solid #ddd; border-radius: 6px; background: white; cursor: pointer; }
        .workflow-node.selected { border-color: #007bff; box-shadow: 0 0 0 2px rgba(0,123,255,0.5); }
        .workflow-connector { width: 2px; height: 30px; background: #007bff; margin: 0 auto; }
        .properties-panel { border: 1px solid #ddd; padding: 20px; margin-top: 20px; border-radius: 4px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .status-bar { display: flex; justify-content: space-between; padding: 10px; background: #f8f9fa; border-radius: 4px; margin-top: 20px; }
        .tab-nav { display: flex; border-bottom: 1px solid #ddd; margin-bottom: 20px; }
        .tab { padding: 10px 20px; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #007bff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DOX Workflow Builder</h1>
            <div>
                <button class="btn btn-secondary" onclick="clearCanvas()">Clear</button>
                <button class="btn btn-primary" onclick="saveWorkflow()">Save Workflow</button>
                <button class="btn btn-success" onclick="executeWorkflow()">Execute</button>
            </div>
        </div>

        <div class="tab-nav">
            <div class="tab active" onclick="showTab('builder')">Builder</div>
            <div class="tab" onclick="showTab('workflows')">My Workflows</div>
            <div class="tab" onclick="showTab('executions')">Executions</div>
        </div>

        <div class="tab-content active" id="builder-tab">
            <h3>Components</h3>
            <div class="component-palette">
                <div class="component trigger" draggable="true" data-type="trigger">
                    <strong>🎯 Trigger</strong><br>
                    <small>Event Source</small>
                </div>
                <div class="component condition" draggable="true" data-type="condition">
                    <strong>🔍 Condition</strong><br>
                    <small>Check Condition</small>
                </div>
                <div class="component action" draggable="true" data-type="action">
                    <strong>⚡ Action</strong><br>
                    <small>Execute Action</small>
                </div>
            </div>

            <h3>Workflow Canvas</h3>
            <div class="workflow-canvas" id="workflow-canvas" ondrop="drop(event)" ondragover="allowDrop(event)">
                <p style="text-align: center; color: #999;">Drag components here to build your workflow</p>
            </div>

            <div class="properties-panel" id="properties-panel" style="display: none;">
                <h4>Component Properties</h4>
                <div id="properties-content"></div>
            </div>

            <div class="status-bar">
                <div>Status: <span id="status">Ready</span></div>
                <div>Nodes: <span id="node-count">0</span></div>
            </div>
        </div>

        <div class="tab-content" id="workflows-tab">
            <h3>Saved Workflows</h3>
            <div id="workflows-list">
                <p>Loading workflows...</p>
            </div>
        </div>

        <div class="tab-content" id="executions-tab">
            <h3>Execution History</h3>
            <div id="executions-list">
                <p>Loading executions...</p>
            </div>
        </div>
    </div>

    <script>
        let workflowNodes = [];
        let selectedNode = null;
        let nodeIdCounter = 1;

        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // Show selected tab
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');

            // Load content for specific tabs
            if (tabName === 'workflows') {
                loadWorkflows();
            } else if (tabName === 'executions') {
                loadExecutions();
            }
        }

        function allowDrop(ev) {
            ev.preventDefault();
        }

        function drop(ev) {
            ev.preventDefault();
            const componentType = ev.dataTransfer.getData('text');

            if (componentType) {
                addWorkflowNode(componentType, ev.offsetX, ev.offsetY);
            }
        }

        function addWorkflowNode(type, x, y) {
            const canvas = document.getElementById('workflow-canvas');
            const nodeId = `node_${nodeIdCounter++}`;

            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'workflow-node';
            nodeDiv.id = nodeId;
            nodeDiv.style.position = 'absolute';
            nodeDiv.style.left = (x - 75) + 'px';
            nodeDiv.style.top = (y - 25) + 'px';
            nodeDiv.onclick = () => selectNode(nodeId);

            const icons = {
                'trigger': '🎯',
                'condition': '🔍',
                'action': '⚡'
            };

            nodeDiv.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 24px;">${icons[type]}</div>
                    <div><strong>${type.toUpperCase()}</strong></div>
                    <div><small>${getNodeDescription(type)}</small></div>
                </div>
            `;

            canvas.appendChild(nodeDiv);

            workflowNodes.push({
                id: nodeId,
                type: type,
                x: x,
                y: y,
                properties: getDefaultProperties(type)
            });

            updateNodeCount();
        }

        function selectNode(nodeId) {
            // Remove previous selection
            document.querySelectorAll('.workflow-node').forEach(node => {
                node.classList.remove('selected');
            });

            // Select new node
            const node = document.getElementById(nodeId);
            node.classList.add('selected');
            selectedNode = workflowNodes.find(n => n.id === nodeId);

            showProperties(selectedNode);
        }

        function showProperties(node) {
            const panel = document.getElementById('properties-panel');
            const content = document.getElementById('properties-content');

            panel.style.display = 'block';
            content.innerHTML = generatePropertiesForm(node);

            // Add event listeners to form fields
            content.querySelectorAll('input, select, textarea').forEach(input => {
                input.addEventListener('change', (e) => {
                    node.properties[e.target.name] = e.target.value;
                });
            });
        }

        function generatePropertiesForm(node) {
            if (node.type === 'trigger') {
                return `
                    <div class="form-group">
                        <label>Trigger Type</label>
                        <select name="triggerType">
                            <option value="webhook">Webhook Event</option>
                            <option value="schedule">Scheduled</option>
                            <option value="manual">Manual Trigger</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Event Source</label>
                        <input type="text" name="eventSource" value="${node.properties.eventSource || ''}" placeholder="e.g., SIGNING_COMPLETED">
                    </div>
                    <div class="form-group">
                        <label>Conditions</label>
                        <textarea name="conditions" rows="3" placeholder="JSON conditions">${node.properties.conditions || ''}</textarea>
                    </div>
                `;
            } else if (node.type === 'condition') {
                return `
                    <div class="form-group">
                        <label>Condition Type</label>
                        <select name="conditionType">
                            <option value="field">Field Value</option>
                            <option value="status">Status Check</option>
                            <option value="time">Time Based</option>
                            <option value="custom">Custom Logic</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Field Name</label>
                        <input type="text" name="fieldName" value="${node.properties.fieldName || ''}" placeholder="e.g., contract_status">
                    </div>
                    <div class="form-group">
                        <label>Operator</label>
                        <select name="operator">
                            <option value="equals">Equals</option>
                            <option value="not_equals">Not Equals</option>
                            <option value="greater_than">Greater Than</option>
                            <option value="less_than">Less Than</option>
                            <option value="contains">Contains</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Value</label>
                        <input type="text" name="value" value="${node.properties.value || ''}" placeholder="Condition value">
                    </div>
                `;
            } else if (node.type === 'action') {
                return `
                    <div class="form-group">
                        <label>Action Type</label>
                        <select name="actionType" onchange="updateActionFields(this)">
                            <option value="api_call">API Call</option>
                            <option value="notification">Send Notification</option>
                            <option value="data_update">Update Data</option>
                            <option value="workflow">Trigger Workflow</option>
                            <option value="custom">Custom Action</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Target Service</label>
                        <select name="targetService">
                            <option value="dox-actv-service">Activation Service</option>
                            <option value="dox-esig-service">E-Signature Service</option>
                            <option value="dox-batch-assembly">Batch Assembly</option>
                            <option value="dox-core-store">Core Store</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Endpoint</label>
                        <input type="text" name="endpoint" value="${node.properties.endpoint || ''}" placeholder="API endpoint">
                    </div>
                    <div class="form-group">
                        <label>Method</label>
                        <select name="method">
                            <option value="POST">POST</option>
                            <option value="GET">GET</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Payload</label>
                        <textarea name="payload" rows="3" placeholder="JSON payload">${node.properties.payload || ''}</textarea>
                    </div>
                `;
            }

            return '';
        }

        function updateActionFields(select) {
            // This would update action-specific fields based on selection
            // Implementation would go here
        }

        function getNodeDescription(type) {
            const descriptions = {
                'trigger': 'When this happens...',
                'condition': 'If this is true...',
                'action': 'Then do this...'
            };
            return descriptions[type] || '';
        }

        function getDefaultProperties(type) {
            const defaults = {
                'trigger': {
                    triggerType: 'webhook',
                    eventSource: '',
                    conditions: ''
                },
                'condition': {
                    conditionType: 'field',
                    fieldName: '',
                    operator: 'equals',
                    value: ''
                },
                'action': {
                    actionType: 'api_call',
                    targetService: '',
                    endpoint: '',
                    method: 'POST',
                    payload: ''
                }
            };
            return defaults[type] || {};
        }

        function clearCanvas() {
            const canvas = document.getElementById('workflow-canvas');
            canvas.innerHTML = '<p style="text-align: center; color: #999;">Drag components here to build your workflow</p>';
            workflowNodes = [];
            selectedNode = null;
            updateNodeCount();
            document.getElementById('properties-panel').style.display = 'none';
        }

        function updateNodeCount() {
            document.getElementById('node-count').textContent = workflowNodes.length;
        }

        async function saveWorkflow() {
            const workflowData = {
                name: prompt('Enter workflow name:'),
                description: prompt('Enter workflow description:'),
                nodes: workflowNodes,
                created_at: new Date().toISOString()
            };

            if (!workflowData.name) return;

            try {
                const response = await fetch('/api/workflows', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(workflowData)
                });

                if (response.ok) {
                    alert('Workflow saved successfully!');
                } else {
                    alert('Failed to save workflow');
                }
            } catch (error) {
                alert('Error saving workflow: ' + error.message);
            }
        }

        async function executeWorkflow() {
            if (workflowNodes.length === 0) {
                alert('Please add components to the workflow first');
                return;
            }

            const executionData = {
                workflow_id: `exec_${Date.now()}`,
                nodes: workflowNodes,
                triggered_by: 'current_user'
            };

            document.getElementById('status').textContent = 'Executing...';

            try {
                const response = await fetch('/api/workflows/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(executionData)
                });

                const result = await response.json();

                if (response.ok) {
                    document.getElementById('status').textContent = 'Completed';
                    alert('Workflow executed successfully!');
                } else {
                    document.getElementById('status').textContent = 'Failed';
                    alert('Workflow execution failed');
                }
            } catch (error) {
                document.getElementById('status').textContent = 'Error';
                alert('Error executing workflow: ' + error.message);
            }
        }

        async function loadWorkflows() {
            try {
                const response = await fetch('/api/workflows');
                const workflows = await response.json();

                const listDiv = document.getElementById('workflows-list');
                listDiv.innerHTML = workflows.map(workflow => `
                    <div style="padding: 15px; border: 1px solid #ddd; margin: 10px 0; border-radius: 4px;">
                        <h4>${workflow.name}</h4>
                        <p>${workflow.description}</p>
                        <small>Created: ${new Date(workflow.created_at).toLocaleString()}</small>
                        <button class="btn btn-secondary" onclick="editWorkflow('${workflow.id}')">Edit</button>
                        <button class="btn btn-primary" onclick="executeWorkflowById('${workflow.id}')">Execute</button>
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('workflows-list').innerHTML = '<p>Error loading workflows</p>';
            }
        }

        async function loadExecutions() {
            try {
                const response = await fetch('/api/executions');
                const executions = await response.json();

                const listDiv = document.getElementById('executions-list');
                listDiv.innerHTML = executions.slice(0, 10).map(execution => `
                    <div style="padding: 15px; border: 1px solid #ddd; margin: 10px 0; border-radius: 4px;">
                        <h4>Execution: ${execution.execution_id}</h4>
                        <p>Status: <strong>${execution.status}</strong></p>
                        <p>Nodes executed: ${execution.nodes_executed}/${execution.total_nodes}</p>
                        <small>Started: ${new Date(execution.started_at).toLocaleString()}</small>
                        ${execution.completed_at ? `<small>Completed: ${new Date(execution.completed_at).toLocaleString()}</small>` : ''}
                        ${execution.error_message ? `<p style="color: red;">Error: ${execution.error_message}</p>` : ''}
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('executions-list').innerHTML = '<p>Error loading executions</p>';
            }
        }

        // Setup drag and drop
        document.querySelectorAll('.component').forEach(component => {
            component.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text', component.dataset.type);
            });
        });

        // Initialize
        updateNodeCount();
    </script>
</body>
</html>
"""

@app.route('/')
def workflow_builder():
    """Workflow builder UI"""
    return WORKFLOW_BUILDER_HTML

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config['API_VERSION'],
            'queue_size': workflow_queue.qsize()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Workflow Management APIs
@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """List all workflows"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM workflows
                WHERE is_active = true
                ORDER BY created_at DESC
            """)
            workflows = cur.fetchall()
        conn.close()

        return jsonify({
            'workflows': [dict(w) for w in workflows],
            'total_count': len(workflows)
        })

    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        return jsonify({'error': 'Failed to list workflows'}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create new workflow"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'nodes']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Generate workflow ID
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Validate workflow structure
        validation_result = validate_workflow_structure(data['nodes'])
        if not validation_result['valid']:
            return jsonify({'error': f'Invalid workflow structure: {validation_result["error"]}'}), 400

        # Create workflow
        workflow = {
            'workflow_id': workflow_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'nodes': data['nodes'],
            'created_by': data.get('created_by', 'system'),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Store in database
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO workflows (workflow_id, name, description, nodes,
                                   created_by, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                workflow_id, data['name'], data.get('description', ''),
                json.dumps(data['nodes']), data.get('created_by', 'system'),
                True, datetime.utcnow(), datetime.utcnow()
            ))
        conn.commit()
        conn.close()

        logger.info(f"Created workflow {workflow_id}: {data['name']}")

        return jsonify({
            'workflow_id': workflow_id,
            'status': 'created',
            'message': 'Workflow created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        return jsonify({'error': 'Failed to create workflow'}), 500

@app.route('/api/workflows/from-description', methods=['POST'])
def create_workflow_from_description():
    """Extract workflow from natural language description using Claude AI"""
    try:
        data = request.get_json()

        # Validate required fields
        if 'description' not in data:
            return jsonify({'error': 'Missing required field: description'}), 400

        description = data['description']
        workflow_name = data.get('workflow_name', f"Workflow_{uuid.uuid4().hex[:8]}")

        # Use Claude to parse natural language into workflow
        workflow_json = parse_workflow_from_description(description)

        if not workflow_json or 'error' in workflow_json:
            return jsonify({'error': 'Failed to parse workflow from description'}), 400

        # Create workflow from parsed JSON
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Validate workflow structure
        validation_result = validate_workflow_structure(workflow_json.get('nodes', []))
        if not validation_result['valid']:
            return jsonify({'error': f'Invalid workflow generated: {validation_result["error"]}'}), 400

        # Store in database
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO workflows (workflow_id, name, description, nodes,
                                   created_by, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                workflow_id, workflow_name, description,
                json.dumps(workflow_json.get('nodes', [])), 'ai-generated',
                True, datetime.utcnow(), datetime.utcnow()
            ))
        conn.commit()
        conn.close()

        logger.info(f"Created workflow from description: {workflow_id}")

        return jsonify({
            'workflow_id': workflow_id,
            'workflow_name': workflow_name,
            'status': 'created',
            'message': 'Workflow created from natural language description',
            'workflow': workflow_json,
            'nodes_count': len(workflow_json.get('nodes', []))
        }), 201

    except Exception as e:
        logger.error(f"Error creating workflow from description: {str(e)}")
        return jsonify({'error': f'Failed to create workflow: {str(e)}'}), 500


@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get specific workflow"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM workflows WHERE workflow_id = %s AND is_active = true
            """, (workflow_id,))
            workflow = cur.fetchone()

        if not workflow:
            conn.close()
            return jsonify({'error': 'Workflow not found'}), 404

        workflow_dict = dict(workflow)
        workflow_dict['nodes'] = json.loads(workflow_dict['nodes'])

        return jsonify(workflow_dict)

    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {str(e)}")
        return jsonify({'error': 'Failed to get workflow'}), 500

@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """Execute a workflow"""
    try:
        data = request.get_json()

        # Get workflow
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM workflows WHERE workflow_id = %s AND is_active = true
            """, (workflow_id,))
            workflow = cur.fetchone()

        if not workflow:
            conn.close()
            return jsonify({'error': 'Workflow not found'}), 404

        # Create execution record
        execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        execution = {
            'execution_id': execution_id,
            'workflow_id': workflow_id,
            'nodes': json.loads(workflow['nodes']),
            'trigger_data': data.get('trigger_data', {}),
            'status': 'RUNNING',
            'started_at': datetime.utcnow(),
            'total_nodes': len(json.loads(workflow['nodes'])),
            'nodes_executed': 0,
            'created_by': data.get('triggered_by', 'system')
        }

        # Store execution
        cur.execute("""
            INSERT INTO workflow_executions (execution_id, workflow_id, nodes, trigger_data,
                                               status, started_at, total_nodes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            execution_id, workflow_id, json.dumps(execution['nodes']),
            json.dumps(data.get('trigger_data', {})), 'RUNNING',
            datetime.utcnow(), len(execution['nodes']), data.get('triggered_by', 'system')
        ))
        conn.commit()
        conn.close()

        # Queue for execution
        try:
            workflow_queue.put(execution, timeout=5)
            logger.info(f"Queued workflow execution {execution_id}")
        except queue.Full:
            return jsonify({'error': 'Execution queue full'}), 503

        return jsonify({
            'execution_id': execution_id,
            'status': 'queued',
            'message': 'Workflow execution queued'
        })

    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
        return jsonify({'error': 'Failed to execute workflow'}), 500

@app.route('/api/executions', methods=['GET'])
def list_executions():
    """List workflow executions"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM workflow_executions
                ORDER BY started_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            executions = cur.fetchall()

            # Get total count
            cur.execute("""
                SELECT COUNT(*) as total FROM workflow_executions
            """)
            total_count = cur.fetchone()['total']

        conn.close()

        return jsonify({
            'executions': [dict(e) for e in executions],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total_count
            }
        })

    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        return jsonify({'error': 'Failed to list executions'}), 500

@app.route('/api/executions/<execution_id>', methods=['GET'])
def get_execution(execution_id):
    """Get execution details"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM workflow_executions WHERE execution_id = %s
            """, (execution_id,))
            execution = cur.fetchone()

            if not execution:
                conn.close()
                return jsonify({'error': 'Execution not found'}), 404

            # Get execution logs
            cur.execute("""
                SELECT * FROM execution_logs
                WHERE execution_id = %s
                ORDER BY created_at ASC
            """, (execution_id,))
            logs = cur.fetchall()

        conn.close()

        execution_dict = dict(execution)
        execution_dict['nodes'] = json.loads(execution_dict['nodes'])
        execution_dict['trigger_data'] = json.loads(execution_dict['trigger_data'])
        execution_dict['logs'] = [dict(log) for log in logs]

        return jsonify(execution_dict)

    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {str(e)}")
        return jsonify({'error': 'Failed to get execution'}), 500

# DSL and Component APIs
@app.route('/api/components/triggers', methods=['GET'])
def list_triggers():
    """List available trigger components"""
    triggers = [
        {
            'id': 'webhook_trigger',
            'name': 'Webhook Trigger',
            'description': 'Triggered by incoming webhook events',
            'configurable_fields': ['event_source', 'event_type', 'conditions']
        },
        {
            'id': 'schedule_trigger',
            'name': 'Scheduled Trigger',
            'description': 'Triggered on schedule',
            'configurable_fields': ['schedule', 'timezone', 'conditions']
        },
        {
            'id': 'manual_trigger',
            'name': 'Manual Trigger',
            'description': 'Manually triggered by user',
            'configurable_fields': ['description', 'notes']
        }
    ]

    return jsonify({'triggers': triggers})

@app.route('/api/components/conditions', methods=['GET'])
def list_conditions():
    """List available condition components"""
    conditions = [
        {
            'id': 'field_condition',
            'name': 'Field Value Condition',
            'description': 'Check field value against criteria',
            'configurable_fields': ['field_path', 'operator', 'value', 'data_type']
        },
        {
            'id': 'status_condition',
            'name': 'Status Condition',
            'description': 'Check entity status',
            'configurable_fields': ['entity_type', 'status_field', 'operator', 'value']
        },
        {
            'id': 'time_condition',
            'name': 'Time-based Condition',
            'description': 'Check time-based criteria',
            'configurable_fields': ['time_field', 'operator', 'value', 'timezone']
        }
    ]

    return jsonify({'conditions': conditions})

@app.route('/api/components/actions', methods=['GET'])
def list_actions():
    """List available action components"""
    actions = [
        {
            'id': 'api_call_action',
            'name': 'API Call',
            'description': 'Make HTTP API call to external service',
            'configurable_fields': ['target_service', 'endpoint', 'method', 'payload', 'headers']
        },
        {
            'id': 'notification_action',
            'name': 'Send Notification',
            'description': 'Send email/other notification',
            'configurable_fields': ['notification_type', 'recipients', 'subject', 'message']
        },
        {
            'id': 'data_update_action',
            'name': 'Update Data',
            'description': 'Update data in database or external system',
            'configurable_fields': ['target_entity', 'update_fields', 'condition']
        },
        {
            'id': 'workflow_action',
            'name': 'Trigger Workflow',
            'description': 'Trigger another workflow',
            'configurable_fields': ['target_workflow_id', 'parameters']
        }
    ]

    return jsonify({'actions': actions})

# Helper functions
def validate_workflow_structure(nodes):
    """Validate workflow node structure"""
    try:
        if not isinstance(nodes, list) or len(nodes) == 0:
            return {'valid': False, 'error': 'Workflow must have at least one node'}

        # Check for required nodes
        has_trigger = any(node.get('type') == 'trigger' for node in nodes)
        has_action = any(node.get('type') == 'action' for node in nodes)

        if not has_trigger:
            return {'valid': False, 'error': 'Workflow must have at least one trigger node'}

        if not has_action:
            return {'valid': False, 'error': 'Workflow must have at least one action node'}

        # Validate node structure
        for node in nodes:
            if 'type' not in node or 'id' not in node:
                return {'valid': False, 'error': 'Each node must have type and id'}

        return {'valid': True}

    except Exception as e:
        logger.error(f"Error validating workflow structure: {str(e)}")
        return {'valid': False, 'error': str(e)}

def workflow_executor_worker():
    """Background worker to execute workflows"""
    while True:
        try:
            execution = workflow_queue.get(timeout=1)
            execution_id = execution['execution_id']

            logger.info(f"Executing workflow {execution_id}")

            try:
                # Execute workflow
                result = execute_workflow_logic(execution)

                # Update execution status
                update_execution_status(execution_id, 'COMPLETED', result)
                logger.info(f"Successfully executed workflow {execution_id}")

            except Exception as e:
                logger.error(f"Error executing workflow {execution_id}: {str(e)}")
                update_execution_status(execution_id, 'FAILED', {'error': str(e)})

            workflow_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error in workflow executor: {str(e)}")
            continue

def execute_workflow_logic(execution):
    """Execute workflow logic"""
    nodes = execution['nodes']
    trigger_data = execution.get('trigger_data', {})
    context = {'trigger_data': trigger_data}

    executed_nodes = []

    for node in nodes:
        try:
            node_id = node['id']
            node_type = node['type']
            properties = node['properties']

            # Log node execution
            log_execution_node(execution['execution_id'], node_id, 'STARTED', properties)

            if node_type == 'trigger':
                result = execute_trigger(properties, context)
            elif node_type == 'condition':
                result = execute_condition(properties, context)
                if not result['satisfied']:
                    # Condition failed, stop workflow
                    break
            elif node_type == 'action':
                result = execute_action(properties, context)
            else:
                result = {'success': False, 'error': f'Unknown node type: {node_type}'}

            # Update context with result
            if result.get('success', False):
                context[f'node_{node_id}_result'] = result.get('data', {})

            executed_nodes.append({
                'node_id': node_id,
                'type': node_type,
                'success': result.get('success', False),
                'result': result,
                'executed_at': datetime.utcnow().isoformat()
            })

            log_execution_node(execution['execution_id'], node_id, 'COMPLETED', result)

        except Exception as e:
            logger.error(f"Error executing node {node['id']}: {str(e)}")
            continue

    return {
        'success': True,
        'executed_nodes': executed_nodes,
        'final_context': context
    }

def execute_trigger(properties, context):
    """Execute trigger node"""
    trigger_type = properties.get('trigger_type', 'webhook')

    if trigger_type == 'webhook':
        # Check if webhook event matches
        event_source = properties.get('event_source')
        received_event = context['trigger_data'].get('event_type')

        if event_source == received_event:
            return {'success': True, 'data': {'event_matched': True}}
        else:
            return {'success': False, 'error': 'Event does not match trigger'}

    elif trigger_type == 'schedule':
        # Check if current time matches schedule
        # This would implement schedule matching logic
        return {'success': True, 'data': {'schedule_matched': True}}

    elif trigger_type == 'manual':
        # Manual triggers always succeed
        return {'success': True, 'data': {'manual_trigger': True}}

    else:
        return {'success': False, 'error': f'Unknown trigger type: {trigger_type}'}

def execute_condition(properties, context):
    """Execute condition node"""
    condition_type = properties.get('condition_type', 'field')

    if condition_type == 'field':
        field_path = properties.get('field_path')
        operator = properties.get('operator')
        expected_value = properties.get('value')

        # Get field value from context
        actual_value = get_context_value(context, field_path)

        # Evaluate condition
        if operator == 'equals':
            satisfied = actual_value == expected_value
        elif operator == 'not_equals':
            satisfied = actual_value != expected_value
        elif operator == 'greater_than':
            satisfied = actual_value > expected_value
        elif operator == 'less_than':
            satisfied = actual_value < expected_value
        else:
            satisfied = False

        return {
            'satisfied': satisfied,
            'data': {
                'field_path': field_path,
                'actual_value': actual_value,
                'expected_value': expected_value,
                'operator': operator
            }
        }

    else:
        return {'satisfied': False, 'error': f'Unknown condition type: {condition_type}'}

def execute_action(properties, context):
    """Execute action node"""
    action_type = properties.get('action_type', 'api_call')

    if action_type == 'api_call':
        return execute_api_call(properties, context)
    elif action_type == 'notification':
        return execute_notification(properties, context)
    elif action_type == 'data_update':
        return execute_data_update(properties, context)
    elif action_type == 'workflow':
        return execute_workflow_action(properties, context)
    else:
        return {'success': False, 'error': f'Unknown action type: {action_type}'}

def execute_api_call(properties, context):
    """Execute API call action"""
    target_service = properties.get('target_service')
    endpoint = properties.get('endpoint')
    method = properties.get('method', 'POST')
    payload = properties.get('payload', {})

    # This would make actual API call
    # For now, simulate success
    logger.info(f"API Call: {method} {target_service}{endpoint}")

    return {
        'success': True,
        'data': {
            'service': target_service,
            'endpoint': endpoint,
            'method': method,
            'payload': payload
        }
    }

def execute_notification(properties, context):
    """Execute notification action"""
    notification_type = properties.get('notification_type', 'email')
    recipients = properties.get('recipients', [])

    logger.info(f"Sending {notification_type} notification to {len(recipients)} recipients")

    return {
        'success': True,
        'data': {
            'notification_type': notification_type,
            'recipients': recipients,
            'sent_at': datetime.utcnow().isoformat()
        }
    }

def execute_data_update(properties, context):
    """Execute data update action"""
    target_entity = properties.get('target_entity')
    update_fields = properties.get('update_fields', {})

    logger.info(f"Updating {target_entity} with fields: {update_fields}")

    return {
        'success': True,
        'data': {
            'entity': target_entity,
            'updated_fields': update_fields,
            'updated_at': datetime.utcnow().isoformat()
        }
    }

def execute_workflow_action(properties, context):
    """Execute workflow trigger action"""
    target_workflow_id = properties.get('target_workflow_id')
    parameters = properties.get('parameters', {})

    logger.info(f"Triggering workflow {target_workflow_id} with parameters: {parameters}")

    return {
        'success': True,
        'data': {
            'workflow_id': target_workflow_id,
            'parameters': parameters,
            'triggered_at': datetime.utcnow().isoformat()
        }
    }

def get_context_value(context, field_path):
    """Get value from context using dot notation"""
    keys = field_path.split('.')
    value = context

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None

    return value

def update_execution_status(execution_id, status, result=None):
    """Update execution status in database"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if result:
                cur.execute("""
                    UPDATE workflow_executions SET status = %s, completed_at = %s,
                                           nodes_executed = nodes_executed,
                                           error_message = %s
                    WHERE execution_id = %s
                """, (status, datetime.utcnow(),
                       result.get('executed_nodes', 0), result.get('error'), execution_id))
            else:
                cur.execute("""
                    UPDATE workflow_executions SET status = %s, completed_at = %s
                    WHERE execution_id = %s
                """, (status, datetime.utcnow(), execution_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating execution status: {str(e)}")

def log_execution_node(execution_id, node_id, status, data):
    """Log execution node status"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO execution_logs (execution_id, node_id, status, data, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (execution_id, node_id, status, json.dumps(data), datetime.utcnow()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging execution node: {str(e)}")


def parse_workflow_from_description(description: str) -> Dict:
    """
    Use Claude AI to parse natural language workflow description into structured workflow JSON.
    Supports saving as reusable behaviors.
    """
    try:
        # Initialize Anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set - NL workflow extraction disabled")
            return {'error': 'API key not configured'}

        client = anthropic.Anthropic(api_key=api_key)

        # System prompt for Claude
        system_prompt = """You are an expert workflow automation engineer. Convert natural language workflow descriptions into structured JSON workflow definitions.

Available Services:
- dox-actv-service: Activation & workflow management
- dox-esig-service: E-signature processing
- dox-batch-assembly: Document batching
- dox-core-store: Data storage
- dox-tmpl-service: Template management
- dox-lifecycle-service: Contract lifecycle
- dox-data-aggregation-service: Analytics & reporting

Available Triggers:
- webhook (event-based)
- schedule (time-based)
- manual (user-initiated)

Available Actions:
- api_call: Call external service
- notification: Send email/alert
- data_update: Update database/entity
- workflow: Trigger another workflow

Output ONLY valid JSON with this structure:
{
  "workflow_name": "descriptive name",
  "description": "what this workflow does",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "properties": {
        "trigger_type": "webhook|schedule|manual",
        "event_source": "event name or schedule",
        "description": "what triggers this"
      }
    },
    {
      "id": "condition_1",
      "type": "condition",
      "properties": {
        "condition_type": "field",
        "field_path": "entity.field",
        "operator": "equals|not_equals|greater_than|less_than|contains",
        "value": "expected value"
      }
    },
    {
      "id": "action_1",
      "type": "action",
      "properties": {
        "action_type": "api_call|notification|data_update|workflow",
        "target_service": "service name",
        "endpoint": "/api/endpoint",
        "method": "POST|GET|PUT|DELETE",
        "description": "what this action does"
      }
    }
  ]
}

Include at least 1 trigger and 1 action. Use descriptive node IDs."""

        # Create message to Claude
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Convert this workflow description into structured JSON:\n\n{description}"
                }
            ]
        )

        # Extract response text
        response_text = message.content[0].text

        # Parse JSON from response
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Try to parse the entire response as JSON
            json_str = response_text.strip()

        # Parse JSON
        workflow = json.loads(json_str)

        # Validate required fields
        if 'nodes' not in workflow:
            return {'error': 'Generated workflow missing nodes'}

        logger.info(f"Parsed workflow with {len(workflow['nodes'])} nodes from description")
        return workflow

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from Claude response: {e}")
        return {'error': f'Invalid JSON generated: {str(e)}'}
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return {'error': f'AI service error: {str(e)}'}
    except Exception as e:
        logger.error(f"Error parsing workflow description: {str(e)}")
        return {'error': str(e)}

# Initialize database tables
def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(500) NOT NULL,
                description TEXT,
                nodes JSONB NOT NULL,
                created_by VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workflow_executions (
                execution_id VARCHAR(255) PRIMARY KEY,
                workflow_id VARCHAR(255) NOT NULL,
                nodes JSONB NOT NULL,
                trigger_data JSONB,
                status VARCHAR(50) NOT NULL DEFAULT 'QUEUED',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                total_nodes INTEGER NOT NULL,
                nodes_executed INTEGER DEFAULT 0,
                created_by VARCHAR(255),
                FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
            );

            CREATE TABLE IF NOT EXISTS execution_logs (
                id SERIAL PRIMARY KEY,
                execution_id VARCHAR(255) NOT NULL,
                node_id VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (execution_id) REFERENCES workflow_executions(execution_id)
            );

            CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at);
            CREATE INDEX IF NOT EXISTS idx_workflow_executions_started_at ON workflow_executions(started_at);
            CREATE INDEX IF NOT EXISTS idx_execution_logs_execution_id ON execution_logs(execution_id);
        """)
    conn.commit()
    conn.close()
    logger.info("Database tables initialized")

# Start background workers
def start_workflow_executor():
    """Start background workflow executor"""
    executor_thread = threading.Thread(target=workflow_executor_worker, daemon=True)
    executor_thread.start()
    logger.info("Workflow executor started")

if __name__ == '__main__':
    # Initialize database
    init_database()

    # Start background workers
    start_workflow_executor()

    # Run the app
    port = int(os.environ.get('PORT', 5006))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')