# Pact Platform: DEPLOYMENT STANDARDS

**Docker, Azure, AWS Deployment Patterns and Best Practices**

**Last Updated**: 2025-10-31
**Owner**: DevOps/Infrastructure Team
**Status**: ACTIVE

---

## Quick Reference

**Production Deployment Options**:
- **Primary**: Azure App Service (easiest)
- **Alternative**: AWS ECS Fargate (more control)
- **Both**: Supported (multi-cloud strategy)

**Development**: Docker Compose locally

---

## Docker Standards

### Dockerfile Best Practices

**Multi-Stage Builds** (Required for all services):

```dockerfile
# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build
COPY app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    [minimal-runtime-deps] \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY app/ .

# Security: Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check (required)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

**Optimization Checklist**:
- [ ] Use multi-stage builds (reduce final image size)
- [ ] Use slim base images (not alpine for Python - compatibility issues)
- [ ] Non-root user (security)
- [ ] Health check endpoint (mandatory)
- [ ] .dockerignore file (skip unnecessary files)
- [ ] --no-cache-dir on pip (reduce layer size)
- [ ] rm -rf /var/lib/apt/lists/* (clean package manager cache)
- [ ] EXPOSE port (documentation)

### Container Image Naming

**Format**: `[registry]/[service-name]:[version]`

**Examples**:
- `pactregistry.azurecr.io/dox-core-store:1.0.0`
- `pactregistry.azurecr.io/dox-core-store:latest`
- `123456789012.dkr.ecr.us-east-1.amazonaws.com/dox-core-store:1.0.0`

### Building & Pushing

```bash
# Build locally
docker build -t [registry]/[service]:1.0.0 .
docker tag [registry]/[service]:1.0.0 [registry]/[service]:latest

# Push to registry
docker push [registry]/[service]:1.0.0
docker push [registry]/[service]:latest

# Using Makefile (recommended)
make build        # Build image
make push         # Push to registry
```

---

## Azure Deployment

### Azure App Service

**Best for**: Most Pact Platform services (simple, managed, good performance)

**Setup**:

```bash
# 1. Create resource group
az group create --name pact-rg --location eastus

# 2. Create App Service plan
az appservice plan create \
  --name pact-plan \
  --resource-group pact-rg \
  --sku B2 \
  --is-linux

# 3. Create web app
az webapp create \
  --resource-group pact-rg \
  --plan pact-plan \
  --name dox-core-store \
  --deployment-container-image-name [registry]/dox-core-store:latest

# 4. Configure container registry
az webapp config container set \
  --name dox-core-store \
  --resource-group pact-rg \
  --docker-custom-image-name [registry]/dox-core-store:latest \
  --docker-registry-server-url https://[registry] \
  --docker-registry-server-user [username] \
  --docker-registry-server-password [password]

# 5. Configure environment variables
az webapp config appsettings set \
  --resource-group pact-rg \
  --name dox-core-store \
  --settings FLASK_ENV=production DATABASE_URL=... LOG_LEVEL=INFO

# 6. Deploy
az webapp deployment container config \
  --name dox-core-store \
  --resource-group pact-rg \
  --enable-cd

# 7. Enable continuous deployment (auto-redeploy on image push)
az webapp deployment container config \
  --name dox-core-store \
  --resource-group pact-rg \
  --enable-cd
```

### Azure Container Registry (ACR)

**Primary Docker registry** for Pact Platform

```bash
# 1. Create registry
az acr create --resource-group pact-rg --name pactregistry --sku Basic

# 2. Build and push directly from ACR
az acr build --registry pactregistry --image dox-core-store:1.0.0 .

# 3. List images
az acr repository list --name pactregistry

# 4. Enable admin user for pushing
az acr update -n pactregistry --admin-enabled true

# 5. Get credentials
az acr credential show --name pactregistry
```

### Azure Database for SQL Server

**For**: dox-core-store service

```bash
# 1. Create MSSQL server
az sql server create \
  --resource-group pact-rg \
  --name pact-sqlserver \
  --admin-user pactadmin \
  --admin-password [strong-password]

# 2. Create database
az sql db create \
  --resource-group pact-rg \
  --server pact-sqlserver \
  --name pact_production

# 3. Configure firewall
az sql server firewall-rule create \
  --resource-group pact-rg \
  --server pact-sqlserver \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# 4. Get connection string
# Format: mssql+pyodbc://user:password@server.database.windows.net/database?driver=ODBC+Driver+17+for+SQL+Server
```

### Azure Key Vault

**For**: Secrets management

```bash
# 1. Create vault
az keyvault create --resource-group pact-rg --name pact-vault

# 2. Add secrets
az keyvault secret set --vault-name pact-vault --name DatabasePassword --value [password]
az keyvault secret set --vault-name pact-vault --name JwtSecret --value [secret]

# 3. Grant App Service access
az keyvault set-policy \
  --name pact-vault \
  --object-id [app-service-object-id] \
  --secret-permissions get list
```

---

## AWS Deployment

### AWS ECS Fargate

**Best for**: Services requiring custom scaling or cost optimization

**Setup**:

```bash
# 1. Create ECS cluster
aws ecs create-cluster --cluster-name pact-cluster --region us-east-1

# 2. Create task definition (JSON file)
cat > task-definition.json << 'EOF'
{
  "family": "dox-core-store",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "dox-core-store",
      "image": "[account-id].dkr.ecr.us-east-1.amazonaws.com/dox-core-store:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "FLASK_ENV", "value": "production" },
        { "name": "LOG_LEVEL", "value": "INFO" }
      ],
      "secrets": [
        { "name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:region:account:parameter/database-url" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dox-core-store",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 5
      }
    }
  ]
}
EOF

# 3. Register task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region us-east-1

# 4. Create service
aws ecs create-service \
  --cluster pact-cluster \
  --service-name dox-core-store \
  --task-definition dox-core-store:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}" \
  --region us-east-1

# 5. Deploy update
aws ecs update-service \
  --cluster pact-cluster \
  --service dox-core-store \
  --force-new-deployment \
  --region us-east-1
```

### AWS ECR (Elastic Container Registry)

**For**: Docker image registry

```bash
# 1. Create repository
aws ecr create-repository --repository-name dox-core-store --region us-east-1

# 2. Push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [account-id].dkr.ecr.us-east-1.amazonaws.com

docker tag dox-core-store:latest [account-id].dkr.ecr.us-east-1.amazonaws.com/dox-core-store:latest
docker push [account-id].dkr.ecr.us-east-1.amazonaws.com/dox-core-store:latest
```

### AWS RDS for SQL Server/PostgreSQL

**For**: Database

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier pact-database \
  --db-instance-class db.t3.micro \
  --engine sqlserver-ex \
  --master-username pactadmin \
  --master-user-password [password] \
  --allocated-storage 20 \
  --region us-east-1
```

### AWS Secrets Manager

**For**: Secrets management

```bash
# Store secret
aws secretsmanager create-secret \
  --name pact/database-url \
  --secret-string "mssql://..." \
  --region us-east-1

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id pact/database-url \
  --region us-east-1
```

---

## Environment Configuration

### Environment Variables

**All services must support environment variables** (12-factor app):

```bash
# Required
FLASK_ENV=production              # development|production
LOG_LEVEL=INFO                    # DEBUG|INFO|WARNING|ERROR

# Service-specific
DATABASE_URL=postgresql://...     # Database connection
JWT_SECRET=...                    # JWT signing secret
AZURE_CONNECTION_STRING=...       # Azure Files
SITE_ID=tenant-1                  # Multi-tenancy

# Optional
PORT=5000                         # Override default port
DEBUG=False                       # Debug mode
WORKER_COUNT=4                    # Gunicorn workers
```

### Configuration File Pattern

**Use environment variables + .env file for development**:

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DATABASE_URL = os.getenv('DATABASE_URL')
    JWT_SECRET = os.getenv('JWT_SECRET')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# app.py
from config import Config
app.config.from_object(Config)
```

### .env File Example

```bash
# .env (development only, git-ignored)
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/pact
LOG_LEVEL=DEBUG
```

---

## Monitoring & Logging

### Health Check Endpoint (Mandatory)

**All services must implement**:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "service": "dox-core-store",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }, 200
```

**Used by**: Docker health checks, load balancers, monitoring systems

### Structured Logging

**Use JSON logging for production**:

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "dox-core-store"
        }
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_object)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
```

### Azure Application Insights

```python
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Add Azure logging
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = os.getenv('APPINSIGHTS_KEY')
middleware = FlaskMiddleware(app)

handler = AzureLogHandler()
logging.getLogger().addHandler(handler)
```

---

## Scaling

### Horizontal Scaling

**Azure App Service**:
```bash
az appservice plan update \
  --name pact-plan \
  --resource-group pact-rg \
  --number-of-workers 3
```

**AWS ECS**:
```bash
aws ecs update-service \
  --cluster pact-cluster \
  --service dox-core-store \
  --desired-count 3
```

### Auto-Scaling

**Azure**:
```bash
az monitor metrics alert create \
  --name high-cpu \
  --resource-group pact-rg \
  --scopes [app-service-id] \
  --condition "avg Percentage CPU > 80 over 5m"
```

---

## Disaster Recovery

### Database Backups

**Azure SQL**:
```bash
az sql db restore \
  --resource-group pact-rg \
  --server pact-sqlserver \
  --name pact-production-restored \
  --from-name pact-production \
  --point-in-time "2025-10-30T12:00:00Z"
```

**AWS RDS**:
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier pact-restored \
  --db-snapshot-identifier pact-snapshot \
  --region us-east-1
```

### Container Image Tagging

**Always tag production images with version + latest**:
```bash
docker tag dox-core-store:1.0.0 registry/dox-core-store:latest
docker push registry/dox-core-store:1.0.0
docker push registry/dox-core-store:latest
```

---

## Rollback Procedure

### Azure App Service

```bash
# Swap deployment slots
az webapp deployment slot swap \
  --resource-group pact-rg \
  --name dox-core-store \
  --slot staging
```

### AWS ECS

```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster pact-cluster \
  --service dox-core-store \
  --task-definition dox-core-store:2 \  # Previous version
  --force-new-deployment
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`make test`)
- [ ] Docker image builds (`make build`)
- [ ] Health check endpoint working
- [ ] Environment variables documented
- [ ] Database migrations applied
- [ ] Logging configured
- [ ] Security scans passed
- [ ] Load tests passed
- [ ] Monitoring/alerting configured
- [ ] Rollback plan documented
- [ ] Team informed of deployment
- [ ] Deployment window scheduled

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-10-31
**Version**: 1.0

