# Azure Infrastructure Setup Guide

**Purpose**: Deploy cloud resources needed for dox services to run
**Timeline**: 1 week (3 days setup + 2 days configuration + 2 days testing)
**Cost**: $300-500/month for dev/staging environment

---

## Prerequisites

You need:
- Azure subscription with billing enabled
- Azure CLI installed (`az --version` to check)
- GitHub credentials for automation

### Install Azure CLI

```bash
# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify
az --version
```

### Authenticate

```bash
az login
# Opens browser for authentication

# Verify access
az account show
```

---

## Phase 1: Setup (Day 1-3)

### 1.1 Create Resource Group

```bash
# Variables
RESOURCE_GROUP="dox-prod"
LOCATION="eastus"

# Create resource group
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

# Verify
az group show --name "$RESOURCE_GROUP"
```

### 1.2 Deploy MSSQL Database

```bash
# Variables
SQL_SERVER="dox-sql-server-$(date +%s)"
SQL_ADMIN_USER="doxadmin"
SQL_ADMIN_PASSWORD="$(openssl rand -base64 32)"
DB_NAME="dox_main_db"

echo "SQL Server: $SQL_SERVER"
echo "Admin User: $SQL_ADMIN_USER"
echo "Password: $SQL_ADMIN_PASSWORD"  # SAVE THIS!

# Create SQL Server
az sql server create \
  --name "$SQL_SERVER" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --admin-user "$SQL_ADMIN_USER" \
  --admin-password "$SQL_ADMIN_PASSWORD"

# Create database
az sql db create \
  --resource-group "$RESOURCE_GROUP" \
  --server "$SQL_SERVER" \
  --name "$DB_NAME" \
  --tier Standard \
  --compute-model Serverless \
  --max-size 32GB

# Allow Azure services
az sql server firewall-rule create \
  --resource-group "$RESOURCE_GROUP" \
  --server "$SQL_SERVER" \
  --name "AllowAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### 1.3 Deploy Redis Cache

```bash
# Variables
REDIS_NAME="dox-redis-$(date +%s)"
REDIS_SKU="Standard"
REDIS_FAMILY="C"
REDIS_CAPACITY="1"

# Create Redis cache
az redis create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REDIS_NAME" \
  --location "$LOCATION" \
  --sku "$REDIS_SKU" \
  --vm-size "$REDIS_FAMILY$REDIS_CAPACITY"

# Get connection string
REDIS_CONNECTION=$(az redis show-connection-string \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "connectionStrings.primaryConnectionString" \
  --output tsv)

echo "Redis Connection: $REDIS_CONNECTION"  # SAVE THIS!
```

### 1.4 Create Azure Storage Account

```bash
# Variables
STORAGE_ACCOUNT="doxstorage$(date +%s | tail -c 5)"
CONTAINER_NAME="pdf-templates"

# Create storage account
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2

# Get storage connection string
STORAGE_CONNECTION=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query "connectionString" \
  --output tsv)

echo "Storage Connection: $STORAGE_CONNECTION"  # SAVE THIS!

# Create container
az storage container create \
  --name "$CONTAINER_NAME" \
  --account-name "$STORAGE_ACCOUNT"
```

---

## Phase 2: Configuration (Day 4-5)

### 2.1 Get Connection Strings

Save these for your .env file:

```bash
# SQL Server connection string
SQL_CONNECTION_STRING="mssql+pyodbc://${SQL_ADMIN_USER}:${SQL_ADMIN_PASSWORD}@${SQL_SERVER}.database.windows.net/${DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"

# Redis connection string (from above)
REDIS_URL="$REDIS_CONNECTION"

# Azure Storage connection string (from above)
AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION"
```

### 2.2 Create .env File

```bash
# Navigate to repository
cd /workspace/cmhiuvaf601cjpsimd1muwhd7/dox-admin

# Create .env template
cat > ../.env.production << 'EOF'
# =======================
# AZURE INFRASTRUCTURE
# =======================

# MSSQL Database
DATABASE_URL=mssql+pyodbc://YOUR_SQL_ADMIN:YOUR_PASSWORD@your-sql-server.database.windows.net/dox_main_db?driver=ODBC+Driver+17+for+SQL+Server

# Redis Cache
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@your-redis-name.redis.cache.windows.net:6379/0

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_STORAGE;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=pdf-templates

# =======================
# APPLICATION SETTINGS
# =======================

# JWT Settings (keep these secure!)
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Settings
API_TITLE=Dox Template Service
API_VERSION=1.0.0
DEBUG=false

# File Upload Settings
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=application/pdf

# =======================
# LOGGING
# =======================
LOG_LEVEL=INFO
EOF

echo "Created .env.production template"
```

### 2.3 Test Connections

```bash
# Install connection tools
pip install pyodbc sqlalchemy psutil

# Test SQL connection
python3 << 'PYTHON'
from sqlalchemy import create_engine, text

db_url = "YOUR_DATABASE_URL"  # Replace with actual URL
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ SQL Server connection successful!")
except Exception as e:
    print(f"❌ SQL Server connection failed: {e}")
PYTHON

# Test Redis connection
python3 << 'PYTHON'
import redis

redis_url = "YOUR_REDIS_URL"  # Replace with actual URL
try:
    r = redis.from_url(redis_url)
    r.ping()
    print("✅ Redis connection successful!")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
PYTHON

# Test Azure Storage
python3 << 'PYTHON'
from azure.storage.blob import BlobServiceClient

connection_str = "YOUR_STORAGE_CONNECTION_STRING"  # Replace
try:
    client = BlobServiceClient.from_connection_string(connection_str)
    properties = client.get_account_information()
    print("✅ Azure Storage connection successful!")
except Exception as e:
    print(f"❌ Azure Storage connection failed: {e}")
PYTHON
```

---

## Phase 3: Database Schema (Day 5-6)

### 3.1 Create Database Tables

Navigate to dox-tmpl-pdf-upload and run migrations:

```bash
cd /workspace/cmhiuvaf601cjpsimd1muwhd7/dox-tmpl-pdf-upload

# Install alembic if not already installed
pip install alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration to Azure
export DATABASE_URL="YOUR_AZURE_CONNECTION_STRING"
alembic upgrade head

# Verify tables created
python3 << 'PYTHON'
from sqlalchemy import create_engine, inspect

engine = create_engine("YOUR_DATABASE_URL")
inspector = inspect(engine)

print("Tables created:")
for table_name in inspector.get_table_names():
    print(f"  ✅ {table_name}")
PYTHON
```

### 3.2 Verify Schema

```bash
# Connect to Azure SQL and verify
az sql db execute \
  --resource-group "dox-prod" \
  --server "YOUR_SQL_SERVER" \
  --name "dox_main_db" \
  --username "doxadmin" \
  --password "YOUR_PASSWORD" \
  --query-text "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo';"
```

---

## Phase 4: Security Configuration

### 4.1 Configure Firewall

```bash
# Allow your local IP
YOUR_IP=$(curl -s https://checkip.amazonaws.com)

az sql server firewall-rule create \
  --resource-group "dox-prod" \
  --server "YOUR_SQL_SERVER" \
  --name "AllowLocalDev" \
  --start-ip-address "$YOUR_IP" \
  --end-ip-address "$YOUR_IP"

# For CI/CD (allow GitHub Actions)
az sql server firewall-rule create \
  --resource-group "dox-prod" \
  --server "YOUR_SQL_SERVER" \
  --name "AllowGitHubActions" \
  --start-ip-address "140.82.112.0" \
  --end-ip-address "140.82.113.255"
```

### 4.2 Store Secrets

```bash
# Store in GitHub Secrets (for CI/CD later)
# Go to: https://github.com/uberpu-ntiva/dox-admin/settings/secrets

# Add these secrets:
# AZURE_SQL_CONNECTION_STRING
# REDIS_URL
# AZURE_STORAGE_CONNECTION_STRING
# JWT_SECRET_KEY
```

---

## Phase 5: Testing (Day 6-7)

### 5.1 Local Connection Test

```bash
# From dox-tmpl-pdf-upload
export DATABASE_URL="YOUR_AZURE_CONNECTION_STRING"
export REDIS_URL="YOUR_REDIS_URL"
export AZURE_STORAGE_CONNECTION_STRING="YOUR_STORAGE_CONNECTION_STRING"

# Start services
docker-compose up

# In another terminal, test endpoints
curl http://localhost:8000/api/v1/health

# Should return:
# {
#   "status": "healthy",
#   "database": "connected",
#   "storage": "connected",
#   "cache": "connected"
# }
```

### 5.2 API Testing

```bash
# Get health details
curl http://localhost:8000/api/v1/health/detailed

# Should show all services connected to Azure
```

---

## Cleanup

To delete all resources and stop incurring costs:

```bash
# Delete resource group (deletes everything)
az group delete --name "dox-prod"

# Confirm deletion
az group show --name "dox-prod" 2>&1 | grep -q "does not exist" && echo "✅ Deleted"
```

---

## Troubleshooting

### Issue: Connection timeout to SQL Server
**Cause**: Firewall rule not configured
**Solution**: Add your IP to firewall rules (see Phase 4.1)

### Issue: Redis SSL error
**Cause**: Connection string format issue
**Solution**: Use `rediss://` (with 's') for SSL connections

### Issue: Azure Storage authentication failed
**Cause**: Connection string is invalid or expired
**Solution**: Regenerate connection string from Azure portal

### Issue: Database migration fails
**Cause**: ODBC driver not installed
**Solution**: Install SQL Server ODBC driver

---

**Status**: ✅ Complete
**Next**: Start implementing dox-core-auth stub service
**Time**: ~1 week of work