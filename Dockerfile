# Production Multi-Stage Dockerfile for AI Fleet Digital Twin
FROM python:3.13-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_CONFIG=production \
    PORT=5000

WORKDIR /app

# Install system dependencies (build-essential needed for some C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application source code
COPY . .

# Initialize SQLite database if not present
RUN python database/init_db.py

# Create unprivileged user for security
RUN useradd -m -u 1000 fleetuser && \
    mkdir -p logs database data && \
    chown -R fleetuser:fleetuser /app

USER fleetuser

EXPOSE 5000

# Health check to ensure application is responsive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/fleet/summary || exit 1

# Launch production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "wsgi:application"]
