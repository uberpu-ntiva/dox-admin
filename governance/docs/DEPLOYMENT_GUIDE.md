# DOX Workflow Engine Deployment Guide

Complete deployment guide for the DOX workflow rules coordination system.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Deployment Options](#deployment-options)
5. [Quick Start](#quick-start)
6. [Production Deployment](#production-deployment)
7. [Configuration](#configuration)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Overview

The DOX workflow engine provides a hybrid orchestration system that combines:

- **Embedded Workflows** (`dox-workflow-core`): Local execution within services
- **Centralized Orchestration** (`dox-workflow-orchestrator`): Cross-service coordination
- **Validation Service** (`dox-validation-service`): File validation and security
- **Infrastructure**: Redis, PostgreSQL, monitoring stack

### Key Features

- ✅ 5-step file validation workflow
- ✅ Real-time team coordination across 7 teams
- ✅ Template recognition and matching
- ✅ Virus scanning with ClamAV
- ✅ Rate limiting and caching
- ✅ Memory bank integration
- ✅ Comprehensive monitoring and observability

---

## Prerequisites

### System Requirements

**Minimum Hardware:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- Network: 1Gbps

**Recommended Hardware:**
- CPU: 8 cores
- RAM: 16GB
- Storage: 500GB SSD
- Network: 10Gbps

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- ClamAV 0.103+

### External Dependencies

- **ClamAV**: For virus scanning
- **PostgreSQL**: For persistent state storage
- **Redis**: For caching and rate limiting
- **Nginx**: For load balancing (optional)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOX Platform                              │
├─────────────────────────────────────────────────────────────┤
│  dox-workflow-orchestrator (Port 5000)                      │
│  ├── Flask API Server                                       │
│  ├── Workflow Engine                                         │
│  ├── State Manager (PostgreSQL)                             │
│  └── Event Publisher (Redis Pub/Sub)                        │
├─────────────────────────────────────────────────────────────┤
│  dox-validation-service (Port 5007)                         │
│  ├── File Validation                                        │
│  ├── Virus Scanner (ClamAV)                                 │
│  └── Rate Limiter (Redis)                                    │
├─────────────────────────────────────────────────────────────┤
│  Application Services                                        │
│  ├── dox-tmpl-pdf-upload (Port 5002)                       │
│  ├── dox-tmpl-pdf-recognizer (Port 5003)                    │
│  ├── dox-core-store (Port 5000)                             │
│  └── dox-core-auth (Port 5001)                              │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure                                             │
│  ├── Redis (Port 6379)                                     │
│  ├── PostgreSQL (Port 5432)                                │
│  ├── Prometheus (Port 9090)                                │
│  └── Grafana (Port 3000)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Options

### 1. Docker Compose (Recommended for Development/Testing)

**Pros:** Easy setup, all services included, portable
**Cons:** Single host, limited scalability

### 2. Kubernetes (Recommended for Production)

**Pros:** Scalable, resilient, production-ready
**Cons:** More complex setup

### 3. Manual Deployment

**Pros:** Full control, customizable
**Cons:** Manual setup required

---

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd dox-admin/strategy
```

### 2. Start Infrastructure

```bash
# Start Redis and PostgreSQL
docker-compose -f infrastructure/redis/docker-compose.yml up -d
docker-compose -f infrastructure/postgres/docker-compose.yml up -d

# Wait for services to be ready
sleep 30
```

### 3. Start Monitoring Stack

```bash
# Start Prometheus, Grafana, etc.
docker-compose -f monitoring/docker-compose.yml up -d
```

### 4. Start Application Services

```bash
# Start workflow orchestrator
cd services/dox-workflow-orchestrator
docker-compose up -d

# Start validation service
cd ../dox-validation-service
docker-compose up -d
```

### 5. Verify Deployment

```bash
# Check service health
curl http://localhost:5000/health
curl http://localhost:5007/health

# Run integration tests
python tests/test_e2e_workflow_integration.py
```

---

## Production Deployment

### 1. Environment Setup

Create environment file `.env`:

```bash
# Service Configuration
SERVICE_ENV=production
DEBUG=false

# Database Configuration
POSTGRES_HOST=postgres.example.com
POSTGRES_PORT=5432
POSTGRES_DB=dox_workflows
POSTGRES_USER=dox_user
POSTGRES_PASSWORD=secure_password_here

# Redis Configuration
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here

# ClamAV Configuration
CLAMAV_HOST=clamav.example.com
CLAMAV_PORT=3310
CLAMAV_ENABLED=true

# Security
API_KEY=your_secure_api_key_here
REQUIRE_AUTH=true

# Monitoring
METRICS_ENABLED=true
```

### 2. Kubernetes Deployment

Create Kubernetes manifests:

**workflow-orchestrator-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dox-workflow-orchestrator
  namespace: dox-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dox-workflow-orchestrator
  template:
    metadata:
      labels:
        app: dox-workflow-orchestrator
    spec:
      containers:
      - name: orchestrator
        image: dox/workflow-orchestrator:latest
        ports:
        - containerPort: 5000
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: POSTGRES_HOST
          value: "postgres-service"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 3. Load Balancer Configuration

**Nginx Configuration:**
```nginx
upstream dox-workflow-orchestrator {
    server dox-workflow-orchestrator-1:5000;
    server dox-workflow-orchestrator-2:5000;
    server dox-workflow-orchestrator-3:5000;
}

upstream dox-validation-service {
    server dox-validation-service-1:5007;
    server dox-validation-service-2:5007;
}

server {
    listen 80;
    server_name api.dox-platform.com;

    location /api/v1/workflows {
        proxy_pass http://dox-workflow-orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/v1/validate {
        proxy_pass http://dox-validation-service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. SSL/TLS Setup

```bash
# Generate SSL certificates
certbot --nginx -d api.dox-platform.com

# Or use existing certificates
cp your-cert.pem /etc/ssl/certs/dox-platform.crt
cp your-key.pem /etc/ssl/private/dox-platform.key
```

---

## Configuration

### Service Configuration

**Workflow Orchestrator:**
- `SERVICE_PORT`: Service port (default: 5000)
- `REDIS_HOST`: Redis server host
- `POSTGRES_HOST`: PostgreSQL server host
- `MEMORY_BANK_PATH`: Path to memory bank files

**Validation Service:**
- `MAX_FILE_SIZE_MB`: Maximum file size (default: 50MB)
- `CLAMAV_ENABLED`: Enable virus scanning (default: true)
- `RATE_LIMIT_PER_USER_PER_DAY`: User rate limit (default: 100)

### Workflow Configuration

Workflow rules are defined in YAML files in `strategy/workflows/`:

```yaml
name: process_document_upload
service: All Upload Services
version: "1.0.0"
priority: high

trigger:
  type: api_request
  source: POST /api/documents/upload

steps:
  - name: File Validation
    action: api_call
    params:
      service: dox-validation-service
      endpoint: /api/validate/file
    on_success: File Storage
    on_failure: escalate
```

### Memory Bank Configuration

Memory banks are stored in `state/memory-banks/`:

- `WORKFLOW_EXECUTION_LOG.json`: Workflow execution audit trail
- `SUPERVISOR.json`: Master coordination log
- `TEAM_*.json`: Team-specific status files
- `SERVICE_*.json`: Service-specific status files

---

## Monitoring

### Prometheus Metrics

**Key Metrics to Monitor:**

- `workflow_completed_total`: Number of completed workflows
- `workflow_failed_total`: Number of failed workflows
- `workflow_duration_seconds`: Workflow execution duration
- `validation_scan_total`: Number of virus scans
- `rate_limit_hits_total`: Rate limit violations

### Grafana Dashboards

Pre-configured dashboards available:

1. **Workflow Orchestrator Dashboard**
   - Active workflows
   - Success/failure rates
   - Execution duration
   - Service health

2. **Validation Service Dashboard**
   - Scan results
   - Rate limit usage
   - Service performance
   - Error rates

3. **Infrastructure Dashboard**
   - Resource usage
   - Database connections
   - Redis memory usage
   - System health

### Alerting Rules

**Critical Alerts:**
- Workflow success rate < 95%
- Service health check failures
- High error rates (>5%)
- Resource usage >80%

**Warning Alerts:**
- Increasing workflow duration
- Rate limit approaching limits
- Database connection issues

### Log Aggregation

Use Loki + Promtail for log aggregation:

```yaml
# promtail-config.yml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: dox-services
    static_configs:
      - targets:
        - localhost
        labels:
          job: dox-workflow
          __path__: /var/log/dox/*.log
```

---

## Troubleshooting

### Common Issues

#### 1. Services Won't Start

**Symptoms:** Container restarts, health checks failing

**Solutions:**
```bash
# Check container logs
docker logs dox-workflow-orchestrator

# Check configuration
cat .env

# Check dependencies
docker ps | grep -E "(redis|postgres)"
```

#### 2. Workflow Execution Fails

**Symptoms:** Workflows stuck in "running" state

**Solutions:**
```bash
# Check workflow orchestrator logs
docker logs dox-workflow-orchestrator | grep ERROR

# Check database connections
curl http://localhost:5000/api/v1/services/health

# Check memory banks
ls -la state/memory-banks/
```

#### 3. Validation Service Errors

**Symptoms:** File validation failures, virus scan errors

**Solutions:**
```bash
# Check ClamAV status
clamdscan --version

# Check Redis connection
redis-cli ping

# Check validation service logs
docker logs dox-validation-service | grep ERROR
```

#### 4. Performance Issues

**Symptoms:** Slow workflow execution, high latency

**Solutions:**
```bash
# Check resource usage
docker stats

# Check database performance
docker exec postgres psql -U dox_user -d dox_workflows -c "SELECT * FROM pg_stat_activity;"

# Check Redis memory usage
redis-cli info memory
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export DEBUG=true

# Or update docker-compose.yml
environment:
  - DEBUG=true
  - LOG_LEVEL=DEBUG
```

### Health Check Scripts

**Comprehensive health check:**
```bash
#!/bin/bash
# health-check.sh

echo "🔍 DOX Platform Health Check"
echo "========================"

# Check services
services=("dox-workflow-orchestrator:5000" "dox-validation-service:5007")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    echo -n "Checking $name... "

    if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
done

# Check infrastructure
echo -n "Checking Redis... "
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo -n "Checking PostgreSQL... "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo "========================"
echo "Health check complete"
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor system health and performance
- Check for failed workflows and retry if needed
- Review log files for errors and warnings

**Weekly:**
- Update virus definitions
- Clean up old log files
- Check resource usage and scale if needed
- Review performance metrics

**Monthly:**
- Update software packages
- Backup configuration and data
- Review and update monitoring alerts
- Security scan and vulnerability assessment

### Backup Procedures

**Database Backup:**
```bash
# PostgreSQL backup
pg_dump -h localhost -U dox_user -d dox_workflows > backup_$(date +%Y%m%d).sql

# Automate with cron
0 2 * * * pg_dump -h localhost -U dox_user -d dox_workflows | gzip > /backups/dox_workflows_$(date +\%Y\%m\%d).sql.gz
```

**Configuration Backup:**
```bash
# Backup configuration files
tar -czf dox-config-backup-$(date +%Y%m%d).tar.gz \
    strategy/workflows/ \
    state/memory-banks/ \
    .env \
    docker-compose.yml
```

### Scaling Guidelines

**When to Scale Up:**
- CPU usage > 80% for sustained periods
- Memory usage > 80%
- Response times > 5 seconds
- Queue depths increasing

**Horizontal Scaling:**
- Add more replicas for stateless services
- Use database read replicas
- Implement Redis clustering

**Vertical Scaling:**
- Increase CPU and memory for compute-intensive services
- Optimize database queries and indexing

### Updates and Upgrades

**Rolling Update Procedure:**
```bash
# 1. Update one service at a time
docker-compose up -d --no-deps dox-workflow-orchestrator

# 2. Wait for health checks
sleep 30

# 3. Verify functionality
curl http://localhost:5000/health

# 4. Continue with next service
docker-compose up -d --no-deps dox-validation-service
```

**Version Compatibility:**
- Check version compatibility matrix
- Test updates in staging environment first
- Have rollback plan ready
- Monitor for issues after deployment

---

## Security

### Network Security

- Use HTTPS in production
- Implement network segmentation
- Use firewall rules to restrict access
- Regularly update SSL certificates

### Application Security

- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Regular security scanning

### Data Security

- Encrypt sensitive data at rest
- Use secure connections for data in transit
- Regular data backups
- Access control and audit logging

---

## Support

### Getting Help

- **Documentation**: Check this guide and API documentation
- **Logs**: Review service logs for error details
- **Health Checks**: Use `/health` endpoints to diagnose issues
- **Monitoring**: Check Grafana dashboards for system status

### Contact Information

- **Platform Team**: platform-team@company.com
- **Infrastructure Team**: infra-team@company.com
- **Emergency**: pagerduty@company.com

### Escalation Procedures

1. **Level 1**: Service restart, configuration check
2. **Level 2**: Database maintenance, scaling
3. **Level 3**: Code deployment, architecture changes
4. **Emergency**: Incident response team activation

---

## Appendix

### Port Reference

| Service | Port | Protocol |
|---------|------|----------|
| dox-workflow-orchestrator | 5000 | HTTP |
| dox-validation-service | 5007 | HTTP |
| dox-tmpl-pdf-upload | 5002 | HTTP |
| dox-tmpl-pdf-recognizer | 5003 | HTTP |
| dox-core-store | 5000 | HTTP |
| dox-core-auth | 5001 | HTTP |
| Redis | 6379 | TCP |
| PostgreSQL | 5432 | TCP |
| Prometheus | 9090 | HTTP |
| Grafana | 3000 | HTTP |

### File Locations

- **Workflows**: `strategy/workflows/`
- **Memory Banks**: `state/memory-banks/`
- **Configuration**: `strategy/services/`
- **Monitoring**: `strategy/monitoring/`
- **Documentation**: `strategy/docs/`

### Environment Variables Reference

[See individual service documentation for complete environment variable reference]

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-02
**Next Review**: 2025-12-02