# DOX Validation Service Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    clamav \
    clamav-freshclam \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Update ClamAV database
RUN freshclam

# Copy application files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash dox && chown -R dox:dox /app
USER dox

# Expose port
EXPOSE 5007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5007/health || exit 1

# Default command
CMD ["python", "-m", "app"]