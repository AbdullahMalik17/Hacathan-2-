# Abdullah Junior - Digital FTE Backend
# Optimized for Fly.io deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/.env.example ./config/.env.example
COPY Vault/ ./Vault/

# Create necessary directories
RUN mkdir -p config/push_notifications Vault/Logs Vault/Needs_Action Vault/Pending_Approval Vault/Done

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FTE_ROLE=cloud
ENV LOG_LEVEL=INFO

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the API server
CMD ["uvicorn", "src.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
