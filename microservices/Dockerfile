# Dockerfile for PDF Microservices
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy microservices requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy microservices code
COPY . .

# Create necessary directories
RUN mkdir -p temp output

# Expose ports for services
# Orchestrator: 8000
# Merge: 8001
# Rotate: 8002
# Split: 8003
EXPOSE 8000 8001 8002 8003

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check for orchestrator
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command to start services
CMD ["python", "start_services.py"]
