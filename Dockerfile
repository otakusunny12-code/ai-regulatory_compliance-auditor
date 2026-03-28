# AI Regulatory Compliance Auditor - Docker Configuration
# Multi-stage build for optimized production image

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 auditor && \
    chown -R auditor:auditor /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY compliance_env/ ./compliance_env/
COPY inference.py .
COPY openenv.yaml .
COPY requirements.txt .

# Set ownership
RUN chown -R auditor:auditor /app

# Switch to non-root user
USER auditor

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from compliance_env.env import ComplianceAuditorEnvironment; env = ComplianceAuditorEnvironment(); print('OK')" || exit 1

# Default command runs inference on all tasks
CMD ["python", "inference.py"]