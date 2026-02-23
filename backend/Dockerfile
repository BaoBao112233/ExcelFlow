# Backend Dockerfile - FastAPI + Vertex AI
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies including Vertex AI
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir google-cloud-aiplatform>=1.60.0

# Copy application code
COPY . .

# Create directory for service account (will be mounted)
RUN mkdir -p /app/credentials

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
