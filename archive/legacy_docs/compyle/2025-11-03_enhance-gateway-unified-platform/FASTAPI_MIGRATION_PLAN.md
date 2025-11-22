# FastAPI Migration Plan

## Executive Summary

Migrate DOX platform from mixed Flask/FastAPI to standardized **FastAPI** for:
- 2-3x performance improvement
- Automatic API documentation
- Better async/await support
- Type safety with Pydantic
- Reduced maintenance complexity

**Timeline:** 8-12 weeks (phased approach)
**Effort:** Medium (no functional changes, only refactoring)
**Risk:** Low (services remain independent)

---

## Current State

### Flask Services (12 services)
```
dox-gtwy-main                    (564 lines)  - Gateway
dox-core-auth                    (803 lines)  - Authentication
dox-actv-service                 (400 lines)  - Activation workflow
dox-actv-listener                (720 lines)  - Event listener
dox-auto-lifecycle-service       (729 lines)  - Contract lifecycle
dox-auto-workflow-engine         (1256 lines) - Workflow builder
dox-batch-assembly               (600 lines)  - Batch assembly
dox-tmpl-field-mapper            (856 lines)  - Field mapping
dox-pact-manual-upload           (500 lines)  - PACT upload
dox-rtns-manual-upload           (500 lines)  - RTNS upload
dox-esig-webhook-listener        (400 lines)  - Webhook receiver
```

### FastAPI Services (8 services)
```
dox-tmpl-service                 (39,700 lines) - Templates (existing)
dox-esig-service                 (43,981 lines) - E-signature (existing)
dox-data-etl-service             (311 lines)    - ETL (existing)
dox-data-distrib-service         (851 lines)    - Distribution (existing)
dox-tmpl-pdf-upload              (844 lines)    - PDF upload (existing)
dox-tmpl-pdf-recognizer          (1000+ lines)  - PDF recognition (existing)
dox-core-store                   (500+ lines)   - Storage (existing)
dox-core-rec-engine              (500+ lines)   - Recognition (existing)
```

### Mixed
```
dox-data-aggregation-service     (600 lines)    - Analytics (existing)
```

---

## Migration Strategy

### Phase 1: Infrastructure & Tools (Week 1-2)

**Objective:** Create migration scaffolding and utilities

**Tasks:**
1. **Create FastAPI migration template**
   ```python
   # template/app.py
   from fastapi import FastAPI, Depends, HTTPException
   from fastapi.middleware.cors import CORSMiddleware
   from pydantic import BaseModel, Field
   from typing import Optional
   import logging

   app = FastAPI(
       title="[SERVICE_NAME]",
       version="1.0.0",
       docs_url="/docs",
       openapi_url="/openapi.json"
   )

   # CORS middleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   # Logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   # Configuration
   class Config:
       SERVICE_NAME = "[SERVICE_NAME]"
       SERVICE_VERSION = "1.0.0"
       REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
       DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

   config = Config()

   # Models (Pydantic)
   class ResponseModel(BaseModel):
       success: bool
       data: Optional[dict] = None
       error: Optional[str] = None

   # Health check
   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "service": config.SERVICE_NAME,
           "version": config.SERVICE_VERSION
       }

   # Root
   @app.get("/")
   async def root():
       return {
           "service": config.SERVICE_NAME,
           "version": config.SERVICE_VERSION,
           "docs": "/docs"
       }
   ```

2. **Create migration scripts**
   - `flask_to_fastapi.py` - Convert routes
   - `validate_migration.py` - Verify functionality
   - `test_compatibility.py` - Compare responses

3. **Document conversion patterns**
   ```python
   # Flask Pattern → FastAPI Pattern

   # 1. Route Definition
   # Flask:  @app.route('/users/<id>', methods=['GET'])
   # FastAPI: @app.get("/users/{id}")

   # 2. Request Body
   # Flask:  data = request.get_json()
   # FastAPI: async def func(request: UserRequest)

   # 3. Response
   # Flask:  return jsonify({...}), 200
   # FastAPI: return {...}  # auto-serialized

   # 4. Error Handling
   # Flask:  return jsonify({...}), 404
   # FastAPI: raise HTTPException(status_code=404, detail=...)

   # 5. Middleware
   # Flask:  @app.before_request, @app.after_request
   # FastAPI: @app.middleware("http")
   ```

---

### Phase 2: High-Impact Services (Week 3-5)

**Objective:** Migrate critical path services first

**Priority Order:**

#### 2A. dox-gtwy-main (API Gateway) - Week 3
- **Why First:** Central hub, high visibility
- **Impact:** High (30+ routes)
- **Risk:** Medium (all traffic flows through)
- **Pattern:** Convert route handling to FastAPI dependency injection

**Migration Steps:**
```python
# Before (Flask)
@app.route('/auth/<path:path>', methods=['GET', 'POST'])
@rate_limit('core-auth')
def auth_routes(path):
    return handle_service_request('core-auth', f'auth/{path}')

# After (FastAPI)
from fastapi import APIRouter, Path, Depends
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/{path:path}")
@router.post("/{path:path}")
async def auth_routes(
    path: Annotated[str, Path()],
    rate_limit_check = Depends(check_rate_limit),
    auth = Depends(require_auth)
):
    return await handle_service_request('core-auth', f'auth/{path}')

app.include_router(router)
```

**Testing:**
- Parallel run Flask & FastAPI versions
- Compare response structures
- Load test both versions
- Verify all 30+ routes work identically

#### 2B. dox-core-auth (Authentication) - Week 4
- **Why Second:** Foundation service, other services depend on it
- **Impact:** High (auth on every request)
- **Risk:** Medium (security-critical)
- **New Features:** Better JWT handling, async token validation

**Migration Improvements:**
```python
# JWT validation (faster in FastAPI)
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi import Security

security = HTTPBearer()

async def validate_token(credentials: HTTPAuthCredentials = Security(security)):
    """Async JWT validation - much faster"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401)

@app.get("/validate")
async def validate(user = Depends(validate_token)):
    return {"user": user}
```

#### 2C. dox-tmpl-field-mapper (Field Mapping) - Week 5
- **Why Third:** Heavy compute, benefits most from async
- **Impact:** Medium
- **Risk:** Low
- **Performance Gain:** Async field extraction = 30-50% faster

---

### Phase 3: Processing Services (Week 6-8)

**Services to Migrate:**

#### 3A. Document Processing Pipeline
```
Week 6: dox-auto-lifecycle-service    (contract state management)
Week 6: dox-batch-assembly            (document batching)
Week 7: dox-pact-manual-upload        (document intake)
Week 7: dox-rtns-manual-upload        (returns processing)
```

#### 3B. Event Processing
```
Week 8: dox-actv-service              (activation workflow)
Week 8: dox-actv-listener             (async event processing) ← Most benefit
Week 8: dox-esig-webhook-listener     (webhook handling)
```

**Why Last:** Lower traffic volume, easier to parallelize

---

### Phase 4: Workflow & Automation (Week 9-10)

```
Week 9:  dox-auto-workflow-engine (1256 lines - largest)
Week 10: Parallel: Data services
         - dox-data-etl-service
         - dox-data-distrib-service
```

**dox-auto-workflow-engine Special Handling:**
```python
# Current: Threading + synchronous execution
# New: True async with FastAPI

# Before (Flask + threading)
workflow_queue = queue.Queue()
def process_workflows():
    while True:
        workflow = workflow_queue.get()
        # synchronous execution

# After (FastAPI async)
async def process_workflows():
    while True:
        workflow = await workflow_queue.get()
        # async execution
        await execute_workflow_step(workflow)  # true concurrency
```

**Performance Impact:** 3-5x throughput improvement

---

## Migration Pattern: Detailed Conversion Guide

### Pattern 1: Simple GET/POST Routes

```python
# ============ BEFORE (Flask) ============
from flask import Flask, request, jsonify

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = db.get_user(user_id)
        if not user:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'data': user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = db.create_user(data)
    return jsonify({'data': user}), 201

# ============ AFTER (FastAPI) ============
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class UserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(request: UserRequest):
    user = db.create_user(request.dict())
    return user
```

### Pattern 2: Middleware & Dependencies

```python
# ============ BEFORE (Flask) ============
@app.before_request
def log_request():
    g.start_time = time.time()
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    elapsed = time.time() - g.start_time
    logger.info(f"Response: {response.status_code} ({elapsed:.2f}s)")
    response.headers['X-Response-Time'] = f"{elapsed:.2f}s"
    return response

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# ============ AFTER (FastAPI) ============
from fastapi import Header, Depends, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        elapsed = time.time() - start_time
        logger.info(f"Response: {response.status_code} ({elapsed:.2f}s)")
        response.headers['X-Response-Time'] = f"{elapsed:.2f}s"
        return response

app.add_middleware(LoggingMiddleware)

async def verify_auth(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return authorization

@app.get("/protected")
async def protected_route(auth = Depends(verify_auth)):
    return {"message": "Protected resource"}
```

### Pattern 3: Error Handling

```python
# ============ BEFORE (Flask) ============
class ValidationError(Exception):
    pass

@app.errorhandler(ValidationError)
def handle_validation(error):
    return jsonify({'error': str(error)}), 400

@app.route('/process', methods=['POST'])
def process_data():
    data = request.get_json()
    if not data.get('required_field'):
        raise ValidationError('required_field is required')
    # process...
    return jsonify({'status': 'ok'})

# ============ AFTER (FastAPI) ============
from fastapi import HTTPException
from pydantic import BaseModel, validator

class ProcessRequest(BaseModel):
    required_field: str

    @validator('required_field')
    def validate_field(cls, v):
        if not v:
            raise ValueError('required_field cannot be empty')
        return v

@app.post("/process")
async def process_data(request: ProcessRequest):
    # Validation automatically happens via Pydantic
    # Invalid request returns 422 Unprocessable Entity
    return {"status": "ok"}
```

---

## Migration Checklist Per Service

```markdown
## dox-gtwy-main Migration Checklist

### Pre-Migration
- [ ] Document all current routes
- [ ] Set up parallel test environment
- [ ] Create test suite for all 30+ routes
- [ ] Document rate limiting rules
- [ ] Document circuit breaker configuration

### Migration
- [ ] Convert Flask app structure to FastAPI
- [ ] Convert all route handlers to async
- [ ] Convert middleware (logging, rate limiting, auth)
- [ ] Convert error handlers
- [ ] Update requirements.txt (replace flask with fastapi)
- [ ] Update Dockerfile

### Testing
- [ ] Run unit tests for each route
- [ ] Parallel load test (Flask vs FastAPI)
- [ ] Performance comparison
- [ ] Circuit breaker validation
- [ ] Rate limiting validation

### Deployment
- [ ] Deploy to staging
- [ ] Blue-green deploy pattern
- [ ] Monitor error rates
- [ ] Verify all downstream services can call new version
- [ ] Rollback plan ready

### Post-Migration
- [ ] Monitor performance gains
- [ ] Document what changed
- [ ] Update runbooks
- [ ] Archive old Flask version
```

---

## Performance Expectations

### Before (Flask)
```
Single Request (avg):     45ms
Concurrent Requests/s:    200/s
Memory per Instance:      150MB
Cold Start:              3-5s
```

### After (FastAPI)
```
Single Request (avg):     15ms  (3.0x faster)
Concurrent Requests/s:    600/s (3.0x higher throughput)
Memory per Instance:      120MB (20% reduction)
Cold Start:              2-3s   (faster imports)
```

**Cumulative Impact:** 5-10x system capacity improvement

---

## Risk Mitigation

### Risk 1: Breaking Changes in API Responses

**Mitigation:**
- Keep FastAPI response format identical to Flask
- Extensive integration testing
- Parallel run period (2-4 weeks)
- Version endpoints during transition

### Risk 2: Async/Await Issues

**Mitigation:**
- All database operations wrapped in `await`
- Redis operations use aioredis
- CPU-bound work moved to thread pool
- Careful testing of concurrent access

### Risk 3: Third-Party Library Compatibility

**Mitigation:**
- Keep same versions where possible
- Test with FastAPI equivalents
- Gradual migration (don't convert all at once)

---

## Rollback Procedure

If FastAPI version fails:

```bash
# 1. Stop FastAPI services
kubectl delete deployment -l version=fastapi

# 2. Scale Flask services back up
kubectl scale deployment flask-gateway --replicas=3

# 3. Revert routing
# (Update service discovery/DNS to point to Flask)

# 4. Investigate and fix issues
# (Debug in parallel environment)

# 5. Re-attempt migration
```

**Estimated Rollback Time:** 5-10 minutes

---

## Phase Summary

| Phase | Services | Duration | Risk | Benefit |
|-------|----------|----------|------|---------|
| 1     | Tools    | 2 weeks  | Low  | Foundation |
| 2     | Gateway, Auth, Field Mapper | 3 weeks | Medium | High visibility |
| 3     | Processing & Events | 3 weeks | Low | Throughput |
| 4     | Workflow & Data | 2 weeks | Low | Scalability |

**Total Duration:** 8-12 weeks (staggered)
**Total Effort:** ~400-500 engineering hours
**Peak Team Size:** 3-4 engineers

---

## Success Criteria

✅ All 20 services migrated to FastAPI
✅ 2-3x performance improvement verified
✅ Zero functional regressions
✅ All integration tests passing
✅ Production load testing successful
✅ Monitoring & alerting updated
✅ Team trained on FastAPI patterns
✅ Documentation updated

---

## Next Steps

1. **Week 1:** Create FastAPI migration template
2. **Week 2:** Build migration & validation tools
3. **Week 3:** Begin dox-gtwy-main migration
4. **Follow checklist** for each subsequent service
5. **Monitor & tune** performance throughout

