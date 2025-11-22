# Centralized Key Storage & Exposure Standards

**Status**: ✅ ACTIVE
**Last Updated**: 2025-11-04
**Owner**: Platform Security Team
**Applies To**: All Pact Platform services and projects

---

## Purpose

This document defines the centralized approach for storing, managing, and exposing API keys, secrets, and authentication credentials across the entire Pact Platform. Eliminates scattered key management and provides a single, secure point of exposure.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Centralized Key Management                │
│                      (Single Point of Truth)                 │
├─────────────────────────────────────────────────────────────┤
│  Vault/Secrets Manager (HashiCorp Vault / AWS Secrets)     │
│  ├─ Service Keys                                            │
│  ├─ API Credentials                                         │
│  ├─ Database Connections                                    │
│  └─ External Service Tokens                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
              ┌───────┴───────┐
              │  Exposure    │
              │  Service     │
              │ (dox-core-store) │
              └───────┬───────┘
                      │
            ┌─────────┴─────────┐
            │   All Services    │
            │  (jules-mcp,       │
            │   dox-gtwy-main,   │
            │   etc.)           │
            └───────────────────┘
```

---

## Centralized Storage Components

### 1. **Key Vault Service** (`dox-core-store`)

**Primary responsibility**: Secure storage and retrieval of all secrets.

**Stored Keys Categories**:
```yaml
service_keys:
  jules_api:                    # Jules API keys
    production: "AQ.Ab8RN6IjejxlqvM0..."
    staging: "AQ.StagingKey123..."
    development: "AQ.DevKey456..."

  external_apis:
    google_services:
      maps_api: "AIzaSy..."
      oauth_client_id: "...-.apps.googleusercontent.com"
    payment_gateways:
      stripe_secret_key: "sk_live_..."
      paypal_client_secret: "..."

  database_connections:
    postgres_main: "postgresql://..."
    redis_cache: "redis://..."

  third_party_integrations:
    aws_access_key: "AKIAIOSFODNN7EXAMPLE"
    aws_secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    slack_bot_token: "xoxb-..."
```

### 2. **Exposure Service** (Part of `dox-core-store`)

**Purpose**: Provide secure, audited access to keys for services.

**Features**:
- **Service Authentication**: JWT-based auth for service-to-service
- **Key Scoping**: Services only get keys they need
- **Audit Logging**: Every key access logged
- **Rate Limiting**: Prevent key abuse
- **Rotation Support**: Seamless key rotation

---

## Service Integration Pattern

### For Services Using Keys (All Services)

```python
# Example: jules-mcp service accessing Jules API key
from dox_core_store import KeyClient

class JulesMCPService:
    def __init__(self):
        # Authenticate service with JWT
        self.key_client = KeyClient(
            service_name="jules-mcp",
            service_token=os.getenv("SERVICE_TOKEN")
        )

    async def get_jules_api_key(self):
        """Get Jules API key with automatic caching"""
        key = await self.key_client.get_key(
            key_path="service_keys.jules_api.production",
            cache_ttl=3600  # Cache for 1 hour
        )
        return key.value

# Usage
jules_service = JulesMCPService()
jules_api_key = await jules_service.get_jules_api_key()
```

### Environment Variables (Minimal)

```bash
# Each service only needs these base env vars
SERVICE_TOKEN="eyJhbGciOiJSUzI1NiIs..."  # Service JWT token
KEY_SERVICE_URL="https://keys.pact-platform.com"
KEY_SERVICE_TIMEOUT=5000

# NO API keys in .env files anymore!
```

---

## Key Categories & Standards

### 1. **Jules AI Keys**
```yaml
service_keys.jules_api:
  environment: "production"
  usage: "Google Jules API access for code generation"
  rotation_policy: "quarterly"
  access_level: "service_only"
  services_with_access: ["jules-mcp"]
```

### 2. **External API Keys**
```yaml
external_apis:
  google_services:
    usage: "Google Maps, OAuth, etc."
    rotation_policy: "as_needed"
    rate_limiting: "enforced"

  payment_gateways:
    usage: "Stripe, PayPal integrations"
    rotation_policy: "annually"
    pci_compliance: "required"
```

### 3. **Database Credentials**
```yaml
database_connections:
  rotation_policy: "monthly"
  connection_pooling: "required"
  ssl_required: "true"
  audit_access: "true"
```

### 4. **Third-Party Integrations**
```yaml
third_party_integrations:
  aws:
    iam_roles_preferred: "true"
    session_duration: "1h"
    audit_cloudtrail: "required"
```

---

## Security Standards

### 1. **Access Control**

```python
# Key access validation
class KeyAccessValidator:
    async def validate_access(self, service_name: str, key_path: str):
        # Check if service has permission
        if not await self.has_permission(service_name, key_path):
            raise UnauthorizedError(
                f"Service {service_name} not authorized for {key_path}"
            )

        # Check rate limits
        if await self.exceeds_rate_limit(service_name):
            raise RateLimitError("Too many key requests")

        # Log access attempt
        await self.log_access(service_name, key_path, "GRANTED")
```

### 2. **Audit Requirements**

```python
# Every key access is logged
{
    "timestamp": "2025-11-04T13:30:00Z",
    "service_name": "jules-mcp",
    "key_path": "service_keys.jules_api.production",
    "action": "GET",
    "status": "GRANTED",
    "request_id": "req_abc123",
    "ip_address": "10.0.1.100",
    "user_agent": "dox-core-store/1.0"
}
```

### 3. **Rotation & Lifecycle**

```yaml
key_lifecycle:
  creation:
    requires_approval: "security_team_lead"
    expiration: "90_days_auto"

  rotation:
    policy: "quarterly_critical"
    notification: "7_days_before"
    downtime: "zero_downtime"

  revocation:
    immediate: "on_compromise"
    scheduled: "on_service_decommission"
```

---

## Implementation Guide

### For New Services

1. **Service Registration**:
```python
# Register service with key management
await key_service.register_service(
    service_name="new-service-name",
    description="Service for X functionality",
    required_keys=[
        "database_connections.postgres_main",
        "external_apis.google_services.maps_api"
    ]
)
```

2. **Service Token Generation**:
```bash
# Generate service JWT token
curl -X POST "https://keys.pact-platform.com/tokens" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"service_name": "new-service-name", "expires_in": "1y"}'
```

3. **Key Access Implementation**:
```python
# In your service code
class NewService:
    def __init__(self):
        self.key_client = KeyClient(
            service_name="new-service-name",
            service_token=os.getenv("SERVICE_TOKEN")
        )

    async def initialize(self):
        # Get all required keys
        self.db_url = await self.key_client.get_key("database_connections.postgres_main")
        self.google_key = await self.key_client.get_key("external_apis.google_services.maps_api")
```

### For Existing Services

**Migration Steps**:

1. **Identify Current Keys**:
```bash
# Find all keys in environment files
grep -r "API_KEY\|SECRET\|TOKEN" . --include="*.env*" --include="*.env"
```

2. **Move to Central Storage**:
```python
# Script to migrate keys to central storage
async def migrate_service_keys(service_name: str):
    keys_found = extract_keys_from_env_files()

    for key_name, key_value in keys_found.items():
        await key_service.store_key(
            key_path=f"{service_name}.{key_name}",
            value=key_value,
            environment="production"
        )
```

3. **Update Service Code**:
```python
# Replace direct env access with key client
# OLD:
# api_key = os.getenv("JULES_API_KEY")

# NEW:
# api_key = await key_client.get_key("service_keys.jules_api.production")
```

---

## Jules AI Integration Updates

### Updated Jules Standards

**Reference**: `/dox-admin/governance/standards/JULES_AI_STANDARDS.md`

**Security Requirements (Updated)**:
- ✅ **No hardcoded secrets** - Use centralized key storage
- ✅ **Service authentication** - Use service JWT tokens
- ✅ **Key access patterns** - Follow centralized storage pattern
- ✅ **Audit compliance** - All key access is logged

### Jules Task Template (Updated)

```python
task_description = """
Implement user authentication

## Security Requirements (Updated)
- Use centralized key storage for all secrets
- No API keys in environment files
- Access keys via dox-core-store key client
- Follow key access pattern from CENTRALIZED_KEY_STORAGE.md

## Key Access Pattern
```python
from dox_core_store import KeyClient

key_client = KeyClient(
    service_name="your-service",
    service_token=os.getenv("SERVICE_TOKEN")
)

# Get Jules API key
jules_key = await key_client.get_key("service_keys.jules_api.production")
```

## Reference Documents
- CENTRALIZED_KEY_STORAGE.md: Key management standards
- JULES_AI_STANDARDS.md: Complete standards
- planning.md: Feature specifications
"""
```

---

## Benefits of Centralization

### 1. **Security Improvements**
- ✅ **Single audit point** - All key access in one place
- ✅ **Reduced exposure** - Keys not scattered in env files
- ✅ **Better rotation** - Automated key lifecycle management
- ✅ **Access control** - Service-based permissions
- ✅ **Zero-touch deployment** - No keys in code repositories

### 2. **Operational Benefits**
- ✅ **Easier rotation** - Update once, all services benefit
- ✅ **Central monitoring** - One dashboard for all key health
- ✅ **Consistent patterns** - Same key access across all services
- ✅ **Automated compliance** - Built-in audit and security checks

### 3. **Development Benefits**
- ✅ **Simplified setup** - Services need only SERVICE_TOKEN
- ✅ **Consistent patterns** - Same key access everywhere
- ✅ **Better developer experience** - No need to manage multiple env files
- ✅ **Environment consistency** - Same key access across dev/staging/prod

---

## Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- [x] Create key storage service in `dox-core-store`
- [x] Define centralized standards document
- [x] Create key management API
- [ ] Set up Vault/Secrets Manager

### Phase 2: Migration (Week 3-4)
- [ ] Migrate `jules-mcp` keys to central storage
- [ ] Update `jules-mcp` to use key client
- [ ] Test key access patterns
- [ ] Verify audit logging works

### Phase 3: Expansion (Week 5-8)
- [ ] Migrate all other services
- [ ] Remove hardcoded keys from all repos
- [ ] Set up automated key rotation
- [ ] Implement monitoring and alerts

### Phase 4: Optimization (Week 9-12)
- [ ] Performance optimization
- [ ] Advanced features (key versioning, rollbacks)
- [ ] Security hardening
- [ ] Documentation and training

---

## Migration Checklist

### For Each Service
- [ ] Identify all keys/secrets in use
- [ ] Register service with key management
- [ ] Move keys to central storage
- [ ] Update service code to use key client
- [ ] Test with staging environment
- [ ] Deploy to production
- [ ] Remove keys from environment files
- [ ] Verify audit logging works

### Security Validation
- [ ] No keys in source code
- [ ] No keys in environment files
- [ ] Service authentication working
- [ ] Key access logged
- [ ] Rate limiting enforced
- [ ] Audit trail complete

---

## Key Access API Reference

### Get Key
```python
# Get single key
key = await key_client.get_key("service_keys.jules_api.production")

# Get multiple keys
keys = await key_client.get_keys([
    "service_keys.jules_api.production",
    "database_connections.postgres_main"
])
```

### Cache Management
```python
# Get with caching
key = await key_client.get_key(
    "service_keys.jules_api.production",
    cache_ttl=3600  # Cache for 1 hour
)

# Clear cache
await key_client.clear_cache("service_keys.jules_api.production")
```

### Health Check
```python
# Verify key service is accessible
health = await key_client.health_check()
if not health.is_healthy:
    # Handle key service outage
    pass
```

---

**Status**: ✅ ACTIVE
**Next Review**: 2025-12-04
**Migration Timeline**: 12 weeks total
**Security Approval**: Required from Security Team

---

## Emergency Procedures

### Key Compromise
1. **Immediate**: Revoke affected key
2. **Within 1 hour**: Rotate to new key
3. **Within 24 hours**: Audit all access since compromise
4. **Within 48 hours**: Security review and process improvement

### Key Service Outage
1. **Immediate**: Switch to cached keys (1 hour cache)
2. **Within 30 minutes**: Restart service with manual fallback
3. **Within 2 hours**: Resolve outage
4. **Post-mortem**: Document and improve resilience

