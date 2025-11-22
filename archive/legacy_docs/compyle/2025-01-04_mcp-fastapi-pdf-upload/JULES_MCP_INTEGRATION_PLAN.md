# Jules MCP Integration Plan

**Date**: 2025-11-03
**Goal**: Integrate Google Jules API with custom MCP server for cost optimization and testing
**Repository**: https://github.com/uberpu-ntiva/jules-mcp
**Next Task**: Implement after hybrid infrastructure setup

---

## Executive Summary

**Opportunity**: Create a custom MCP server that integrates with Google Jules API to offset costs and provide AI-powered development capabilities within our dox ecosystem.

**Strategy**: Build a Jules MCP server that can:
- Automate code generation and bug fixes using Jules
- Integrate with our existing dox services
- Provide cost-effective AI assistance
- Test Jules capabilities in our environment

---

## Jules API Overview

### What is Jules?

Google Jules is an AI-powered coding assistant that can:
- Fix bugs automatically
- Generate code from requirements
- Review and optimize code
- Create pull requests
- Handle complex development tasks

### API Capabilities

Based on research from https://developers.google.com/jules/api:

**Core Resources**:
- **Source**: Input sources (GitHub repositories)
- **Session**: Continuous work units (like chat sessions)
- **Activity**: Individual actions within sessions

**API Methods**:
- `POST /v1alpha/sessions` - Create new coding session
- `GET /v1alpha/sessions/{id}` - Get session details
- `POST /v1alpha/sessions/{id}:approvePlan` - Approve generated plan
- `GET /v1alpha/sources` - List available sources
- `POST /v1alpha/sources` - Add new source

**Authentication**:
- API Key authentication (X-Goog-Api-Key header)
- Max 3 API keys per account
- Setup via https://jules.google/settings#api

---

## Proposed MCP Server Architecture

### Repository: https://github.com/uberpu-ntiva/jules-mcp

### MCP Tools to Implement

**1. Code Generation Tool**
```python
@mcp.tool()
async def generate_code(
    repository_url: str,
    prompt: str,
    branch: str = "main"
) -> dict:
    """
    Generate code using Jules AI for a specific repository.

    Args:
        repository_url: GitHub repository URL
        prompt: Description of code to generate
        branch: Target branch for changes

    Returns:
        Generated code and plan details
    """
```

**2. Bug Fix Tool**
```python
@mcp.tool()
async def fix_bug(
    repository_url: str,
    bug_description: str,
    file_path: Optional[str] = None
) -> dict:
    """
    Fix bugs automatically using Jules AI.

    Args:
        repository_url: GitHub repository URL
        bug_description: Description of the bug to fix
        file_path: Optional specific file to fix

    Returns:
        Bug fix details and implementation plan
    """
```

**3. Code Review Tool**
```python
@mcp.tool()
async def review_code(
    repository_url: str,
    pull_request_url: str,
    review_focus: str = "general"
) -> dict:
    """
    Review code changes using Jules AI.

    Args:
        repository_url: GitHub repository URL
        pull_request_url: Pull request to review
        review_focus: Focus area (security, performance, style)

    Returns:
        Code review feedback and suggestions
    """
```

**4. Session Management Tool**
```python
@mcp.tool()
async def create_jules_session(
    repository_url: str,
    task_description: str,
    session_type: str = "coding"
) -> dict:
    """
    Create a new Jules coding session.

    Args:
        repository_url: GitHub repository URL
        task_description: Description of the coding task
        session_type: Type of session (coding, review, debugging)

    Returns:
        Session details and activity tracking
    """
```

### MCP Prompts to Implement

**1. Code Analysis Prompt**
```python
@mcp.prompt()
async def analyze_codebase(
    repository_url: str,
    analysis_type: str = "comprehensive"
) -> str:
    """
    Generate a comprehensive codebase analysis prompt for Jules.

    Args:
        repository_url: GitHub repository URL
        analysis_type: Type of analysis (security, performance, architecture)

    Returns:
        Structured prompt for codebase analysis
    """
```

**2. Refactoring Strategy Prompt**
```python
@mcp.prompt()
async def plan_refactoring(
    repository_url: str,
    refactoring_goals: List[str]
) -> str:
    """
    Create a refactoring strategy prompt for Jules.

    Args:
        repository_url: GitHub repository URL
        refactoring_goals: List of refactoring objectives

    Returns:
        Structured prompt for refactoring planning
    """
```

### MCP Resources to Implement

**1. Session Status Resource**
```python
@mcp.resource("jules://sessions/{session_id}")
async def get_session_status(session_id: str) -> dict:
    """Get current status and activities of a Jules session."""
```

**2. Repository Analysis Resource**
```python
@mcp.resource("jules://analysis/{repository_url}")
async def get_repository_analysis(repository_url: str) -> dict:
    """Get cached analysis results for a repository."""
```

---

## Integration with Dox Ecosystem

### Connection Points

**1. dox-tmpl-pdf-upload Integration**
- Use Jules to optimize PDF processing code
- Automate bug fixes in validation logic
- Generate new template recognition algorithms

**2. dox-mcp-server Integration**
- Provide Jules tools alongside existing template tools
- Enable AI-powered code generation within template management
- Automate MCP server improvements

**3. dox-core-auth Integration**
- Use Jules to identify security vulnerabilities
- Generate authentication best practices code
- Automate security patch implementations

### Workflow Integration

**Automated Code Improvement Pipeline**:
```python
# Example workflow
1. User requests template feature improvement
2. MCP server receives request via Jules tool
3. Jules analyzes current codebase
4. Jules generates improved code
5. Automated testing via dox services
6. Pull request creation and review
7. Deployment if tests pass
```

**Bug Fix Automation**:
```python
# Example bug fix workflow
1. Error detected in dox service
2. MCP server triggers Jules bug fix tool
3. Jules analyzes error and generates fix
4. Automated testing of fix
5. PR created and merged automatically
```

---

## Cost Optimization Strategy

### Why Use Jules Through MCP?

**Cost Benefits**:
- Centralized API key management
- Shared sessions across multiple tools
- Optimized prompt engineering
- Reduced redundant API calls
- Caching of common analyses

**Implementation Benefits**:
- Unified AI interface across all dox services
- Consistent prompt templates
- Centralized logging and monitoring
- Easier cost tracking and budgeting

### Cost Control Features

**Session Management**:
- Session pooling and reuse
- Automatic session cleanup
- Cost tracking per session
- Usage quotas and limits

**Smart Caching**:
- Cache common analysis results
- Reuse code generation patterns
- Store frequent fixes
- Implement TTL for cached results

**Usage Monitoring**:
- Real-time cost tracking
- Budget alerts and limits
- Usage analytics and reporting
- Optimization recommendations

---

## Implementation Plan

### Phase 1: Basic MCP Server (Week 1)

**Repository Setup**:
```bash
# Create repository structure
github.com/uberpu-ntiva/jules-mcp/
├── app/
│   ├── main.py              # MCP server entry point
│   ├── tools/
│   │   ├── code_generation.py
│   │   ├── bug_fix.py
│   │   ├── code_review.py
│   │   └── session_management.py
│   ├── prompts/
│   │   ├── code_analysis.py
│   │   └── refactoring_strategy.py
│   ├── resources/
│   │   ├── session_status.py
│   │   └── repository_analysis.py
│   ├── client/
│   │   └── jules_client.py   # Jules API wrapper
│   └── config.py
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Core Implementation**:
- FastMCP server setup
- Jules API client implementation
- Basic code generation tool
- Session management functionality
- Authentication and error handling

### Phase 2: Advanced Features (Week 2)

**Enhanced Tools**:
- Advanced code review capabilities
- Multi-repository support
- Custom prompt templates
- Integration with dox services

**Optimization Features**:
- Response caching
- Session pooling
- Cost tracking
- Usage analytics

### Phase 3: Dox Integration (Week 3)

**Service Integration**:
- Connect to dox-tmpl-pdf-upload
- Integrate with dox-mcp-server
- Hook into dox-core-auth
- Automated workflows

**Testing & Validation**:
- End-to-end testing
- Performance optimization
- Security validation
- Cost analysis

---

## Technical Implementation Details

### Jules API Client

```python
# app/client/jules_client.py
import httpx
from typing import Dict, List, Optional

class JulesClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://jules.googleapis.com"
        self.headers = {
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json"
        }

    async def create_session(
        self,
        repository_url: str,
        task_description: str
    ) -> Dict:
        """Create a new Jules session."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1alpha/sessions",
                headers=self.headers,
                json={
                    "source": {"repository_url": repository_url},
                    "prompt": task_description
                }
            )
            return response.json()

    async def get_session(self, session_id: str) -> Dict:
        """Get session details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1alpha/sessions/{session_id}",
                headers=self.headers
            )
            return response.json()

    async def approve_plan(self, session_id: str) -> Dict:
        """Approve the generated plan."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1alpha/sessions/{session_id}:approvePlan",
                headers=self.headers
            )
            return response.json()
```

### Environment Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Jules API Configuration
    jules_api_key: str
    jules_base_url: str = "https://jules.googleapis.com"

    # MCP Server Configuration
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8000

    # Dox Integration
    dox_pdf_upload_url: str
    dox_mcp_server_url: str

    # Cost Control
    max_daily_cost: float = 100.0
    cost_tracking_enabled: bool = True

    # Caching
    cache_ttl: int = 3600  # 1 hour
    enable_caching: bool = True

    class Config:
        env_file = ".env"
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["python", "app/main.py"]
```

### Docker Compose Integration

```yaml
# Add to existing docker-compose.yml
jules-mcp-server:
  build: ./jules-mcp
  environment:
    - JULES_API_KEY=${JULES_API_KEY}
    - DOX_PDF_UPLOAD_URL=http://dox-tmpl-pdf-upload:8000
    - DOX_MCP_SERVER_URL=http://dox-mcp-server:8000
    - COST_TRACKING_ENABLED=true
    - MAX_DAILY_COST=50.0
  depends_on:
    - dox-tmpl-pdf-upload
    - dox-mcp-server
  networks:
    - dox-network
```

---

## Usage Examples

### Direct MCP Usage

```python
# Using Jules MCP tools directly
import asyncio
from mcp import Client

async def generate_code():
    client = Client()

    # Generate code for template service
    result = await client.call_tool("generate_code", {
        "repository_url": "https://github.com/uberpu-ntiva/dox-tmpl-service",
        "prompt": "Add batch template processing functionality",
        "branch": "feature/batch-processing"
    })

    print(f"Generated plan: {result['plan']}")
    print(f"Estimated cost: ${result['cost_estimate']}")
```

### Integration with Dox Services

```python
# Using Jules within dox-tmpl-pdf-upload
from app.services.jules_integration import JulesIntegration

class TemplateService:
    def __init__(self):
        self.jules = JulesIntegration()

    async def optimize_validation(self, template_id: str):
        """Use Jules to optimize template validation logic."""
        result = await self.jules.fix_bug(
            repository_url="https://github.com/uberpu-ntiva/dox-tmpl-pdf-upload",
            bug_description=f"Optimize validation for template {template_id}",
            file_path="app/services/validation.py"
        )

        return result
```

---

## Cost Analysis

### Expected Cost Savings

**Without MCP Integration**:
- Multiple API keys needed
- Redundant API calls
- No session reuse
- Individual service optimization required

**With Jules MCP Server**:
- Single API key management
- Shared sessions and caching
- Optimized prompt engineering
- Centralized cost tracking

**Estimated Savings**: 30-50% reduction in Jules API costs

### Budget Planning

**Recommended Configuration**:
- Daily budget: $50-100
- Monthly budget: $1,500-3,000
- Session timeout: 24 hours
- Cache TTL: 1 hour
- Max concurrent sessions: 5

---

## Security Considerations

### API Key Management
- Secure storage of API keys
- Rotation policies
- Access logging
- Rate limiting

### Code Security
- Review Jules-generated code before deployment
- Automated security scanning
- Sandboxing for generated code
- Rollback procedures

### Data Privacy
- No sensitive code sent to external APIs
- Local processing where possible
- Data retention policies
- Compliance with organizational policies

---

## Monitoring & Analytics

### Metrics to Track
- API usage and costs
- Session success rates
- Code quality metrics
- Performance improvements
- Error rates and types

### Dashboards
- Real-time cost tracking
- Usage analytics
- Performance metrics
- Security alerts

---

## Next Steps

### Immediate Actions
1. **Create GitHub repository**: https://github.com/uberpu-ntiva/jules-mcp
2. **Obtain Jules API key**: https://jules.google/settings#api
3. **Set up development environment**
4. **Implement basic MCP server**
5. **Test with dox services**

### For Next Task Session
1. **Clone jules-mcp repository**
2. **Implement basic MCP server structure**
3. **Create Jules API client**
4. **Build first MCP tool (code generation)**
5. **Test integration with dox-tmpl-pdf-upload**
6. **Validate cost optimization**

---

**Document Status**: ✅ PLAN READY
**Created**: 2025-11-03
**Next Task**: Implement Jules MCP server after hybrid infrastructure setup
**Repository**: https://github.com/uberpu-ntiva/jules-mcp
**Priority**: HIGH (Cost optimization opportunity)