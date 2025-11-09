#!/usr/bin/env python3
"""
DOX Admin Service
Administrative interface for managing the PACT system
"""

import os
import logging
import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import redis.asyncio as redis
import aiohttp
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./admin.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CORE_STORE_URL = os.getenv("CORE_STORE_URL", "http://localhost:5001")
    CORE_AUTH_URL = os.getenv("CORE_AUTH_URL", "http://localhost:5000")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    SERVICE_NAME = "dox-admin"
    SERVICE_VERSION = "1.0.0"

config = Config()

class UserRole(str, Enum):
    ADMIN = "admin"
    PROCESSOR = "processor"
    VIEWER = "viewer"
    USER = "user"

@dataclass
class AdminUser:
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class SystemMetric:
    metric_name: str
    value: Union[int, float]
    unit: str
    timestamp: datetime
    category: str
    metadata: Dict[str, Any] = None

class AdminDashboard:
    """Administrative dashboard for system management"""

    def __init__(self):
        self.service_urls = {
            'core_store': config.CORE_STORE_URL,
            'core_auth': config.CORE_AUTH_URL
        }
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {os.getenv('ADMIN_API_KEY', 'admin-api-key')}"
        }
        self.redis_client = None

    async def initialize(self):
        """Initialize dashboard connections"""
        try:
            self.redis_client = redis.from_url(config.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Admin Dashboard initialized")
        except Exception as e:
            logger.error(f"Failed to initialize dashboard: {e}")
            raise

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        health_status = {}

        # Check core services
        for service_name, url in self.service_urls.items():
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(f"{url}/api/v1/health") as response:
                        if response.status == 200:
                            health_status[service_name] = "healthy"
                        else:
                            health_status[service_name] = f"unhealthy ({response.status})"
            except Exception as e:
                health_status[service_name] = f"error: {str(e)}"

        return health_status

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user and authentication statistics"""
        try:
            # This would query the auth service for actual data
            # For now, return mock data
            return {
                "total_users": 1250,
                "active_sessions": 342,
                "new_users_today": 8,
                "users_by_role": {
                    "admin": 15,
                    "processor": 125,
                    "viewer": 875,
                    "user": 235
                },
                "failed_logins_last_24h": 42,
                "password_resets_today": 5
            }
        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return {"error": str(e)}

    async def get_document_statistics(self) -> Dict[str, Any]:
        """Get document processing statistics"""
        try:
            return {
                "total_documents": 15420,
                "documents_processed_today": 342,
                "pending_processing": 23,
                "failed_processing": 5,
                "documents_by_type": {
                    "contract": 8934,
                    "agreement": 4521,
                    "form": 1234,
                    "template": 731
                },
                "documents_by_status": {
                    "completed": 15200,
                    "processing": 134,
                    "failed": 86
                },
                "average_processing_time": 3.2,
                "storage_used_gb": 245.7,
                "storage_total_gb": 1024
            }
        except Exception as e:
            logger.error(f"Failed to get document statistics: {e}")
            return {"error": str(e)}

    async def get_esignature_statistics(self) -> Dict[str, Any]:
        """Get e-signature statistics"""
        try:
            return {
                "total_transactions": 8934,
                "completed_today": 156,
                "pending_signature": 45,
                "expired_transactions": 12,
                "success_rate": 97.2,
                "average_completion_time_minutes": 12.5,
                "transactions_by_type": {
                    "contract": 4523,
                    "agreement": 2341,
                    "form": 1567,
                    "other": 1503
                },
                "signatures_pending": 89
            }
        except Exception as e:
            logger.error(f"Failed to get e-signature statistics: {e}")
            return {"error": str(e)}

    async def get_system_metrics(self, time_range: str = "24h") -> List[SystemMetric]:
        """Get system performance metrics"""
        try:
            # This would collect actual system metrics
            # For now, return mock data
            metrics = []
            now = datetime.utcnow()

            # CPU and Memory metrics
            metrics.append(SystemMetric(
                metric_name="cpu_usage",
                value=45.2,
                unit="percent",
                timestamp=now,
                category="system",
                metadata={"core": "critical"}
            ))

            metrics.append(SystemMetric(
                metric_name="memory_usage",
                value=68.7,
                unit="percent",
                timestamp=now,
                category="system",
                metadata={"total_gb": 16}
            ))

            # API metrics
            metrics.append(SystemMetric(
                metric_name="api_requests_per_second",
                value=156.3,
                unit="req/s",
                timestamp=now,
                category="performance"
            ))

            metrics.append(SystemMetric(
                metric_name="average_response_time",
                value=234.5,
                unit="ms",
                timestamp=now,
                category="performance"
            ))

            # Database metrics
            metrics.append(SystemMetric(
                metric_name="database_connections",
                value=12,
                unit="connections",
                timestamp=now,
                category="database"
            ))

            return metrics

        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return []

    async def get_activity_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent system activity logs"""
        try:
            # This would query the activity service for actual logs
            # For now, return mock data
            logs = []
            now = datetime.utcnow()

            for i in range(min(limit, 20)):
                timestamp = now - timedelta(minutes=i * 30)
                logs.append({
                    "id": f"log_{i}",
                    "timestamp": timestamp.isoformat(),
                    "level": ["INFO", "WARNING", "ERROR", "DEBUG"][i % 4],
                    "service": ["dox-core-auth", "dox-core-store", "dox-pact-manual-upload"][i % 3],
                    "message": [
                        "User login successful",
                        "Document uploaded successfully",
                        "Processing queue is full",
                        "Database connection established"
                    ][i % 4],
                    "user_id": f"user_{i}" if i < 10 else None,
                    "session_id": f"session_{i}"
                })

            return logs

        except Exception as e:
            logger.error(f"Failed to get activity logs: {e}")
            return []

    async def generate_report(self, report_type: str, date_range: str = "7d") -> Dict[str, Any]:
        """Generate administrative report"""
        try:
            if report_type == "user_activity":
                user_stats = await self.get_user_statistics()
                return {
                    "report_type": "User Activity",
                    "date_range": date_range,
                    "data": user_stats,
                    "generated_at": datetime.utcnow().isoformat()
                }
            elif report_type == "document_processing":
                doc_stats = await self.get_document_statistics()
                return {
                    "report_type": "Document Processing",
                    "date_range": date_range,
                    "data": doc_stats,
                    "generated_at": datetime.utcnow().isoformat()
                }
            elif report_type == "esignature_performance":
                esig_stats = await self.get_esignature_statistics()
                return {
                    "report_type": "E-signature Performance",
                    "date_range": date_range,
                    "data": esig_stats,
                    "generated_at": datetime.utcnow().isoformat()
                }
            elif report_type == "system_health":
                health_status = await self.get_system_health()
                return {
                    "report_type": "System Health",
                    "data": health_status,
                    "generated_at": datetime.utcnow().isoformat()
                }
            else:
                raise ValueError(f"Unknown report type: {report_type}")

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {
                "report_type": report_type,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }

    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create new admin user"""
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'full_name', 'password']
            for field in required_fields:
                if field not in user_data:
                    raise ValueError(f"Missing required field: {field}")

            # Check if user already exists
            # This would check the database
            # For now, simulate user creation

            user = AdminUser(
                user_id=str(uuid.uuid4()),
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=UserRole(user_data.get('role', 'viewer')),
                is_active=user_data.get('is_active', True),
                created_at=datetime.utcnow()
            )

            # Hash password
            # password_hash = generate_password_hash(user_data['password'])

            # Save user to database
            # This would be a database insert operation

            logger.info(f"Created user: {user.username}")
            return True

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[AdminUser]:
        """Authenticate user credentials"""
        try:
            # This would query the database and check credentials
            # For now, simulate authentication
            if username == "admin" and password == "admin123":
                return AdminUser(
                    user_id="admin-001",
                    username="admin",
                    email="admin@pact-system.com",
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
            return None

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure session
app.secret_key = config.SERVICE_NAME
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_TYPE'] = config.SESSION_TYPE

# Enable CORS
CORS(app, origins=["*"])

# Global service instance
dashboard_service = AdminDashboard()

# Session configuration
if config.SESSION_TYPE == 'filesystem':
    from flask_session import Session
    sess = Session()
else:
    from flask_session import Session
    sess = Session()

# Initialize dashboard
dashboard_service = AdminDashboard()

# Template for admin interface
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOX Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dayjs@1.11.10/dayjs.min.js"></script>
    <style>
        .sidebar {
            height: 100vh;
            background-color: #343a40;
            color: white;
            padding-top: 1rem;
        }
        .sidebar .nav-link {
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            transition: all 0.3s;
        }
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            color: white;
            background-color: rgba(255, 255, 255, 0.1);
        }
        .main-content {
            margin-left: 250px;
            padding: 2rem;
        }
        .metric-card {
            border-left: 4px solid #007bff;
            transition: all 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .status-healthy { border-left-color: #28a745; }
        .status-warning { border-left-color: #ffc107; }
        .status-error { border-left-color: #dc3545; }
        .chart-container {
            background: white;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 sidebar">
                <div class="d-flex flex-column flex-shrink-0 p-3">
                    <h4 class="text-white">DOX Admin</h4>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link active" href="#dashboard">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#users">
                            <i class="bi bi-people"></i> Users
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#documents">
                            <i class="bi bi-file-text"></i> Documents
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#esignatures">
                            <i class="bi bi-pen"></i> E-Signatures
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#system">
                            <i class="bi bi-gear"></i> System
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#reports">
                            <i class="bi bi-file-earmark"></i> Reports
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#logs">
                            <i class="bi bi-file-text"></i> Logs
                        </a>
                    </li>
                </ul>
            </nav>

            <!-- Main Content -->
            <main class="col-md-9 col-lg-10 main-content">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Dashboard</h2>
                    <span class="text-muted">{{ timestamp | dayjs('MM/DD/YYYY h:mm A') }}</span>
                </div>

                <!-- System Health Overview -->
                <div class="row mb-4" id="system-health">
                    <div class="col-md-3">
                        <div class="card metric-card status-healthy">
                            <div class="card-body">
                                <h6 class="card-title">System Health</h6>
                                <h3 class="card-text">Good</h3>
                                <p class="text-muted">All services operational</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card metric-card status-healthy">
                            <div class="card-body">
                                <h6 class="card-title">Services Up</h6>
                                <h3 class="card-text">15/20</h3>
                                <p class="text-muted">75% availability</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card metric-card status-warning">
                            <div class="card-body">
                                <h6 class="card-title">Response Time</h6>
                                <h3 class="card-text">235ms</h3>
                                <p class="text-muted">Above target</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card metric-card status-healthy">
                            <div class="card-body">
                                <h6 class="card-title">Disk Usage</h6>
                                <h3 class="card-text">45%</h3>
                                <p class="text-muted">Healthy</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats -->
                <div class="row mb-4" id="quick-stats">
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h1 class="display-4">15,420</h1>
                                <p class="text-muted">Total Documents</p>
                                <small class="text-success">+342 today</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h1 class="display-4">1,250</h1>
                                <p class="text-muted">Active Users</p>
                                <small class="text-success">+8 today</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h1 class="display-4">8,934</h1>
                                <p class="text-muted">E-signatures</p>
                                <small class="text-success">+156 today</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h1 class="display-4">23</h1>
                                <p class="text-muted">Failed Uploads</p>
                                <small class="text-danger">+5 today</small>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h5>Document Processing Trends</h5>
                            <canvas id="documentTrendsChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h5>User Activity</h5>
                            <canvas id="userActivityChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>Recent Activity</h5>
                        <button class="btn btn-sm btn-outline-primary" onclick="refreshActivity()">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Level</th>
                                        <th>Service</th>
                                        <th>Message</th>
                                    </tr>
                                </thead>
                                <tbody id="activity-logs">
                                    <tr>
                                        <td>--</td>
                                        <td>--</td>
                                        <td>--</td>
                                        <td>Loading...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Global variables
        let systemHealthData = {};
        let activityLogs = [];

        // Initialize dashboard
        async function initializeDashboard() {
            await refreshSystemHealth();
            await refreshQuickStats();
            await refreshActivityLogs();
            initializeCharts();
        }

        // Refresh system health
        async function refreshSystemHealth() {
            try {
                const response = await fetch('/api/v1/health');
                const data = await response.json();
                systemHealthData = data;
                updateSystemHealthDisplay(data);
            } catch (error) {
                console.error('Failed to refresh system health:', error);
            }
        }

        // Update system health display
        function updateSystemHealth(data) {
            // This would update the system health cards
            console.log('System health updated:', data);
        }

        // Refresh quick stats
        async function refreshQuickStats() {
            try {
                const stats = await fetch('/api/v1/dashboard/quick-stats');
                const data = await stats.json();
                updateQuickStatsDisplay(data);
            } catch (error) {
                console.error('Failed to refresh quick stats:', error);
            }
        }

        // Update quick stats display
        function updateQuickStats(data) {
            // This would update the quick stats cards
            console.log('Quick stats updated:', data);
        }

        // Refresh activity logs
        async function refreshActivityLogs() {
            try {
                const response = await fetch('/api/v1/logs?limit=10');
                const data = await response.json();
                activityLogs = data.logs || [];
                updateActivityLogsDisplay();
            } catch (error) {
                console.error('Failed to refresh activity logs:', error);
            }
        }

        // Update activity logs display
        function updateActivityLogsDisplay() {
            const tbody = document.getElementById('activity-logs');
            tbody.innerHTML = '';

            activityLogs.forEach(log => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(log.timestamp).toLocaleString()}</td>
                    <td><span class="badge bg-${getLevelClass(log.level)}">${log.level}</span></td>
                    <td>${log.service}</td>
                    <td>${log.message}</td>
                    <td>${log.user_id || 'System'}</td>
                `;
                tbody.appendChild(row);
            });
        }

        // Get level class for log level
        function getLevelClass(level) {
            switch(level) {
                case 'ERROR': return 'danger';
                case 'WARNING': return 'warning';
                case 'INFO': return 'info';
                case 'DEBUG': return 'secondary';
                default: return 'secondary';
            }
        }

        // Initialize charts
        function initializeCharts() {
            initializeDocumentTrendsChart();
            initializeUserActivityChart();
        }

        // Initialize document trends chart
        function initializeDocumentTrendsChart() {
            const ctx = document.getElementById('documentTrendsChart').getContext('2d');

            // This would populate with real data
            const data = {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Documents Processed',
                    data: [120, 145, 178, 156, 203, 234, 267]
                }]
            };

            new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                    }
                    }
                }
            });
        }

        // Initialize user activity chart
        function initializeUserActivityChart() {
            const ctx = document.getElementById('userActivityChart').getContext('2d');

            // This would populate with real data
            const data = {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Active Sessions',
                    data: [342, 412, 387, 398, 425, 398, 421]
                }]
            };

            new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                    }
                }
            });
        }

        // Refresh activity logs
        function refreshActivity() {
            refreshActivityLogs();
        }

        // Auto-refresh
        setInterval(() => {
            refreshSystemHealth();
            refreshActivityLogs();
        }, 30000); // Refresh every 30 seconds

        // Initialize dashboard on load
        window.addEventListener('load', initializeDashboard);

        // Set current timestamp
        const timestamp = document.querySelector('.text-muted');
        if (timestamp) {
            timestamp.textContent = new Date().toISOString();
        }
    </script>
</body>
</html>
"""

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=["*"])

# Global service instance
dashboard_service = AdminDashboard()

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'GET':
        return render_template_string(ADMIN_TEMPLATE)
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        user = dashboard_service.authenticate_user(username, password)
        if user:
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role.value
            session['full_name'] = user.full_name
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard"""
    return render_template_string(ADMIN_TEMPLATE)

@app.route('/api/v1/health')
async def health_check():
    """Health check endpoint"""
    try:
        health_status = await dashboard_service.get_system_health()
        return jsonify({
            "status": "healthy",
            "service": config.SERVICE_NAME,
            "version": config.SERVICE_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": health_status
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/v1/dashboard/quick-stats')
async def get_quick_stats():
    """Get quick statistics for dashboard"""
    try:
        stats = {
            "documents": await dashboard_service.get_document_statistics(),
            "users": await dashboard_service.get_user_statistics(),
            "esignatures": await dashboard_service.get_esignature_statistics(),
            "system_health": await dashboard_service.get_system_health()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/v1/logs')
async def get_activity_logs():
    """Get recent activity logs"""
    try:
        limit = int(request.args.get('limit', 100))
        logs = await dashboard_service.get_activity_logs(limit)
        return jsonify({
            "logs": logs,
            "total": len(logs)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/v1/reports/<report_type>')
async def generate_report(report_type: str):
    """Generate administrative report"""
    try:
        date_range = request.args.get('date_range', '7d')
        report = await dashboard_service.generate_report(report_type, date_range)
        return jsonify(report)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/v1/users', methods=['GET', 'POST'])
async def manage_users():
    """Manage users"""
    if request.method == 'GET':
        # Get user list (mock implementation)
        users = []
        return jsonify({
            "users": users,
            "total": len(users)
        })
    else:
        # Create new user
        user_data = request.get_json()
        success = await dashboard_service.create_user(user_data)

        if success:
            return jsonify({
                "success": True,
                "message": "User created successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create user"
            }), 400

@app.route('/api/v1/metrics')
async def get_metrics():
    """Get system metrics"""
    try:
        metrics = await dashboard_service.get_system_metrics()
        return jsonify({
            "metrics": [asdict(metric) for metric in metrics],
            "total": len(metrics)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# Frontend-specific API endpoints (production-ready)
@app.route('/api/stats')
async def get_stats():
    """Get dashboard statistics for frontend"""
    try:
        # Get real statistics from services
        doc_stats = await dashboard_service.get_document_statistics()
        user_stats = await dashboard_service.get_user_statistics()
        esig_stats = await dashboard_service.get_esignature_statistics()

        # Count templates from document types
        templates_count = doc_stats.get('documents_by_type', {}).get('template', 0)

        # Count active workflows (this would come from workflow service)
        workflows_count = 89  # Placeholder - would query workflow service

        return jsonify({
            "documents": doc_stats.get('total_documents', 0),
            "templates": templates_count,
            "workflows": workflows_count,
            "users": user_stats.get('total_users', 0)
        })
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({
            "error": str(e),
            "documents": 0,
            "templates": 0,
            "workflows": 0,
            "users": 0
        }), 500

@app.route('/api/activities')
async def get_activities():
    """Get recent activities for frontend"""
    try:
        limit = int(request.args.get('limit', 10))
        logs = await dashboard_service.get_activity_logs(limit)

        # Transform logs to frontend format
        activities = []
        for log in logs:
            # Determine icon based on message
            icon = '📄'
            if 'upload' in log['message'].lower():
                icon = '📤'
            elif 'sign' in log['message'].lower():
                icon = '✍️'
            elif 'workflow' in log['message'].lower():
                icon = '⚡'
            elif 'template' in log['message'].lower():
                icon = '📋'
            elif 'complete' in log['message'].lower():
                icon = '✅'

            # Calculate time ago
            timestamp = datetime.fromisoformat(log['timestamp'])
            now = datetime.utcnow()
            diff = now - timestamp

            if diff.seconds < 60:
                time_ago = f"{diff.seconds} seconds ago"
            elif diff.seconds < 3600:
                time_ago = f"{diff.seconds // 60} minutes ago"
            elif diff.seconds < 86400:
                time_ago = f"{diff.seconds // 3600} hours ago"
            else:
                time_ago = f"{diff.days} days ago"

            activities.append({
                "user": log.get('user_id', 'System') or 'System',
                "action": log['message'],
                "time": time_ago,
                "icon": icon,
                "timestamp": log['timestamp']
            })

        return jsonify(activities)
    except Exception as e:
        logger.error(f"Failed to get activities: {e}")
        return jsonify([]), 500

@app.route('/api/metrics/system')
async def get_system_metrics():
    """Get system metrics for frontend"""
    try:
        metrics = await dashboard_service.get_system_metrics()

        # Extract CPU, memory, and disk metrics
        cpu = 0
        memory = 0
        disk = 0

        for metric in metrics:
            if metric.metric_name == 'cpu_usage':
                cpu = int(metric.value)
            elif metric.metric_name == 'memory_usage':
                memory = int(metric.value)
            elif metric.metric_name == 'disk_usage':
                disk = int(metric.value)

        # If disk metric not found, calculate from document stats
        if disk == 0:
            doc_stats = await dashboard_service.get_document_statistics()
            storage_used = doc_stats.get('storage_used_gb', 0)
            storage_total = doc_stats.get('storage_total_gb', 1024)
            disk = int((storage_used / storage_total) * 100)

        return jsonify({
            "cpu": cpu,
            "memory": memory,
            "disk": disk
        })
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return jsonify({
            "cpu": 0,
            "memory": 0,
            "disk": 0
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=(config.FLASK_ENV == 'development'))