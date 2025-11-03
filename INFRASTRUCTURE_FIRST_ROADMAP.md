# Infrastructure-First Implementation Roadmap

**Duration**: 2-3 weeks
**Approach**: Option 3 - Get real infrastructure working, then iterate

---

## Overview

This roadmap guides you through deploying real Azure infrastructure and creating a minimal auth service stub. After this, the services can run with persistent data and real cloud resources.

```
Week 1: Infrastructure Setup
  ├─ Deploy MSSQL database
  ├─ Deploy Redis cache
  ├─ Deploy Azure Storage
  └─ Configure connections

Week 2: Minimal Auth Service
  ├─ Implement dox-core-auth (JWT only)
  ├─ Deploy to Docker
  └─ Test with dox-tmpl-pdf-upload

Week 3: Integration Testing
  ├─ Test database operations
  ├─ Test file uploads to Azure
  ├─ Test auth flow end-to-end
  └─ Document findings
```

---

## What You Get After This

✅ Real MSSQL database (persistent data)
✅ Real Redis cache (rate limiting works)
✅ Real Azure Storage (file uploads work)
✅ Real JWT authentication (tokens work)
✅ All services connectable (actual integration)
❌ Still no comprehensive testing
❌ Still no CI/CD automation
❌ Still no full user management

---

## Week 1: Infrastructure Setup

### Prerequisites

1. **Azure Subscription**
   - Sign up at https://azure.microsoft.com/en-us/free/
   - Verify billing is enabled

2. **Install Azure CLI**
   ```bash
   # macOS
   brew install azure-cli

   # Linux
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

   # Verify
   az --version
   ```

3. **Authenticate**
   ```bash
   az login
   # Opens browser for authentication
   ```

### Day 1-2: Deploy Core Infrastructure

**Commands**:
```bash
# Create resource group
az group create --name dox-prod --location eastus

# Deploy MSSQL database
SQL_SERVER="dox-sql-server-$(date +%s)"
az sql server create --name "$SQL_SERVER" --resource-group dox-prod --admin-user doxadmin --admin-password "YourPassword123!"

az sql db create --name dox_main_db --resource-group dox-prod --server "$SQL_SERVER" --edition Standard

# Deploy Redis cache
REDIS_NAME="dox-redis-$(date +%s)"
az redis create --name "$REDIS_NAME" --resource-group dox-prod --location eastus --sku Standard --vm-size C1

# Create Azure Storage
STORAGE_ACCOUNT="doxstorage$(date +%s | tail -c 5)"
az storage account create --name "$STORAGE_ACCOUNT" --resource-group dox-prod --location eastus --sku Standard_LRS

az storage container create --name pdf-templates --account-name "$STORAGE_ACCOUNT"
```

### Day 3-4: Configuration

1. **Get connection strings**
2. **Test all connections**
3. **Create .env files**
4. **Apply database schema**

### Day 5: Verify Infrastructure

Test all resources are running and accessible.

---

## Week 2: Minimal Auth Service

### What We're Building

**dox-core-auth** service with:
- ✅ JWT token generation and validation
- ✅ Hardcoded demo users (admin, user1, user2)
- ✅ Token expiry and validation
- ⚠️ No user registration (hardcoded only)
- ⚠️ No OAuth (upgrade to full service later)

### Day 6-7: Implementation

1. Create service structure
2. Implement JWT logic
3. Add Docker configuration
4. Test locally

### Day 8: Integration

1. Test with dox-tmpl-pdf-upload
2. Verify token flow
3. Debug any issues

---

## Week 3: Integration Testing

### Day 9-10: Database Testing

```bash
# Test database connections
python -c "
from sqlalchemy import create_engine
engine = create_engine('YOUR_DATABASE_URL')
engine.execute('SELECT 1')
print('✅ Database connected')
"

# Test table creation
alembic upgrade head
```

### Day 11: File Upload Testing

```bash
# Test upload with real Azure Storage
curl -X POST http://localhost:8000/api/v1/templates/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# Verify in Azure
az storage blob list --container-name pdf-templates
```

### Day 12-13: End-to-End Testing

1. Test complete workflow
2. Performance baseline
3. Documentation

### Day 14: Review and Cleanup

1. Final verification
2. Update documentation
3. Prepare for next phase

---

## Success Criteria

You'll know it's working when:

✅ All Azure resources deployed
✅ Database stores data persistently
✅ Files upload to Azure Storage
✅ Authentication tokens work
✅ Rate limiting functions with Redis
✅ Services restart and maintain data

---

## Cost Estimate

| Resource | Cost/Month |
|----------|-----------|
| MSSQL Database | $15-30 |
| Redis Cache | $30-50 |
| Azure Storage | $2-5 |
| **Total** | **$50-85/month** |

---

## Next Steps After Week 3

1. Add comprehensive testing
2. Implement full user management
3. Set up CI/CD pipelines
4. Scale to production

---

**Status**: Ready to start
**Timeline**: 2-3 weeks
**Next Action**: Deploy Azure infrastructure (Week 1)