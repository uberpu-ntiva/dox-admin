# DOX Workflow Engine Operations Runbook

Comprehensive operational procedures for the DOX workflow engine.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Incident Response](#incident-response)
3. [Performance Tuning](#performance-tuning)
4. [Backup and Recovery](#backup-and-recovery)
5. [Security Operations](#security-operations)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Troubleshooting Playbooks](#troubleshooting-playbooks)

---

## Daily Operations

### Morning Checklist (9:00 AM UTC)

**System Health Check:**
```bash
#!/bin/bash
# morning-checklist.sh

echo "🌅 DOX Platform Morning Checklist - $(date)"
echo "=============================================="

# 1. Check all services
services=("workflow-orchestrator:5000" "validation-service:5007" "pdf-upload:5002" "pdf-recognizer:5003")

echo "📊 Service Health Status:"
for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -f --max-time 5 "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "  ✅ $name (port $port)"
    else
        echo "  ❌ $name (port $port) - CHECK NEEDED"
    fi
done

# 2. Check infrastructure
echo ""
echo "🏗️ Infrastructure Status:"
echo -n "  Redis: "
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo -n "  PostgreSQL: "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# 3. Check yesterday's workflow statistics
echo ""
echo "📈 Yesterday's Workflow Summary:"
# Query database for yesterday's stats
psql -h localhost -U dox_user -d dox_workflows -c "
SELECT
    COUNT(*) as total_workflows,
    COUNT(CASE WHEN current_state = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN current_state = 'failed' THEN 1 END) as failed,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration_seconds
FROM workflow_states
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day';
" 2>/dev/null || echo "  ❌ Database query failed"

# 4. Check for errors in logs
echo ""
echo "🚨 Error Summary (Last 24 Hours):"
error_count=$(grep -c "ERROR" /var/log/dox/*.log 2>/dev/null || echo "0")
if [ $error_count -eq 0 ]; then
    echo "  ✅ No errors found"
else
    echo "  ⚠️ $error_count errors found - review logs"
fi

echo "=============================================="
```

### Daily Team Coordination Sync

The `sync_team_coordination` workflow runs automatically at 9 AM UTC:

**What it does:**
1. Aggregates status from all 20 services
2. Analyzes cross-team dependencies
3. Identifies blockers and escalations
4. Updates 7 team memory banks
5. Publishes coordination events

**Monitor sync completion:**
```bash
# Check if daily sync completed
curl -s "http://localhost:5000/api/v1/workflows?status=success&limit=5" | \
  jq -r '.workflows[] | select(.rule_name == "sync_team_coordination") | .workflow_id' | \
  head -1 | xargs -I {} curl -s "http://localhost:5000/api/v1/workflows/{}"
```

### Performance Monitoring

**Key metrics to review daily:**
- Workflow success rate (target: >95%)
- Average workflow duration (target: <30 seconds)
- Validation scan time (target: <5 seconds)
- Service response times (target: <200ms)
- Resource utilization (target: <80%)

**Grafana Dashboard Review:**
1. Open Grafana: http://localhost:3000
2. Review "DOX Workflow Orchestrator" dashboard
3. Check for any anomalies or trends
4. Investigate any alerts triggered

### Security Monitoring

**Daily security checks:**
```bash
#!/bin/bash
# security-check.sh

echo "🔒 Security Check - $(date)"

# 1. Check for failed authentication attempts
auth_failures=$(grep -c "authentication failed" /var/log/dox/auth.log 2>/dev/null || echo "0")
echo "Failed auth attempts: $auth_failures"

if [ $auth_failures -gt 100 ]; then
    echo "⚠️ High number of auth failures - investigate"
fi

# 2. Check virus scan results
virus_detections=$(grep -c "infected" /var/log/dox/validation.log 2>/dev/null || echo "0")
echo "Virus detections: $virus_detections"

if [ $virus_detections -gt 0 ]; then
    echo "🚨 Virus detected - review quarantine"
fi

# 3. Check rate limit violations
rate_limit_hits=$(grep -c "rate limit exceeded" /var/log/dox/validation.log 2>/dev/null || echo "0")
echo "Rate limit violations: $rate_limit_hits"

# 4. Review access logs for suspicious activity
echo "Top IP addresses by requests:"
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -10
```

---

## Incident Response

### Incident Severity Levels

**P1 - Critical:**
- Platform completely down
- Data corruption or loss
- Security breach
- Major customer impact

**P2 - High:**
- Core functionality degraded
- Significant performance issues
- Multiple services affected
- Customer impact for multiple users

**P3 - Medium:**
- Single service degraded
- Performance issues for some users
- Non-critical functionality affected

**P4 - Low:**
- Minor issues
- Cosmetic problems
- Documentation issues

### Incident Response Workflow

**1. Detection and Triage**
```bash
# Check for active incidents
curl -s "http://localhost:5000/api/v1/workflows?status=failed&limit=10" | \
  jq -r '.workflows[] | select(.updated_at > "'"$(date -d '1 hour ago' -I)"'"') | \
  .workflow_id'

# Check error rates
error_rate=$(curl -s "http://localhost:5000/api/v1/metrics" | \
  jq -r '.metrics.error_rate_5m // 0')

if (( $(echo "$error_rate > 0.05" | bc -l) )); then
    echo "🚨 High error rate detected: $error_rate"
fi
```

**2. Initial Assessment**
- Gather basic information (what, when, impact)
- Determine severity level
- Create incident ticket
- Notify stakeholders

**3. Investigation**
- Check service logs
- Review metrics and dashboards
- Identify root cause
- Document findings

**4. Resolution**
- Implement fix
- Verify resolution
- Monitor for recurrence
- Document lessons learned

### Incident Communication Templates

**P1 Incident Alert:**
```
🚨 CRITICAL INCIDENT - DOX Platform

Service: [Service Name]
Impact: [Description of impact]
Start Time: [Timestamp]
Status: [Investigating/Resolving/Resolved]
Est. Resolution: [Time estimate]

Updates will be provided every 15 minutes.
```

**P2 Incident Alert:**
```
⚠️ HIGH SEVERITY INCIDENT - DOX Platform

Service: [Service Name]
Impact: [Description of impact]
Start Time: [Timestamp]
Status: [Investigating/Resolving/Resolved]

Next update in 30 minutes.
```

### Escalation Procedures

**When to Escalate:**
- P1 incidents not resolved within 15 minutes
- P2 incidents not resolved within 1 hour
- Multiple P3/P4 incidents occurring
- Unknown root cause after 30 minutes

**Escalation Contacts:**
- **On-Call Engineer**: pager@company.com
- **Platform Lead**: platform-lead@company.com
- **Incident Commander**: incident@company.com

---

## Performance Tuning

### Database Optimization

**PostgreSQL Performance Tuning:**
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Analyze table statistics
ANALYZE workflow_states;
ANALYZE workflow_step_results;
ANALYZE workflow_events;
```

**Connection Pool Optimization:**
```python
# In workflow orchestrator app.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### Redis Optimization

**Memory Management:**
```bash
# Check Redis memory usage
redis-cli info memory | grep used_memory_human

# Check key space stats
redis-cli info keyspace

# Monitor slow operations
redis-cli --latency-history -i 1
```

**Configuration Tuning:**
```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Application Performance

**Workflow Engine Tuning:**
```python
# Optimize workflow runner
WORKFLOW_CONCURRENCY = 10
WORKFLOW_TIMEOUT = 300  # 5 minutes
WORKFLOW_RETRY_ATTEMPTS = 3
WORKFLOW_RETRY_BACKOFF = 1.5  # Exponential backoff multiplier
```

**Rate Limiting Optimization:**
```python
# Tune rate limiting
RATE_LIMIT_CACHE_TTL = 3600  # 1 hour
RATE_LIMIT_CLEANUP_INTERVAL = 300  # 5 minutes
RATE_LIMIT_BATCH_SIZE = 100
```

### Scaling Guidelines

**Horizontal Scaling:**
- Add more application replicas behind load balancer
- Use read replicas for database reads
- Implement Redis clustering for high availability

**Vertical Scaling:**
- Increase CPU cores for CPU-intensive operations
- Add memory for caching and in-memory processing
- Use faster storage (SSD/NVMe)

**Auto-scaling Triggers:**
```yaml
# Kubernetes HPA example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dox-workflow-orchestrator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dox-workflow-orchestrator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Backup and Recovery

### Database Backup Strategy

**Daily Backup:**
```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dox_workflows_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -h localhost -U dox_user -d dox_workflows > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Verify backup
if [ -f "${BACKUP_FILE}.gz" ]; then
    echo "✅ Backup created: ${BACKUP_FILE}.gz"

    # Clean up old backups (keep 30 days)
    find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
else
    echo "❌ Backup failed"
    exit 1
fi
```

**Point-in-Time Recovery:**
```bash
# Enable WAL archiving
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

### Configuration Backup

```bash
#!/bin/bash
# backup-config.sh

CONFIG_BACKUP_DIR="/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $CONFIG_BACKUP_DIR

# Backup configuration files
tar -czf "$CONFIG_BACKUP_DIR/dox-config_$DATE.tar.gz" \
    strategy/workflows/ \
    strategy/memory-banks/ \
    .env \
    docker-compose.yml \
    monitoring/

echo "✅ Configuration backup completed"
```

### Recovery Procedures

**Database Recovery:**
```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop application services
docker-compose down

# Drop existing database
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS dox_workflows;"

# Create new database
psql -h localhost -U postgres -c "CREATE DATABASE dox_workflows OWNER dox_user;"

# Restore from backup
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | psql -h localhost -U dox_user -d dox_workflows
else
    psql -h localhost -U dox_user -d dox_workflows < $BACKUP_FILE
fi

echo "✅ Database restored from backup"
```

**Configuration Recovery:**
```bash
#!/bin/bash
# restore-config.sh

CONFIG_BACKUP=$1

if [ -z "$CONFIG_BACKUP" ]; then
    echo "Usage: $0 <config_backup.tar.gz>"
    exit 1
fi

# Backup current configuration
tar -czf "config-backup-$(date +%Y%m%d_%H%M%S).tar.gz" \
    strategy/workflows/ \
    strategy/memory-banks/ \
    .env

# Restore configuration
tar -xzf $CONFIG_BACKUP

echo "✅ Configuration restored"
```

### Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 24 hours

**Recovery Priority Order:**
1. Database and configuration
2. Application services
3. Monitoring and logging
4. External integrations

**Test Recovery Procedures:**
- Monthly disaster recovery drills
- Quarterly full system recovery test
- Annual off-site recovery test

---

## Security Operations

### Security Monitoring

**Daily Security Scans:**
```bash
#!/bin/bash
# security-scan.sh

echo "🔒 Daily Security Scan - $(date)"

# 1. Check for unauthorized access attempts
echo "Checking authentication logs..."
auth_attempts=$(grep -c "authentication failed" /var/log/dox/auth.log)
echo "Failed auth attempts: $auth_attempts"

# 2. Check for suspicious IP addresses
echo "Checking top IP addresses..."
awk '{print $1}' /var/log/nginx/access.log | \
  sort | uniq -c | sort -nr | head -10 > /tmp/top_ips.txt

# 3. Check for virus detections
echo "Checking virus scan results..."
virus_found=$(grep -c "scan_result.*infected" /var/log/dox/validation.log)
echo "Viruses detected: $virus_found"

# 4. Check file integrity
echo "Checking file integrity..."
find /opt/dox -type f -name "*.py" -exec sha256sum {} \; > /tmp/current_hashes.txt
diff /opt/dox/baseline_hashes.txt /tmp/current_hashes.txt || echo "⚠️ File integrity check failed"

# 5. Check for exposed credentials
echo "Checking for exposed credentials..."
grep -r "password\|secret\|key" /opt/dox/config/ | grep -v "encrypted\|hashed" > /tmp/exposed_creds.txt
```

### Vulnerability Management

**Weekly Vulnerability Scanning:**
```bash
#!/bin/bash
# vulnerability-scan.sh

# Scan Docker images for vulnerabilities
docker images --format "table {{.Repository}}:{{.Tag}}" | grep dox

# Use Trivy for vulnerability scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image dox-workflow-orchestrator:latest

# Scan Python packages
pip-audit --format=json > /tmp/vulnerability-report.json
```

**Security Patch Management:**
- Monitor security advisories for all dependencies
- Apply critical patches within 24 hours
- Test patches in staging before production deployment
- Maintain patch inventory and schedule

### Access Control

**User Access Management:**
```bash
# Review active user accounts
psql -h localhost -U dox_user -d dox_workflows -c "
SELECT username, last_login, role, status
FROM users
WHERE status = 'active'
ORDER BY last_login DESC;
"

# Review API key usage
psql -h localhost -U dox_user -d dox_workflows -c "
SELECT api_key, created_at, last_used, usage_count
FROM api_keys
WHERE last_used > NOW() - INTERVAL '30 days';
"
```

**Network Security:**
```bash
# Review firewall rules
iptables -L -n -v

# Check for open ports
netstat -tulpn | grep LISTEN

# Monitor network connections
ss -tuln | grep -E ":(5000|5007|6379|5432)"
```

---

## Maintenance Procedures

### Weekly Maintenance

**System Health Check:**
```bash
#!/bin/bash
# weekly-maintenance.sh

echo "🔧 Weekly Maintenance - $(date)"

# 1. Clean up old logs
find /var/log/dox -name "*.log" -mtime +30 -delete
find /tmp -name "dox-*" -mtime +7 -delete

# 2. Optimize database
psql -h localhost -U dox_user -d dox_workflows -c "VACUUM ANALYZE;"

# 3. Check disk space
df -h | grep -E "(/$|/opt|/var)"

# 4. Update ClamAV signatures
freshclam

# 5. Backup configuration
./backup-config.sh

echo "✅ Weekly maintenance completed"
```

### Monthly Maintenance

**System Updates:**
```bash
#!/bin/bash
# monthly-maintenance.sh

echo "🔄 Monthly Maintenance - $(date)"

# 1. Update system packages
apt-get update && apt-get upgrade -y

# 2. Update Docker images
docker-compose pull

# 3. Restart services
docker-compose down
docker-compose up -d

# 4. Verify services are healthy
sleep 30
./health-check.sh

# 5. Generate monthly report
./generate-monthly-report.sh

echo "✅ Monthly maintenance completed"
```

### Quarterly Maintenance

**Comprehensive System Review:**
- Performance analysis and optimization
- Security audit and penetration testing
- Capacity planning and scaling review
- Documentation updates
- Disaster recovery testing

---

## Troubleshooting Playbooks

### Playbook: High Error Rate

**Symptoms:**
- Error rate > 5%
- Multiple workflow failures
- Service health checks failing

**Investigation Steps:**
1. Check service logs for error patterns
2. Review recent deployments or changes
3. Check system resources (CPU, memory, disk)
4. Verify external service dependencies
5. Check database performance

**Common Causes:**
- Database connection issues
- External service outages
- Resource exhaustion
- Configuration errors
- Code deployment issues

**Resolution Steps:**
```bash
# 1. Check service status
docker ps | grep dox

# 2. Check recent logs
docker logs --since 1h dox-workflow-orchestrator

# 3. Check system resources
top -p $(pgrep -f dox)

# 4. Restart affected services
docker-compose restart dox-workflow-orchestrator

# 5. Verify recovery
curl -f http://localhost:5000/health
```

### Playbook: Slow Workflow Execution

**Symptoms:**
- Workflow duration > 5 minutes
- Queued workflows accumulating
- User complaints about slowness

**Investigation Steps:**
1. Check workflow execution logs
2. Profile slow workflow steps
3. Check external service response times
4. Review database query performance
5. Analyze resource utilization

**Common Causes:**
- Database query performance issues
- External service latency
- Resource contention
- Workflow step bottlenecks
- Large file processing

**Resolution Steps:**
```bash
# 1. Identify slow workflows
curl -s "http://localhost:5000/api/v1/workflows?status=running" | \
  jq -r '.workflows[] | select(.duration_seconds > 300)'

# 2. Check database performance
psql -h localhost -U dox_user -d dox_workflows -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;"

# 3. Scale services if needed
docker-compose up -d --scale dox-workflow-orchestrator=5

# 4. Optimize database indexes
psql -h localhost -U dox_user -d dox_workflows -c "ANALYZE;"
```

### Playbook: Validation Service Issues

**Symptoms:**
- File validation failures
- Virus scan errors
- Rate limiting issues

**Investigation Steps:**
1. Check ClamAV service status
2. Verify Redis connectivity
3. Review validation service logs
4. Check disk space and permissions
5. Test file validation manually

**Common Causes:**
- ClamAV service down
- Redis connection issues
- Disk space exhaustion
- Permission problems
- Network connectivity issues

**Resolution Steps:**
```bash
# 1. Check ClamAV status
clamdscan --version
systemctl status clamav-daemon

# 2. Check Redis connectivity
redis-cli ping

# 3. Check disk space
df -h /tmp
df -h /var/lib/clamav

# 4. Restart services
systemctl restart clamav-daemon
docker-compose restart dox-validation-service

# 5. Test validation
curl -X POST http://localhost:5007/api/v1/validate/scan \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/tmp/test.pdf", "file_hash": "test", "file_size": 1024}'
```

### Playbook: Memory Bank Issues

**Symptoms:**
- Team coordination failures
- Memory bank update errors
- File locking conflicts

**Investigation Steps:**
1. Check memory bank file permissions
2. Verify file locking mechanism
3. Review team coordination logs
4. Check for concurrent access issues
5. Validate JSON file integrity

**Common Causes:**
- File permission issues
- Concurrent access conflicts
- JSON corruption
- Disk I/O problems
- Network file system issues

**Resolution Steps:**
```bash
# 1. Check file permissions
ls -la strategy/memory-banks/

# 2. Validate JSON files
for file in strategy/memory-banks/*.json; do
    python -m json.tool "$file" > /dev/null 2>&1 || echo "Invalid JSON: $file"
done

# 3. Fix permissions if needed
chmod 664 strategy/memory-banks/*.json
chown dox:dox strategy/memory-banks/*.json

# 4. Test memory bank update
curl -X POST http://localhost:5000/api/v1/coordination/sync
```

### Contact Information

**Escalation Contacts:**
- **On-Call Engineer**: +1-555-123-4567
- **Platform Lead**: platform-lead@company.com
- **Incident Commander**: incident@company.com

**Documentation Updates:**
- Update runbook with new procedures
- Document lessons learned from incidents
- Share best practices with team

---

**Runbook Version**: 1.0.0
**Last Updated**: 2025-11-02
**Next Review**: 2025-12-02