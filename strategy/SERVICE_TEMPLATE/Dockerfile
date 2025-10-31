# Pact Platform Service - Standard Dockerfile Template
# Supports both Python Flask and Node.js services

# ============= PYTHON FLASK BACKEND =============
# Uncomment for backend services

FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies for PDF/image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpoppler-cpp-dev \
    pdftk-java \
    ghostscript \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp0 \
    pdftk-java \
    ghostscript \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set Python path
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Port
EXPOSE 5000

# Run application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]


# ============= NODE.JS FRONTEND =============
# Uncomment for frontend services and comment out Python section above

# FROM node:18-alpine as builder
#
# WORKDIR /app
#
# COPY app/package*.json .
#
# RUN npm ci --only=dependencies
#
# # Runtime stage
# FROM node:18-alpine
#
# WORKDIR /app
#
# COPY --from=builder /app/node_modules ./node_modules
#
# COPY app/ .
#
# # Create non-root user
# RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser
# USER appuser
#
# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"
#
# EXPOSE 3000
#
# CMD ["npm", "start"]


# ============= BUILD INSTRUCTIONS =============
# docker build -t [service-name]:latest .
# docker run -p 5000:5000 [service-name]:latest
