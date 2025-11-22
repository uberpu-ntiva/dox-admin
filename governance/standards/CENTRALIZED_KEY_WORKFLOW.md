# Centralized Key Storage: Complete Workflow Steps

**Purpose**: Step-by-step guide showing exactly how the centralized key management system works.

---

## Overview

```
SETUP PHASE                    RUNTIME PHASE                  MAINTENANCE PHASE
┌──────────────────┐          ┌──────────────────┐           ┌──────────────────┐
│ 1. Setup         │          │ 2. Service       │           │ 3. Operations    │
│    dox-core-store│ ──────→ │    Onboarding    │ ────────→ │    & Rotation    │
└──────────────────┘          └──────────────────┘           └──────────────────┘
      Week 1                      Week 2-3                        Ongoing
```

---

## PHASE 1: Initial Setup (Week 1)

### Step 1.1: Deploy dox-core-store Service

**What happens**:
```bash
# Infrastructure team deploys the service
git clone https://github.com/pact-platform/dox-core-store.git
cd dox-core-store

# Configure production environment
cp config/production.yml.example config/production.yml
# Edit with production values:
# - Vault endpoint and token
# - PostgreSQL connection string
# - Redis cluster connection
# - JWT secret
```

**Verification**:
```bash
# Start the service
docker-compose up -d

# Verify it's running
curl https://keys.pact-platform.com/health

# Expected response:
{
  "status": "healthy",
  "checks": {
    "vault": "healthy",
    "redis": "healthy",
    "postgres": "healthy",
    "jwt_signing": "healthy"
  }
}
```

### Step 1.2: Initialize Vault

**What happens**:
```bash
# Security team initializes Vault
vault auth enable jwt
vault write auth/jwt/config \
  bound_issuer="https://keys.pact-platform.com" \
  user_claim="service_name"

# Create policy for dox-core-store
vault policy write dox-core-store - <<EOF
path "secret/data/*" {
  capabilities = ["read", "list"]
}
path "secret/metadata/*" {
  capabilities = ["read", "list"]
}
EOF
```

### Step 1.3: Store Initial Keys

**What happens**:
```bash
# Infrastructure/Security team stores all production keys
vault kv put secret/service_keys/jules_api/production \
  value="AQ.Ab8RN6IjejxlqvM0TAGt5bhWZeMJf9PFwuKBs-dqj9rARpcOPA"

vault kv put secret/database_connections/postgres_main \
  value="postgresql://user:pass@postgres.internal:5432/pact"

vault kv put secret/external_apis/google_services/maps_api \
  value="AIzaSy..."

# Verify keys are stored
vault kv list secret/service_keys/
vault kv list secret/database_connections/
```

### Step 1.4: Set Up Monitoring

**What happens**:
```bash
# Prometheus starts scraping metrics
# Update prometheus.yml
scrape_configs:
  - job_name: 'dox-core-store'
    static_configs:
      - targets: ['https://keys.pact-platform.com:9090/metrics']

# Grafana dashboard created
# Alerts configured for:
# - Vault connectivity
# - High latency
# - Failed key access attempts
# - Rate limit violations
```

**Dashboard shows**:
- Key request rate (per service)
- Cache hit ratio
- Vault access latency
- Failed authentication attempts
- Active services

### Step 1.5: Set Up Audit Log Retention

**What happens**:
```sql
-- Configure PostgreSQL audit log cleanup
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
BEGIN
  DELETE FROM key_access_audit
  WHERE timestamp < NOW() - INTERVAL '90 days';

  DELETE FROM service_auth_audit
  WHERE timestamp < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Run nightly
SELECT cron.schedule('cleanup-audit-logs', '0 2 * * *', 'SELECT cleanup_old_audit_logs()');
```

---

## PHASE 2: Service Onboarding (Week 2-3)

### Step 2.1: Register Service (Example: jules-mcp)

**Actor**: Platform administrator

**What happens**:

```bash
# Step A: Generate admin token (one-time setup)
ADMIN_TOKEN=$(curl -X POST "https://keys.pact-platform.com/auth/admin-token" \
  -H "Authorization: Bearer BOOTSTRAP_TOKEN" \
  -d '{"expires_in": 3600}' \
  | jq -r '.token')

# Step B: Register the service
curl -X POST "https://keys.pact-platform.com/services/register" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jules-mcp",
    "description": "Jules AI MCP server for code generation",
    "environment": "production",
    "rate_limit_requests": 60,
    "rate_limit_window": 60000,
    "permissions": [
      "service_keys.jules_api.production",
      "database_connections.postgres_main",
      "external_apis.google_services.oauth_client_id"
    ]
  }'

# Response:
{
  "service_id": "uuid-...",
  "name": "jules-mcp",
  "status": "registered",
  "permissions_count": 3,
  "message": "Service registered successfully"
}
```

### Step 2.2: Generate Service Token

**Actor**: Platform administrator or CI/CD pipeline

**What happens**:

```bash
# Generate JWT token for the service (valid for 1 year)
SERVICE_TOKEN=$(curl -X POST "https://keys.pact-platform.com/auth/service-token" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "service_name": "jules-mcp",
    "expires_in": 31536000
  }' \
  | jq -r '.token')

# Token contains:
# {
#   "service_name": "jules-mcp",
#   "permissions": ["service_keys.jules_api.production", ...],
#   "environment": "production",
#   "active": true,
#   "iat": 1699089600,
#   "exp": 1730625600
# }

echo "Token: $SERVICE_TOKEN"
```

### Step 2.3: Store Service Token in Deployment

**Actor**: DevOps/Deployment team

**What happens**:

```bash
# Option A: Kubernetes Secret
kubectl create secret generic jules-mcp-keys \
  --from-literal=SERVICE_TOKEN="$SERVICE_TOKEN" \
  --namespace=production

# Option B: Environment variable in CI/CD
# In GitHub Actions or GitLab CI:
# Set SECRET: SERVICE_TOKEN in repository secrets

# Option C: Docker environment
# Create .env file (never commit to git):
# SERVICE_TOKEN=eyJhbGciOiJSUzI1NiIs...
```

### Step 2.4: Update Service Code

**Actor**: Development team (Claude instructs Jules)

**What happens**:

```typescript
// OLD CODE (julius-mcp before migration)
import * as dotenv from 'dotenv';
dotenv.config();

const julesApiKey = process.env.JULES_API_KEY;  // From .env file
const dbUrl = process.env.DATABASE_URL;

// NEW CODE (After migration)
import { KeyClient } from 'dox-core-store-client';

const keyClient = new KeyClient({
  serviceToken: process.env.SERVICE_TOKEN,  // From secret/env
  keyServiceUrl: process.env.KEY_SERVICE_URL,  // https://keys.pact-platform.com
  cacheTtl: 3600  // 1 hour cache
});

// Initialize on startup
async function initialize() {
  // Get Jules API key
  const julesApiKey = await keyClient.getKey(
    'service_keys.jules_api.production'
  );

  // Get database URL
  const dbUrl = await keyClient.getKey(
    'database_connections.postgres_main'
  );

  // Keys are cached for 1 hour automatically
  return { julesApiKey, dbUrl };
}
```

### Step 2.5: Test Key Access

**Actor**: Development team

**What happens**:

```bash
# Development testing
export SERVICE_TOKEN="dev-token-..."
export KEY_SERVICE_URL="https://keys-staging.pact-platform.com"

npm test  # Tests pass with correct keys

# Expected test output:
# ✓ Can retrieve Jules API key
# ✓ Can retrieve database URL
# ✓ Keys are cached
# ✓ Cache respects TTL
# ✓ Failed auth returns 401
```

### Step 2.6: Deploy to Staging

**Actor**: CI/CD pipeline

**What happens**:

```bash
# Deploy to staging environment
git push origin feature/centralized-keys

# GitHub Actions workflow:
# 1. Runs tests
# 2. Builds docker image
# 3. Pushes to staging registry
# 4. Deploys to staging kubernetes cluster
# 5. Injects SERVICE_TOKEN secret
# 6. Health checks pass

# Audit log shows:
{
  "timestamp": "2025-11-04T14:30:00Z",
  "service_name": "jules-mcp",
  "key_path": "service_keys.jules_api.production",
  "action": "GET",
  "status": "GRANTED",
  "environment": "staging",
  "cached": false
}
```

### Step 2.7: Verify in Staging

**Actor**: QA/Testing team

**What happens**:

```bash
# Test that service works with centralized keys
curl -X POST https://staging-api.pact-platform.com/v1/task \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test Jules with centralized keys",
    "source": "sources/github/test/repo"
  }'

# Expected response:
{
  "session_id": "session-abc123",
  "status": "created",
  "message": "Successfully created worker with centralized key management"
}

# Audit log shows successful key access in staging
```

---

## PHASE 3: Runtime - Key Access (Ongoing)

### Step 3.1: Service Starts

**What happens** (at pod/container startup):

```typescript
// service.ts
import { KeyClient } from 'dox-core-store-client';

async function startService() {
  console.log('Initializing Jules MCP service...');

  // 1. Create key client
  const keyClient = new KeyClient({
    serviceToken: process.env.SERVICE_TOKEN,
    keyServiceUrl: process.env.KEY_SERVICE_URL,
    cacheTtl: 3600
  });

  // 2. Validate authentication
  try {
    await keyClient.validateAuth();
    console.log('✓ Service authenticated successfully');
  } catch (error) {
    console.error('✗ Authentication failed:', error.message);
    process.exit(1);
  }

  // 3. Initialize key cache
  const keys = await keyClient.getKeys([
    'service_keys.julius_api.production',
    'database_connections.postgres_main'
  ]);
  console.log('✓ Keys loaded and cached');

  // 4. Start server
  startMCPServer(keys);
  console.log('✓ Jules MCP service ready');
}

startService();
```

**Backend flow**:

```
1. Service sends:
   POST /keys/batch
   Authorization: Bearer SERVICE_TOKEN
   Body: {
     key_paths: [
       "service_keys.julius_api.production",
       "database_connections.postgres_main"
     ],
     cache_ttl: 3600
   }

2. dox-core-store:
   a) Validates JWT token
      └─ Checks signature
      └─ Checks expiration
      └─ Checks service is active
   b) Verifies permissions
      └─ "julius-mcp" has permission for these keys
   c) Checks rate limits
      └─ Service hasn't exceeded 60 requests/min
   d) Retrieves from Vault
      └─ Reads secrets from Vault
   e) Caches in Redis
      └─ Sets TTL to 3600 seconds
   f) Logs access
      └─ Records in PostgreSQL audit table

3. Service receives:
   {
     "keys": [
       {
         "key_path": "service_keys.julius_api.production",
         "value": "AQ.Ab8RN6IjejxlqvM0...",
         "cached": false,
         "expires_at": "2025-11-04T15:30:00Z"
       },
       {
         "key_path": "database_connections.postgres_main",
         "value": "postgresql://...",
         "cached": false,
         "expires_at": "2025-11-04T15:30:00Z"
       }
     ]
   }
```

### Step 3.2: Service Uses Keys

**What happens** (during operation):

```python
# service.py - Using cached keys

class JulesMCPService:
    def __init__(self, key_client):
        self.key_client = key_client
        self.keys_cache = {}

    async def create_worker(self, task_description):
        # Get Jules API key (from cache, already loaded)
        jules_key = await self.key_client.get_key(
            'service_keys.julius_api.production'
        )

        # Get database URL (from cache)
        db_url = await self.key_client.get_key(
            'database_connections.postgres_main'
        )

        # Use keys to call Jules API
        response = await self.call_jules_api(
            api_key=jules_key,
            task=task_description
        )

        # Use DB URL to save result
        await self.save_to_database(
            db_url=db_url,
            result=response
        )

        return response

# Behind the scenes:
# 1st call to get_key() - Cache HIT (returns in 1ms)
# 2nd call to get_key() - Cache HIT (returns in 1ms)
# After 3600 seconds - Cache MISS, fetches from Vault (50-100ms)
```

### Step 3.3: Concurrent Requests

**What happens** (during high load):

```
Request 1 (from Pod A):
  GET /keys/get?path=service_keys.julius_api.production
  ├─ Auth check: 5ms
  ├─ Redis cache check: 1ms (HIT!)
  └─ Response: 10ms total

Request 2 (from Pod B):
  GET /keys/get?path=database_connections.postgres_main
  ├─ Auth check: 5ms
  ├─ Redis cache check: 1ms (HIT!)
  └─ Response: 10ms total

Request 3 (from Pod C):
  GET /keys/get?path=service_keys.julius_api.production
  ├─ Auth check: 5ms
  ├─ Redis cache check: 1ms (HIT!)
  └─ Response: 10ms total

All 3 requests complete in parallel: ~10ms each
```

**Audit log shows**:
```json
[
  {
    "timestamp": "2025-11-04T14:45:00.001Z",
    "service_name": "julius-mcp",
    "key_path": "service_keys.julius_api.production",
    "action": "GET",
    "status": "GRANTED",
    "cached": true,
    "request_id": "req-pod-a-001"
  },
  {
    "timestamp": "2025-11-04T14:45:00.002Z",
    "service_name": "julius-mcp",
    "key_path": "database_connections.postgres_main",
    "action": "GET",
    "status": "GRANTED",
    "cached": true,
    "request_id": "req-pod-b-001"
  },
  {
    "timestamp": "2025-11-04T14:45:00.003Z",
    "service_name": "julius-mcp",
    "key_path": "service_keys.julius_api.production",
    "action": "GET",
    "status": "GRANTED",
    "cached": true,
    "request_id": "req-pod-c-001"
  }
]
```

---

## PHASE 4: Key Rotation (Quarterly)

### Step 4.1: Plan Rotation

**What happens** (2 weeks before rotation):

```bash
# Security team notification sent
Subject: "Q4 2025 Key Rotation Starting"

Plan:
├─ Week 1: Rotate Jules API keys
├─ Week 2: Rotate database passwords
├─ Week 3: Rotate external API keys
└─ Week 4: Verify and finalize
```

### Step 4.2: Generate New Key

**What happens** (Week 1):

```bash
# Security team generates new Jules API key from Google Console
NEW_JULES_KEY="AQ.NewKey123456789xyz..."

# Store new key with version suffix
vault kv put secret/service_keys/julius_api/production \
  value="$NEW_JULIUS_KEY" \
  version="2" \
  created_at="2025-11-04" \
  rotation_reason="quarterly_rotation"

# Mark old key as deprecated but keep for grace period
vault kv put secret/service_keys/julius_api/deprecated \
  value="AQ.Ab8RN6IjejxlqvM0..." \
  version="1"

echo "New key stored. Grace period: 7 days"
```

### Step 4.3: Update Services (Zero-downtime)

**What happens** (automatically due to caching):

```
Timeline:
Day 1 - Key rotated in Vault
  ├─ Old key still used by services (from 1-hour cache)
  └─ New key available in Vault

Day 1 - Cache expiration starts
  ├─ Service A cache expires → Fetches new key
  ├─ Service B cache expires → Fetches new key
  └─ Service C cache expires → Fetches new key

Result: Zero service downtime!
```

**No deployment needed because**:
- Services don't restart
- Keys are fetched from cache first
- When cache expires, new key is fetched automatically
- Grace period allows any failed requests to retry

### Step 4.4: Verify Rotation

**What happens** (after 7 days):

```bash
# Check audit logs
curl "https://keys.pact-platform.com/audit/logs?days=7" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | jq '.audit_logs | group_by(.key_path) | map({
      key_path: .[0].key_path,
      total_accesses: length,
      last_access: max_by(.timestamp).timestamp
    })'

# Output:
{
  "key_path": "service_keys.julius_api.production",
  "total_accesses": 15420,
  "last_access": "2025-11-04T14:59:59Z"
}

# All services using new key ✓
```

### Step 4.5: Remove Old Key

**What happens** (after 7-day grace period):

```bash
# Remove old deprecated key from Vault
vault kv delete secret/service_keys/julius_api/deprecated

# Archive to audit log for compliance
curl -X POST "https://keys.pact-platform.com/audit/archive" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "key_path": "service_keys.julius_api.production",
    "old_version": "1",
    "reason": "Quarterly rotation completed"
  }'

echo "Key rotation complete and verified"
```

---

## PHASE 5: Failure & Recovery

### Step 5.1: Service Requests Key, Cache Expired, Vault Down

**What happens** (degraded but safe):

```
Timeline:
1. Service requests key
   ├─ Cache HIT? NO (expired)
   ├─ Check Vault? ERROR (Vault down)
   └─ Result: CACHE_FALLBACK

2. Behavior options (configured):
   a) Use last cached value (if not too stale)
   b) Return error with retry advice
   c) Use hardcoded fallback (if available)

3. Audit log:
   {
     "timestamp": "2025-11-04T15:00:00Z",
     "service_name": "julius-mcp",
     "action": "GET",
     "status": "FALLBACK_CACHE",
     "cache_age_seconds": 3650,
     "error": "Vault unavailable",
     "fallback_used": true
   }

4. Alert: "Vault down, using fallback cache"
```

### Step 5.2: Rate Limit Exceeded

**What happens** (service making too many requests):

```
Timeline:
1. Service makes 61st request in 60 seconds
2. Rate limiter detects violation
3. Request rejected with 429 status

Response:
{
  "error": "Rate limit exceeded",
  "service": "julius-mcp",
  "limit": 60,
  "window_seconds": 60,
  "retry_after": 45,
  "current_usage": 61
}

Audit log:
{
  "timestamp": "2025-11-04T15:00:00Z",
  "service_name": "julius-mcp",
  "action": "GET",
  "status": "RATE_LIMITED",
  "current_usage": 61,
  "limit": 60
}

Alert: "julius-mcp exceeding rate limit"
```

### Step 5.3: Key Compromise Detected

**What happens** (emergency):

```bash
# Step 1: Alert sent immediately
Subject: "SECURITY ALERT: Possible Key Compromise"

# Step 2: Immediate actions
vault kv patch secret/service_keys/julius_api/production \
  compromised=true \
  compromised_at="2025-11-04T15:00:00Z"

# Step 3: Notify all services
POST /services/notify-key-change
  Body: {
    "key_path": "service_keys.julius_api.production",
    "action": "key_compromised",
    "urgency": "critical",
    "affected_services": ["julius-mcp", "webapp", "...]
  }

# Step 4: Audit every access with the old key
SELECT * FROM key_access_audit
WHERE key_path = 'service_keys.julius_api.production'
  AND timestamp > '2025-11-04T10:00:00Z'
ORDER BY timestamp DESC;

# Step 5: Generate new key immediately (no waiting)
vault kv put secret/service_keys/julius_api/production \
  value="$EMERGENCY_NEW_KEY" \
  rotation_reason="SECURITY_COMPROMISE"
```

---

## Complete End-to-End Example

### Scenario: Deploy new version of jules-mcp to production

```
┌─────────────────────────────────────────────────────────────┐
│ Complete Flow: Code → Deploy → Run → Access Keys            │
└─────────────────────────────────────────────────────────────┘

STEP 1: Development
┌────────────────────────────────┐
│ Claude writes planning.md       │
│ Jules implements with key       │
│ migration instructions          │
│ Jules creates code that uses    │
│ KeyClient to fetch keys         │
└─────────────┬──────────────────┘
              │
STEP 2: Build & Push
┌────────────────────────────────┐
│ git push origin feature/...     │
│ GitHub Actions CI/CD runs:      │
│  1. npm run tests               │
│  2. npm run build               │
│  3. docker build ...            │
│  4. docker push gcr.io/...      │
└─────────────┬──────────────────┘
              │
STEP 3: Deploy to Production
┌────────────────────────────────┐
│ kubectl apply -f deployment.yml │
│ Kubernetes:                     │
│  1. Creates pod                 │
│  2. Injects SERVICE_TOKEN       │
│  3. Sets env variables          │
│  4. Starts container            │
└─────────────┬──────────────────┘
              │
STEP 4: Service Startup
┌────────────────────────────────┐
│ Container starts, logs show:    │
│ "Initializing Jules MCP..."     │
│ KeyClient validates token       │
│ ✓ Authentication OK             │
│ Fetches keys batch:             │
│  - service_keys.julius_api...   │
│  - database_connections...      │
│ ✓ Keys loaded and cached        │
│ ✓ Jules MCP ready               │
└─────────────┬──────────────────┘
              │
STEP 5: Request Arrives
┌────────────────────────────────┐
│ User calls Claude to create     │
│ work for Jules                  │
│ Claude creates Jules worker:    │
│ POST /v1/tasks                  │
│   task_description: "..."       │
│   source: "sources/github/..."  │
└─────────────┬──────────────────┘
              │
STEP 6: Jules Uses Keys
┌────────────────────────────────┐
│ Jules MCP service:              │
│  1. Gets Jules API key (cached) │
│  2. Calls Jules API             │
│  3. Gets DB URL (cached)        │
│  4. Stores result in database   │
│ ✓ Request processed            │
│ Response sent to Claude         │
└─────────────┬──────────────────┘
              │
STEP 7: Audit Trail Complete
┌────────────────────────────────┐
│ Audit log shows:                │
│ - 14:45:00 - Auth OK            │
│ - 14:45:01 - Key1 fetched       │
│ - 14:45:01 - Key2 fetched       │
│ - 14:45:02 - Keys used          │
│ - 14:45:05 - Complete           │
│ ✓ Full traceability             │
└────────────────────────────────┘
```

---

## Quick Reference: What Changed for Services

### Before (Scattered Keys)
```bash
# .env file (NEVER commit this!)
JULIUS_API_KEY=AQ.Ab8RN6IjejxlqvM0...
DATABASE_URL=postgresql://...
STRIPE_KEY=sk_live_...

# service.ts
const key = process.env.JULIUS_API_KEY;
```

### After (Centralized Keys)
```bash
# Only this in environment (can commit if encrypted)
SERVICE_TOKEN=eyJhbGciOiJSUzI1NiIs...
KEY_SERVICE_URL=https://keys.pact-platform.com

# service.ts
const keyClient = new KeyClient();
const key = await keyClient.getKey('service_keys.julius_api.production');
```

### Benefits
- ✅ **Secure**: Keys not in code/env files
- ✅ **Audited**: Every access logged
- ✅ **Rotated**: Change once, all services benefit
- ✅ **Monitored**: Central dashboard for all keys
- ✅ **Compliant**: HIPAA, SOC2, PCI-DSS ready

---

**Status**: 📋 WORKFLOW COMPLETE
**Ready**: For implementation starting with Phase 1 setup

