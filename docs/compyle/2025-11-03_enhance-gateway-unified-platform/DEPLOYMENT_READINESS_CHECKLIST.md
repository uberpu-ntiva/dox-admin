# DOX Platform Deployment Readiness Checklist

**Date:** 2025-11-03
**Repository:** dox-gtwy-main
**Branch:** compyle/enhance-gateway-unified-platform
**Target:** main

---

## ✅ PRE-DEPLOYMENT VALIDATION

### Code Quality Check
- [x] **Syntax Validated** - All Python files parse correctly
- [x] **Imports Checked** - All required packages available
- [x] **Type Safety** - Proper type annotations where critical
- [x] **Error Handling** - Comprehensive try/catch blocks
- [x] **Logging** - Appropriate logging throughout
- [x] **Configuration** - All settings via environment variables

### Functionality Testing
- [x] **Gateway Routes** - All 20 service routes implemented
- [x] **Circuit Breakers** - Fault tolerance for all services
- [x] **Rate Limiting** - Per-service limits configured
- [x] **Authentication** - Middleware applied to protected routes
- [x] **NL Workflows** - Claude API integration implemented
- [x] **Graceful Degradation** - Fallbacks for missing API keys

### Security Review
- [x] **No Secrets in Code** - No hardcoded passwords/tokens
- [x] **Environment Variables** - All sensitive data via env vars
- [x] **Input Validation** - Pydantic models for request validation
- [x] **Error Messages** - No sensitive info in error responses
- [x] **CORS Configuration** - Proper origins configured

### Documentation Review
- [x] **API Documentation** - All new endpoints documented
- [x] **Deployment Guide** - Step-by-step procedures
- [x] **Environment Variables** - Complete list provided
- [x] **Troubleshooting** - Common issues and solutions
- [x] **Rollback Plan** - Clear recovery procedures

---

## 🚀 DEPLOYMENT PROCEDURES

### Environment Variables Required

**Critical Variables:**
```bash
# Redis Configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0

# Database Configuration
export DATABASE_URL=postgresql://user:pass@localhost/dox_gateway

# Service Configuration
export DEBUG=false
export LOG_LEVEL=INFO
export SECRET_KEY=your-secret-key

# NEW: For Natural Language Workflows
export ANTHROPIC_API_KEY=sk-ant-xxx
```

**Optional Variables (auto-configured with defaults):**
```bash
# All 20 service URLs automatically use localhost:port pattern
# Override as needed for your environment:
export CORE_AUTH_URL=http://dox-core-auth:5001
export ACTIVATION_SERVICE_URL=http://dox-actv-service:5010
export WORKFLOW_ENGINE_URL=http://dox-auto-workflow-engine:5013
# ... etc (see config.py for complete list)
```

### Step-by-Step Deployment

#### Phase 1: Pre-Deployment Checks (5 minutes)

```bash
# 1. Verify you're on correct branch
cd /workspace/cmhhwyhw102vzojio3tbkco6u/dox-gtwy-main
git status
# Should show: On branch compyle/enhance-gateway-unified-platform

# 2. Verify all changes committed
git log --oneline -5
# Should show recent commits for gateway enhancement

# 3. Test local configuration
python -c "from config import GatewayConfig; GatewayConfig.validate()"
# Should return: True (no validation errors)

# 4. Test imports
python -c "import app; print('✅ All imports successful')"
# Should show: ✅ All imports successful
```

#### Phase 2: Build & Deploy (15 minutes)

```bash
# 1. Build Docker image
docker build -t dox-gtwy-main:v2 .

# 2. Tag for deployment
docker tag dox-gtwy-main:v2 your-registry/dox-gtwy-main:v2

# 3. Push to registry
docker push your-registry/dox-gtwy-main:v2

# 4. Update Kubernetes deployment
kubectl set image deployment/dox-gtwy-main \
  dox-gtwy-main=your-registry/dox-gtwy-main:v2

# 5. Wait for rollout
kubectl rollout status deployment/dox-gtwy-main --timeout=300s
```

#### Phase 3: Post-Deployment Verification (10 minutes)

```bash
# 1. Health check
curl -f http://your-gateway-url/health
# Should return: {"status": "healthy", ...}

# 2. Test new routes (sample)
for route in activation lifecycle workflows-engine field-mapping pdf-upload barcode batch; do
  echo "Testing /$route/health"
  curl -f http://your-gateway-url/$route/health || echo "❌ FAILED: $route"
done

# 3. Test circuit breakers
curl -s http://your-gateway-url/api/v1/gateway/status | jq '.circuit_breakers'
# Should show all circuit breakers: {"state": "closed", ...}

# 4. Test NL workflows (if API key set)
if [ -n "$ANTHROPIC_API_KEY" ]; then
  curl -X POST http://your-gateway-url/workflows-engine/api/workflows/from-description \
    -H "Content-Type: application/json" \
    -d '{"description": "Test workflow: when document uploaded, send notification"}'
  # Should return: {"workflow_id": "...", "status": "created"}
fi
```

---

## 🔍 POST-DEPLOYMENT TESTING

### Smoke Tests (Automated)

```bash
#!/bin/bash
# smoke_tests.sh

GATEWAY_URL="http://your-gateway-url"
FAILED_TESTS=()

echo "🔍 Running smoke tests..."

# Test 1: Basic health
echo "Test 1: Gateway health check"
if ! curl -sf "$GATEWAY_URL/health" > /dev/null; then
  FAILED_TESTS+=("Gateway health check failed")
fi

# Test 2: All new routes reachable
echo "Test 2: New routes reachability"
ROUTES="activation activation-events lifecycle workflows-engine field-mapping pdf-upload barcode batch pact-upload rtns-upload esig-webhooks data-etl data-distrib data-aggregation"
for route in $ROUTES; do
  if ! curl -sf "$GATEWAY_URL/$route/health" > /dev/null 2>&1; then
    FAILED_TESTS+=("Route /$route/health failed")
  fi
done

# Test 3: Circuit breakers
echo "Test 3: Circuit breaker status"
CB_STATUS=$(curl -s "$GATEWAY_URL/api/v1/gateway/status" | jq -r '.circuit_breakers | keys | length')
if [ "$CB_STATUS" -lt 20 ]; then
  FAILED_TESTS+=("Circuit breakers not fully initialized: $CB_STATUS/20")
fi

# Results
if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
  echo "✅ All smoke tests passed"
  exit 0
else
  echo "❌ Smoke tests failed:"
  for test in "${FAILED_TESTS[@]}"; do
    echo "  - $test"
  done
  exit 1
fi
```

### Integration Tests

```bash
# Test gateway → service integration
echo "🔍 Testing service integration..."

# Test authentication flow
AUTH_TOKEN=$(curl -s -X POST "$GATEWAY_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.token')

# Test protected route with auth
curl -H "Authorization: Bearer $AUTH_TOKEN" \
  "$GATEWAY_URL/storage/documents" \
  | jq -r '.success'  # Should return "true"

# Test rate limiting
for i in {1..150}; do
  curl -s "$GATEWAY_URL/storage/documents" > /dev/null
done
# 151st request should be rate limited
curl -s "$GATEWAY_URL/storage/documents" | jq -r '.error'  # Should show rate limit error
```

### Performance Tests

```bash
# Load test new routes
echo "🔍 Performance testing..."

# Test 100 concurrent requests to activation endpoint
ab -n 100 -c 10 "$GATEWAY_URL/activation/health"

# Test 100 concurrent requests to workflow endpoint
ab -n 100 -c 10 "$GATEWAY_URL/workflows-engine/health"

# Expected: <500ms response time, 95% success rate
```

---

## 📊 MONITORING & OBSERVABILITY

### Key Metrics to Monitor

**Gateway Metrics:**
- Request rate per service
- Response time distribution
- Error rate per service
- Circuit breaker state changes
- Rate limiting blocks

**NL Workflow Metrics:**
- Workflow creation success rate
- Claude API response time
- Parsing error rate
- Workflow execution success rate

**System Metrics:**
- Memory usage
- CPU usage
- Redis connection health
- Database query performance

### Alerting Rules

```yaml
# Prometheus alerts for deployment
groups:
  - name: dox-gateway-alerts
    rules:
      - alert: GatewayDown
        expr: up{job="dox-gtwy-main"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "DOX Gateway is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in gateway"

      - alert: CircuitBreakerOpen
        expr: circuit_breaker_state == 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker open for service"

      - alert: NLWorkflowFailed
        expr: nl_workflow_success_rate < 0.95
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Natural language workflow creation failing"
```

### Log Monitoring

```bash
# Key log patterns to watch
echo "🔍 Monitoring key log patterns..."

# Check for authentication errors
kubectl logs deployment/dox-gtwy-main | grep "AUTH_ERROR" | tail -10

# Check for circuit breaker activations
kubectl logs deployment/dox-gtwy-main | grep "CIRCUIT_BREAKER" | tail -10

# Check for NL workflow issues
kubectl logs deployment/dox-gtwy-main | grep "NL_WORKFLOW" | tail -10

# Check for service timeouts
kubectl logs deployment/dox-gtwy-main | grep "SERVICE_TIMEOUT" | tail -10
```

---

## 🔄 ROLLBACK PROCEDURES

### Quick Rollback (5 minutes)

```bash
# 1. Check current deployment
kubectl get deployment dox-gtwy-main -o wide
kubectl rollout history deployment/dox-gtwy-main

# 2. Rollback to previous version
kubectl rollout undo deployment/dox-gtwy-main

# 3. Wait for rollback completion
kubectl rollout status deployment/dox-gtwy-main --timeout=300s

# 4. Verify rollback
curl -f http://your-gateway-url/health
```

### Full Rollback (10 minutes)

```bash
# 1. Scale to zero (emergency stop)
kubectl scale deployment dox-gtwy-main --replicas=0

# 2. Deploy previous known-good image
kubectl set image deployment/dox-gtwy-main \
  dox-gtwy-main=your-registry/dox-gtwy-main:v1

# 3. Scale back up
kubectl scale deployment dox-gtwy-main --replicas=3

# 4. Verify everything works
kubectl rollout status deployment/dox-gtwy-main
```

### Rollback Validation

```bash
# After rollback, run smoke tests again
./smoke_tests.sh

# Verify old behavior works
curl -s http://your-gateway-url/api/v1/gateway/routes | jq '.total'
# Should show original route count (6 instead of 20)
```

---

## 📋 FINAL DEPLOYMENT CHECKLIST

### Pre-Deploy
- [ ] Environment variables set
- [ ] Docker image built successfully
- [ ] Configuration validated
- [ ] Backup current deployment
- [ ] Notify stakeholders

### Deploy
- [ ] Deploy to staging first
- [ ] Run all tests on staging
- [ ] Get stakeholder approval
- [ ] Deploy to production
- [ ] Monitor rollout progress

### Post-Deploy
- [ ] Run smoke tests
- [ ] Verify all new routes working
- [ ] Check monitoring dashboards
- [ ] Alert teams of deployment
- [ ] Document deployment results

### 24-Hour Monitoring
- [ ] Monitor error rates
- [ ] Watch performance metrics
- [ ] Check user feedback
- [ ] Prepare rollback if needed
- [ ] Document lessons learned

---

## 🆘 TROUBLESHOOTING GUIDE

### Common Issues & Solutions

**Issue: Service Not Reachable**
```bash
# Check service status
kubectl get pods -l app=dox-gtwy-main

# Check logs for errors
kubectl logs deployment/dox-gtwy-main --tail=50

# Check if target service is running
curl -s http://dox-actv-service:5010/health || echo "Service down"
```

**Issue: Circuit Breaker Open**
```bash
# Check circuit breaker status
curl -s http://your-gateway-url/api/v1/gateway/status | jq '.circuit_breakers'

# Manually reset (if needed)
curl -X POST http://your-gateway-url/api/v1/gateway/reset-circuit-breakers
```

**Issue: NL Workflow Fails**
```bash
# Check API key
echo $ANTHROPIC_API_KEY | cut -c1-10

# Test Claude API directly
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

**Issue: High Memory Usage**
```bash
# Check memory usage
kubectl top pods -l app=dox-gtwy-main

# Check memory leaks
kubectl logs deployment/dox-gtwy-main | grep "Memory" | tail -10

# Restart if needed
kubectl rollout restart deployment/dox-gtwy-main
```

### Contact Information

**For Deployment Issues:**
- Platform Team: platform@company.com
- On-call Engineer: +1-555-0123
- Slack: #dox-deployments

**For Post-Deploy Issues:**
- Development Team: dev@company.com
- Service Owner: dox-gateway-team@company.com

---

## ✅ DEPLOYMENT READY STATUS

| Area | Status | Notes |
|------|--------|-------|
| Code Quality | ✅ Ready | All files validated |
| Testing | ✅ Ready | Comprehensive test suite |
| Documentation | ✅ Ready | Complete guides provided |
| Environment | ✅ Ready | All variables documented |
| Monitoring | ✅ Ready | Alerting rules configured |
| Rollback | ✅ Ready | Quick procedures in place |
| Team Notification | ⏳ Pending | Send deployment notice |

**Overall Status:** ✅ **READY FOR DEPLOYMENT**

---

**Deployment Command:**
```bash
# When ready to deploy:
git checkout compyle/enhance-gateway-unified-platform
kubectl apply -f k8s/gateway-deployment.yaml
kubectl rollout status deployment/dox-gtwy-main
```

**Verification Command:**
```bash
# After deployment:
curl -f http://your-gateway-url/health && \
./smoke_tests.sh && \
echo "✅ Deployment successful!"
```

---

*Generated with Compyle*