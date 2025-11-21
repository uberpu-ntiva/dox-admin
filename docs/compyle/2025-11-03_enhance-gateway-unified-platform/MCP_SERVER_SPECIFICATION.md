# DOX MCP Server Specification

## Overview

The **dox-mcp-server** is a Model Context Protocol (MCP) server that exposes all DOX platform functionality as callable tools for Claude Desktop and AI agents. It provides a unified interface to the entire DOX platform through the gateway.

## Architecture

```
Claude Desktop / AI Agent
           ↓
    MCP Client Protocol
           ↓
  dox-mcp-server (MCP Server)
           ↓
  DOX API Gateway (dox-gtwy-main)
           ↓
  20+ Microservices (all DOX services)
```

## MCP Server Implementation

### File: `/dox-mcp-server/server.py`

```python
"""
DOX MCP Server
Exposes DOX platform as Model Context Protocol tools
"""

import os
import json
import requests
from typing import Any, Dict, List
from pydantic import BaseModel, Field
import mcp.server.models as models
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource

# Configuration
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8080")
GATEWAY_AUTH_TOKEN = os.environ.get("GATEWAY_AUTH_TOKEN", "")

# Initialize MCP Server
server = Server("dox-mcp-server")

# Define request/response models
class DocumentUploadRequest(BaseModel):
    file_path: str = Field(..., description="Path to document file")
    document_type: str = Field(..., description="Type: pdf, image, scan")
    account_id: str = Field(..., description="Customer account ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class WorkflowCreateRequest(BaseModel):
    workflow_name: str = Field(..., description="Name for workflow")
    description: str = Field(..., description="Natural language description of workflow")
    trigger_type: str = Field(..., description="Trigger: webhook, schedule, manual")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Workflow steps")

class DocumentQueryRequest(BaseModel):
    query: str = Field(..., description="Search query")
    account_id: str = Field(default=None, description="Filter by account")
    document_type: str = Field(default=None, description="Filter by type")
    limit: int = Field(default=50, description="Max results")

# Helper function to call gateway
def call_gateway(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Call DOX API Gateway"""
    url = f"{GATEWAY_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {GATEWAY_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Gateway error: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

# Define MCP Tools

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available DOX platform tools."""
    return [
        # Document Operations
        Tool(
            name="upload_document",
            description="Upload a document to the DOX platform for processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to document file"},
                    "document_type": {"type": "string", "description": "Type: pdf, image, scan"},
                    "account_id": {"type": "string", "description": "Customer account ID"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["file_path", "document_type", "account_id"]
            }
        ),
        Tool(
            name="search_documents",
            description="Search for documents in the platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "account_id": {"type": "string", "description": "Filter by account"},
                    "document_type": {"type": "string", "description": "Filter by type"},
                    "limit": {"type": "integer", "description": "Max results", "default": 50}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_document_status",
            description="Get processing status of a document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID"}
                },
                "required": ["document_id"]
            }
        ),

        # Workflow Operations
        Tool(
            name="create_workflow",
            description="Create a new automation workflow from description",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string", "description": "Name for workflow"},
                    "description": {"type": "string", "description": "What should happen?"},
                    "trigger_type": {"type": "string", "description": "When: webhook, schedule, manual"},
                    "actions": {"type": "string", "description": "What actions to perform?"}
                },
                "required": ["workflow_name", "description", "trigger_type"]
            }
        ),
        Tool(
            name="execute_workflow",
            description="Execute an existing workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow ID"},
                    "input_data": {"type": "object", "description": "Input parameters"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="list_workflows",
            description="List all available workflows",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results", "default": 50}
                }
            }
        ),

        # Contract/Lifecycle Operations
        Tool(
            name="create_contract",
            description="Create a new contract and manage its lifecycle",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_name": {"type": "string", "description": "Contract name"},
                    "contract_type": {"type": "string", "description": "Type of contract"},
                    "party_id": {"type": "string", "description": "Party/customer ID"},
                    "start_date": {"type": "string", "description": "Start date (ISO 8601)"},
                    "value": {"type": "number", "description": "Contract value"},
                    "terms": {"type": "object", "description": "Contract terms"}
                },
                "required": ["contract_name", "contract_type", "party_id", "start_date"]
            }
        ),
        Tool(
            name="transition_contract_state",
            description="Transition contract to next state (draft→review→signature→active)",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string", "description": "Contract ID"},
                    "new_state": {"type": "string", "description": "Target state"}
                },
                "required": ["contract_id", "new_state"]
            }
        ),
        Tool(
            name="get_contract_status",
            description="Get contract current state and lifecycle info",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string", "description": "Contract ID"}
                },
                "required": ["contract_id"]
            }
        ),

        # E-Signature Operations
        Tool(
            name="request_signatures",
            description="Create a signature request for a document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID"},
                    "signers": {"type": "array", "description": "List of signer emails"},
                    "message": {"type": "string", "description": "Message for signers"},
                    "due_date": {"type": "string", "description": "Signature deadline"}
                },
                "required": ["document_id", "signers"]
            }
        ),
        Tool(
            name="get_signature_status",
            description="Check status of signature request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "Signature request ID"}
                },
                "required": ["request_id"]
            }
        ),

        # Data & Analytics
        Tool(
            name="get_platform_analytics",
            description="Get platform-wide analytics and metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_type": {"type": "string", "description": "Type: documents_processed, workflows_executed, contracts_active"},
                    "time_range": {"type": "string", "description": "Range: today, week, month, year"}
                }
            }
        ),
        Tool(
            name="get_account_summary",
            description="Get account summary and activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "Account ID"}
                },
                "required": ["account_id"]
            }
        ),

        # Batch Operations
        Tool(
            name="create_batch",
            description="Create a batch assembly for document processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "batch_name": {"type": "string", "description": "Batch name"},
                    "document_ids": {"type": "array", "description": "Document IDs to batch"},
                    "bundling_strategy": {"type": "string", "description": "Strategy: sequential, grouped, hierarchical"},
                    "target_format": {"type": "string", "description": "Output format: pdf, zip, archive"}
                },
                "required": ["batch_name", "document_ids"]
            }
        ),
        Tool(
            name="get_batch_status",
            description="Check batch assembly progress",
            inputSchema={
                "type": "object",
                "properties": {
                    "batch_id": {"type": "string", "description": "Batch ID"}
                },
                "required": ["batch_id"]
            }
        ),

        # Field Mapping
        Tool(
            name="extract_fields",
            description="Extract fields from document using template",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID"},
                    "template_id": {"type": "string", "description": "Template ID for field definition"},
                    "override_values": {"type": "object", "description": "Override specific field values"}
                },
                "required": ["document_id"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle tool calls from Claude."""

    if name == "upload_document":
        return call_gateway("POST", "/pdf-upload/documents", arguments)

    elif name == "search_documents":
        query_params = "&".join([f"{k}={v}" for k, v in arguments.items()])
        return call_gateway("GET", f"/storage/documents/search?{query_params}")

    elif name == "get_document_status":
        doc_id = arguments.get("document_id")
        return call_gateway("GET", f"/storage/documents/{doc_id}/status")

    elif name == "create_workflow":
        return call_gateway("POST", "/workflows-engine/workflows/create", arguments)

    elif name == "execute_workflow":
        workflow_id = arguments.get("workflow_id")
        return call_gateway("POST", f"/workflows-engine/workflows/{workflow_id}/execute",
                           {"input_data": arguments.get("input_data", {})})

    elif name == "list_workflows":
        return call_gateway("GET", "/workflows-engine/workflows")

    elif name == "create_contract":
        return call_gateway("POST", "/lifecycle/contracts", arguments)

    elif name == "transition_contract_state":
        contract_id = arguments.get("contract_id")
        return call_gateway("POST", f"/lifecycle/contracts/{contract_id}/transition",
                           {"new_state": arguments.get("new_state")})

    elif name == "get_contract_status":
        contract_id = arguments.get("contract_id")
        return call_gateway("GET", f"/lifecycle/contracts/{contract_id}")

    elif name == "request_signatures":
        return call_gateway("POST", "/esig/signature-requests", arguments)

    elif name == "get_signature_status":
        request_id = arguments.get("request_id")
        return call_gateway("GET", f"/esig/signature-requests/{request_id}/status")

    elif name == "get_platform_analytics":
        return call_gateway("GET", "/data-aggregation/analytics",  arguments)

    elif name == "get_account_summary":
        account_id = arguments.get("account_id")
        return call_gateway("GET", f"/storage/accounts/{account_id}/summary")

    elif name == "create_batch":
        return call_gateway("POST", "/batch/assemblies", arguments)

    elif name == "get_batch_status":
        batch_id = arguments.get("batch_id")
        return call_gateway("GET", f"/batch/assemblies/{batch_id}")

    elif name == "extract_fields":
        return call_gateway("POST", "/field-mapping/extract", arguments)

    else:
        return {"error": f"Unknown tool: {name}"}

# List resources available
@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources and documentation."""
    return [
        Resource(
            uri="dox://platform/documentation",
            name="DOX Platform Documentation",
            description="Complete API and integration guide"
        ),
        Resource(
            uri="dox://platform/workflows",
            name="Workflow Templates",
            description="Pre-built workflow templates"
        ),
        Resource(
            uri="dox://platform/templates",
            name="Document Templates",
            description="Available document templates"
        )
    ]

# Main entry point
if __name__ == "__main__":
    import uvicorn

    # For debugging locally
    port = int(os.environ.get("MCP_SERVER_PORT", 8888))
    uvicorn.run(server, host="0.0.0.0", port=port)
```

## Integration with Claude Desktop

Create configuration file: `~/.config/Claude/mcp-config.json`

```json
{
  "mcpServers": {
    "dox": {
      "command": "python",
      "args": ["/path/to/dox-mcp-server/server.py"],
      "env": {
        "GATEWAY_URL": "http://localhost:8080",
        "GATEWAY_AUTH_TOKEN": "your-auth-token",
        "MCP_SERVER_PORT": "8888"
      }
    }
  }
}
```

## Usage in Claude Desktop

Once configured, you can use DOX tools directly in Claude conversations:

**Example 1: Upload and Process Document**
```
@Claude: Please upload the contract at /home/user/contracts/agreement.pdf and extract the parties involved.

Claude will:
1. Call upload_document tool
2. Wait for processing
3. Call extract_fields tool
4. Return results
```

**Example 2: Create Automated Workflow**
```
@Claude: Create a workflow that when a contract is signed, automatically creates a batch assembly with all related documents and sends a confirmation email.

Claude will:
1. Call create_workflow tool with natural language description
2. MCP server converts to workflow definition
3. Returns workflow ID
4. Saves it for reuse
```

**Example 3: Analytics and Reporting**
```
@Claude: Show me analytics for this month - how many documents processed, contracts created, and workflows executed?

Claude will:
1. Call get_platform_analytics tool
2. Return metrics dashboard
3. Provide insights and trends
```

## Deployment Options

### Option 1: Docker Container
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .
ENV GATEWAY_URL=http://dox-gtwy-main:8080
CMD ["python", "server.py"]
```

### Option 2: Kubernetes Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: dox-mcp-server
spec:
  selector:
    app: dox-mcp-server
  ports:
    - port: 8888
      targetPort: 8888
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dox-mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dox-mcp-server
  template:
    metadata:
      labels:
        app: dox-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: dox-mcp-server:latest
        ports:
        - containerPort: 8888
        env:
        - name: GATEWAY_URL
          value: http://dox-gtwy-main:8080
        - name: GATEWAY_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: dox-secrets
              key: mcp-token
```

## Key Benefits

✅ **Unified Interface** - All 20+ services through single tool set
✅ **Natural Language** - Describe what you want, MCP translates to API calls
✅ **Claude Integration** - Use DOX platform directly in Claude Desktop
✅ **Error Handling** - Circuit breakers, retries, graceful degradation
✅ **Rate Limiting** - Inherited from gateway (50-200 req/min per service)
✅ **Monitoring** - All calls logged and metriced via gateway
✅ **Extensible** - Easy to add new tools as services scale

## Next Steps

1. Create `dox-mcp-server` repository in your workspace
2. Copy server.py implementation above
3. Deploy via Docker or Kubernetes
4. Configure Claude Desktop with mcp-config.json
5. Start using DOX tools in Claude conversations!

