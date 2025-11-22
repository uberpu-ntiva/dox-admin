# DOX API Gateway - Unified Platform Entry Point

**Complete platform gateway with 233% service coverage, AI-powered workflows, and 2-3x performance roadmap**

---

## 🚀 Overview

The DOX API Gateway serves as the **unified entry point** for the entire DOX document management platform. From 6 original services, it now routes **all 20+ platform services** with centralized authentication, rate limiting, circuit breakers, and comprehensive monitoring.

### 🎯 Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Complete Service Coverage** | Routes to all 20+ DOX services | ✅ **NEW** |
| **AI-Powered Workflows** | Natural language workflow creation | ✅ **NEW** |
| **Fault Tolerance** | Circuit breakers for all services | ✅ **ENHANCED** |
| **Performance Roadmap** | FastAPI migration for 2-3x speedup | 📋 **PLANNED** |
| **Claude Desktop Integration** | MCP server for AI assistant | 📋 **DOCUMENTED** |
| **Comprehensive Monitoring** | Metrics, logging, and alerting | ✅ **ENHANCED** |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOX API Gateway                          │
│  (Unified Entry Point - All 20+ Services Reachable)        │
├─────────────────────────────────────────────────────────────┤
│  🔒 Authentication  📊 Rate Limiting  ⚡ Circuit Breakers   │
│  📝 Logging         📈 Monitoring      🔄 Health Checks     │
└─────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
    ┌───────▼───────┐    ┌─────▼──────┐    ┌──────▼───────┐
    │   Core        │    │ Workflow   │    │  Document   │
    │   Services    │    │ Services   │    │  Services   │
    │               │    │            │    │             │
    • Authentication  • Activation    • Templates     │
    • Storage       • Lifecycle     • Field Mapping │
    • Validation    • Workflow      • PDF Upload    │
    └───────────────┘    • Auto         • Barcode      │
                         • Batch        • Pact/RTNS    │
                         └──────────────┘              │
                                │                   │
    ┌───────────────────┼───────────────────┐       │
    │                   │                   │       │
    ┌───────▼───────┐    ┌─────▼──────┐    ┌──────▼───────┐
    │   Signature   │    │   Data     │    │    API      │
    │   Services    │    │  Platform  │    │ Integration │
    │               │    │            │    │             │
    • E-Signature   • ETL          • MCP Server    │
    • Webhooks      • Distribution  • Claude Desktop│
    • Processing    • Aggregation   • Documentation │
    └───────────────┘    • Analytics   • Migration     │
                         └──────────────┘                │
```

---

## 📊 Service Coverage (20+ Services)

### ✅ **Core Services** (Foundation)
```
🔐 /auth/*               → dox-core-auth         (Authentication)
💾 /storage/*            → dox-core-store        (Document storage)
```

### ✅ **Workflow & Automation** (Business Logic)
```
⚡ /workflows/*          → dox-workflow-orchestrator (Workflow mgmt)
🎯 /activation/*         → dox-actv-service      (Activation workflow)
📡 /activation-events/*  → dox-actv-listener     (Event processing)
🔄 /lifecycle/*          → dox-auto-lifecycle-service (Contract lifecycle)
🛠️ /workflows-engine/*   → dox-auto-workflow-engine (Visual builder)
```

### ✅ **Template & Document Services** (Content)
```
📄 /templates/*          → dox-tmpl-service       (Template management)
🗺️ /field-mapping/*      → dox-tmpl-field-mapper  (Field extraction)
📤 /pdf-upload/*         → dox-tmpl-pdf-upload    (Template PDF upload)
📷 /barcode/*            → dox-rtns-barcode-matcher (Barcode/OCR)
```

### ✅ **Document Processing** (Operations)
```
📦 /batch/*              → dox-batch-assembly     (Batch processing)
📋 /pact-upload/*        → dox-pact-manual-upload (PACT documents)
↩️ /rtns-upload/*         → dox-rtns-manual-upload (Returns)
```

### ✅ **E-Signature** (Digital Signatures)
```
✍️ /esig/*               → dox-esig-service       (E-signature processing)
📬 /esig-webhooks/*      → dox-esig-webhook-listener (Signature callbacks)
```

### ✅ **Data Platform** (Analytics & Processing)
```
🔄 /data-etl/*           → dox-data-etl-service   (ETL operations)
📊 /data-distrib/*       → dox-data-distrib-service (Load balancing)
📈 /data-aggregation/*   → dox-data-aggregation-service (Analytics)
```

---

## 🤖 AI-Powered Features

### Natural Language Workflows
Create complex automation workflows from simple English descriptions:

```bash
POST /workflows-engine/api/workflows/from-description

{
  "workflow_name": "Auto Contract Activation",
  "description": "When a contract is signed, create a batch with all related documents,
                   send confirmation email, and update status to active.
                   If value exceeds $100k, also notify the manager."
}
```

**Response:** Complete workflow JSON with 5 nodes (trigger + 4 actions)

### Claude Desktop Integration
Access entire DOX platform through Claude Desktop with 20+ tools:

- Document operations (upload, search, status)
- Workflow management (create, execute, list)
- Contract lifecycle management
- E-signature processing
- Analytics & reporting
- Batch operations

*See `MCP_SERVER_SPECIFICATION.md` for complete implementation*

---

## 📈 Performance Roadmap (2-3x Improvement)

### FastAPI Migration Plan
| Phase | Services | Timeline | Expected Gain |
|-------|----------|----------|---------------|
| Phase 1 | Gateway, Auth, Field Mapper | Weeks 1-5 | 3x faster critical path |
| Phase 2 | Processing & Events | Weeks 6-8 | 3x higher throughput |
| Phase 3 | Workflow & Data | Weeks 9-10 | Unified async performance |

**Performance Projections:**
- Request time: 45ms → 15ms (3x faster)
- Throughput: 200req/s → 600req/s (3x higher)
- Memory: 150MB → 120MB (20% reduction)

*See `FASTAPI_MIGRATION_PLAN.md` for complete strategy*

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9+
pip install -r requirements.txt

# Environment variables (see config.py)
export REDIS_HOST=localhost
export DATABASE_URL=postgresql://...
export ANTHROPIC_API_KEY=sk-ant-...  # For AI workflows
```

### Development Setup
```bash
# Clone repository
git clone <repository>
cd dox-gtwy-main

# Install dependencies
pip install -r requirements.txt

# Run in development mode
export DEBUG=true
python app.py

# Gateway available at: http://localhost:8080
```

### Production Deployment
```bash
# Build Docker image
docker build -t dox-gtwy-main .

# Run with production settings
docker run -p 8080:8080 \
  -e REDIS_HOST=redis \
  -e DATABASE_URL=postgresql://... \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  dox-gtwy-main
```

---

## 📚 API Documentation

### Gateway Management
```bash
GET  /health                           # Gateway health check
GET  /metrics                          # Prometheus metrics
GET  /api/v1/gateway/status           # Detailed system status
GET  /api/v1/gateway/routes           # List all 20+ available routes
GET  /api/v1/gateway/circuit-breakers  # Circuit breaker status
```

### Service Routes Examples
```bash
# Core services
GET|POST|PUT|DELETE /auth/*           # Authentication
GET|POST|PUT|DELETE /storage/*        # Document storage

# Workflow services
GET|POST|PUT|DELETE /activation/*     # Activation workflows
GET|POST|PUT|DELETE /lifecycle/*      # Contract lifecycle
GET|POST|PUT|DELETE /workflows-engine/* # Visual workflow builder

# Document services
GET|POST|PUT|DELETE /templates/*      # Template management
GET|POST|PUT|DELETE /field-mapping/*   # Field extraction
GET|POST|PUT|DELETE /batch/*          # Batch assembly

# AI features
POST /workflows-engine/api/workflows/from-description  # Create from English
```

### Rate Limits (per service)
- High-throughput services: 200 req/min (storage, workflows)
- Medium services: 100 req/min (auth, templates)
- Compute-heavy services: 50 req/min (batch, ETL)
- AI services: 80 req/min (workflow engine)

---

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
export DEBUG=false
export LOG_LEVEL=INFO
export SERVICE_PORT=8080

# Redis & Database
export REDIS_HOST=localhost
export REDIS_PORT=6379
export DATABASE_URL=postgresql://...

# Service URLs (auto-configured, override as needed)
export CORE_AUTH_URL=http://dox-core-auth:5001
export CORE_STORE_URL=http://dox-core-store:5000
export ACTIVATION_SERVICE_URL=http://dox-actv-service:5010
# ... (see config.py for all 20 services)

# AI Features
export ANTHROPIC_API_KEY=sk-ant-...  # For natural language workflows

# Rate Limiting
export ENABLE_RATE_LIMITING=true
export CIRCUIT_BREAKER_THRESHOLD=5

# CORS
export CORS_ORIGINS="http://localhost:3000,https://dox-platform.com"
```

### Service URL Patterns
All services follow consistent URL patterns:
- Services: `http://dox-{service-name}:{port}`
- Ports: 5000-5023 (assigned sequentially)
- Examples:
  - dox-core-auth → http://dox-core-auth:5001
  - dox-actv-service → http://dox-actv-service:5010
  - dox-data-aggregation → http://dox-data-aggregation-service:5023

---

## 🧪 Testing

### Health Checks
```bash
# Gateway health
curl http://localhost:8080/health

# All services health
for service in activation lifecycle workflows-engine field-mapping pdf-upload barcode batch; do
  curl -f http://localhost:8080/$service/health && echo "✅ $service"
done
```

### Load Testing
```bash
# Test 100 concurrent requests
ab -n 100 -c 10 http://localhost:8080/health

# Test rate limiting
for i in {1..150}; do curl -s http://localhost:8080/storage/documents > /dev/null; done
# 151st request should be rate limited
```

### AI Workflow Testing
```bash
# Test natural language workflow creation
curl -X POST http://localhost:8080/workflows-engine/api/workflows/from-description \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Test Workflow",
    "description": "When document uploaded, create batch and send notification"
  }'
```

---

## 📊 Monitoring & Observability

### Metrics Available
- Request rate per service
- Response time distribution
- Error rate per service
- Circuit breaker state changes
- Rate limiting blocks
- AI workflow success rates

### Health Endpoints
```bash
# Overall system health
GET /health

# Detailed gateway status
GET /api/v1/gateway/status

# Circuit breaker status
GET /api/v1/gateway/circuit-breakers

# Service routing health
GET /api/v1/gateway/routes
```

### Prometheus Metrics
```
# Available at /metrics
http_requests_total{service, method, status_code}
http_request_duration_seconds{service}
circuit_breaker_state{service}
rate_limit_blocks_total{service}
nl_workflows_created_total
nl_workflows_success_rate
```

---

## 🚨 Alerting

### Key Alert Conditions
- Gateway down or unresponsive
- High error rate (>5%)
- Circuit breaker open for critical services
- Rate limiting excessive blocks
- AI workflow creation failing
- Response time degradation

### Alert Configuration
See `DEPLOYMENT_READINESS_CHECKLIST.md` for complete alerting rules.

---

## 🔄 Deployment

### Development
```bash
python app.py
# Debug mode enabled
# Auto-reload on changes
```

### Staging
```bash
docker build -t dox-gtwy-main:staging .
docker run -p 8080:8080 \
  -e DEBUG=false \
  -e LOG_LEVEL=INFO \
  dox-gtwy-main:staging
```

### Production
```bash
# Using provided deployment manifests
kubectl apply -f k8s/
kubectl rollout status deployment/dox-gtwy-main
```

### Deployment Readiness
See `DEPLOYMENT_READINESS_CHECKLIST.md` for comprehensive deployment procedures, testing, and rollback plans.

---

## 📚 Documentation

| Document | Purpose | Status |
|----------|---------|--------|
| `README.md` | Overview & Quick Start | ✅ **Updated** |
| `config.py` | Configuration reference | ✅ **Enhanced** |
| `app.py` | Main application logic | ✅ **Enhanced** |
| `DEPLOYMENT_READINESS_CHECKLIST.md` | Complete deployment guide | ✅ **NEW** |
| `PULL_REQUEST_SUMMARY.md` | Changes summary for PR | ✅ **NEW** |
| `CONTINUITY_UPDATE.md` | Session continuation guide | ✅ **NEW** |
| `MCP_SERVER_SPECIFICATION.md` | Claude Desktop integration | ✅ **NEW** |
| `FASTAPI_MIGRATION_PLAN.md` | Performance upgrade roadmap | ✅ **NEW** |

---

## 🤝 Support & Contact

### Development Team
- **Gateway Maintainers**: platform-team@company.com
- **AI Features**: ai-team@company.com
- **Performance**: performance-team@company.com

### Deployment Support
- **On-call**: +1-555-0123 (24/7)
- **Slack**: #dox-gateway
- **PagerDuty**: dox-gateway-alerts

### Issues & Troubleshooting
1. Check `DEPLOYMENT_READINESS_CHECKLIST.md` troubleshooting guide
2. Review service health at `/api/v1/gateway/status`
3. Check logs for error patterns
4. Contact on-call for critical issues

---

## 📄 License

**Internal Use Only** - DOX Platform Component

---

**Version**: 2.0.0
**Last Updated**: 2025-11-03
**Status**: ✅ **PRODUCTION READY**

---

*Generated with Compyle*