"""
FastAPI Migration Template
Use this template for migrating Flask services to FastAPI
"""

import os
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, Field
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service Configuration (customize per service)
class ServiceConfig:
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "template-service")
    SERVICE_VERSION = os.environ.get("SERVICE_VERSION", "1.0.0")
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/db")

    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

config = ServiceConfig()

# FastAPI App Instance
app = FastAPI(
    title=config.SERVICE_NAME,
    version=config.SERVICE_VERSION,
    description=f"FastAPI version of {config.SERVICE_NAME}",
    docs_url="/docs" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic Models (Base Models - customize per service)
class ResponseModel(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: time.time())

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    dependencies: Optional[Dict[str, str]] = None

# Middleware for Request Timing
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Middleware for Request Logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} ({process_time:.3f}s)")
    return response

# Authentication Dependencies
async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    """Verify JWT token"""
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Add your JWT validation logic here
    # For now, just return a mock user
    return {"sub": "user123", "email": "user@example.com", "roles": ["user"]}

async def verify_admin_token(user: dict = Depends(verify_token)):
    """Verify admin privileges"""
    if "admin" not in user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

# Rate Limiting (simple implementation)
from collections import defaultdict
from datetime import datetime, timedelta

rate_limit_store = defaultdict(list)

async def rate_limit(request, max_requests: int = 100, window_seconds: int = 60):
    """Simple rate limiting"""
    client_ip = request.client.host
    now = datetime.utcnow()

    # Clean old entries
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if now - req_time < timedelta(seconds=window_seconds)
    ]

    if len(rate_limit_store[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    rate_limit_store[client_ip].append(now)

# Health Check Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check"""
    return HealthResponse(
        status="healthy",
        service=config.SERVICE_NAME,
        version=config.SERVICE_VERSION,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/health/detailed", response_model=HealthResponse)
async def detailed_health_check():
    """Detailed health check with dependencies"""
    dependencies = {}

    # Check Redis (if applicable)
    try:
        # Add Redis check here
        dependencies["redis"] = "connected"
    except Exception as e:
        dependencies["redis"] = f"error: {str(e)}"

    # Check Database
    try:
        # Add database check here
        dependencies["database"] = "connected"
    except Exception as e:
        dependencies["database"] = f"error: {str(e)}"

    return HealthResponse(
        status="healthy",
        service=config.SERVICE_NAME,
        version=config.SERVICE_VERSION,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        dependencies=dependencies
    )

# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "status": "running",
        "docs": "/docs" if config.DEBUG else "disabled",
        "health": "/health"
    }

# Example Protected Endpoint
@app.get("/protected", response_model=ResponseModel)
async def protected_route(user: dict = Depends(verify_token)):
    """Example protected endpoint"""
    return ResponseModel(
        success=True,
        data={"message": "Protected resource accessed", "user": user["email"]}
    )

# Example Admin Endpoint
@app.get("/admin/stats", response_model=ResponseModel)
async def admin_stats(admin_user: dict = Depends(verify_admin_token)):
    """Example admin endpoint"""
    return ResponseModel(
        success=True,
        data={"message": "Admin stats accessed", "admin": admin_user["email"]}
    )

# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return ResponseModel(
        success=False,
        error=exc.detail,
        timestamp=time.time()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return ResponseModel(
        success=False,
        error="Internal server error",
        timestamp=time.time()
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info(f"Starting {config.SERVICE_NAME} v{config.SERVICE_VERSION}")
    logger.info(f"Debug mode: {config.DEBUG}")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info(f"Shutting down {config.SERVICE_NAME}")

# Migration Helper Functions
def convert_flask_route_to_fastapi(flask_route_path: str, methods: List[str]) -> str:
    """Convert Flask route to FastAPI path"""
    # Convert /users/<user_id> to /users/{user_id}
    fastapi_path = flask_route_path
    for param in ["<", ">"]:
        fastapi_path = fastapi_path.replace(param, "")
    for param in flask_route_path.split("/"):
        if param and "<" in flask_route_path:
            fastapi_path = fastapi_path.replace(f"/{param}", f"/{{{param.replace('<', '').replace('>', '')}}}")
    return fastapi_path

def convert_flask_error_response(error_msg: str, status_code: int) -> HTTPException:
    """Convert Flask error response to FastAPI"""
    return HTTPException(
        status_code=status_code,
        detail=error_msg
    )

# Database Connection Example (customize per service)
async def get_db_connection():
    """Get database connection - customize for your service"""
    # Example for PostgreSQL
    import asyncpg
    return await asyncpg.connect(config.DATABASE_URL)

# Redis Connection Example (customize per service)
async def get_redis_connection():
    """Get Redis connection - customize for your service"""
    import aioredis
    return await aioredis.from_url(
        f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}"
    )

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {config.SERVICE_NAME} on port 8000")
    uvicorn.run(
        "template:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level="info" if not config.DEBUG else "debug"
    )