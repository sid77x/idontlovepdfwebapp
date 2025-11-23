# Docker Setup Guide for IdontLovePDF

This guide explains how to run IdontLovePDF using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose 2.0 or later
- At least 4GB of RAM available for Docker
- 10GB of free disk space

## Quick Start

### Production Deployment

Run all services in production mode:

```bash
docker-compose up -d
```

This will start:
- **Streamlit App** on http://localhost:8501
- **Microservices API** on http://localhost:8000
- **React Frontend** on http://localhost:3000

### Development Mode

For development with hot-reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

## Architecture

The application consists of three main services:

### 1. Streamlit Application (Main UI)
- **Port**: 8501
- **Purpose**: Main web interface for PDF manipulation
- **Features**: All PDF tools (merge, split, rotate, compress, OCR, etc.)

### 2. Microservices Backend
- **Orchestrator Port**: 8000
- **Merge Service**: 8001
- **Rotate Service**: 8002
- **Split Service**: 8003
- **Purpose**: FastAPI-based microservices for PDF operations
- **API Docs**: http://localhost:8000/docs

### 3. React Frontend (Optional)
- **Port**: 3000
- **Purpose**: Alternative modern frontend interface

## Service Management

### Start All Services
```bash
docker-compose up -d
```

### Start Specific Service
```bash
# Start only Streamlit app
docker-compose up -d streamlit-app

# Start only microservices
docker-compose up -d microservices

# Start only frontend
docker-compose up -d frontend
```

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f streamlit-app
docker-compose logs -f microservices
docker-compose logs -f frontend
```

### Restart Services
```bash
docker-compose restart
```

## Building Images

### Build All Images
```bash
docker-compose build
```

### Build Specific Service
```bash
docker-compose build streamlit-app
docker-compose build microservices
docker-compose build frontend
```

### Rebuild Without Cache
```bash
docker-compose build --no-cache
```

## Environment Variables

You can customize the deployment using environment variables:

### Streamlit App
- `STREAMLIT_SERVER_PORT`: Port for Streamlit (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Bind address (default: 0.0.0.0)

### Microservices
- `PDF_HOST`: Host for services (default: 0.0.0.0)
- `PDF_BASE_PORT`: Starting port number (default: 8000)
- `PDF_MAX_FILE_SIZE`: Max upload size in MB (default: 100)
- `PDF_REQUEST_TIMEOUT`: Request timeout in seconds (default: 300)

### Creating .env File

Create a `.env` file in the root directory:

```env
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Microservices Configuration
PDF_HOST=0.0.0.0
PDF_BASE_PORT=8000
PDF_MAX_FILE_SIZE=100
PDF_REQUEST_TIMEOUT=300

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

## Volume Management

The application uses volumes for persistent data:

### Temporary Files
- `./temp`: Temporary upload files
- `./output`: Processed output files

### Custom Volume Mounts

Edit `docker-compose.yml` to customize volume mounts:

```yaml
volumes:
  - ./custom-temp:/app/temp
  - ./custom-output:/app/output
```

## Health Checks

All services include health checks:

### Check Service Health
```bash
# Streamlit app
curl http://localhost:8501/_stcore/health

# Microservices orchestrator
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

### View Health Status
```bash
docker-compose ps
```

## Networking

Services communicate through a custom bridge network called `pdfnet`.

### Service URLs (Internal)
- Streamlit: `http://streamlit-app:8501`
- Orchestrator: `http://microservices:8000`
- Frontend: `http://frontend:80`

## Troubleshooting

### Port Already in Use

If you get port binding errors:

```bash
# Change ports in docker-compose.yml
# For example, change 8501:8501 to 8502:8501
```

Or stop the conflicting service:

```bash
# Find process using port
lsof -i :8501

# Kill the process
kill -9 <PID>
```

### Permission Issues

If you encounter permission errors:

```bash
# Fix ownership
sudo chown -R $USER:$USER temp/ output/

# Or run with sudo (not recommended)
sudo docker-compose up -d
```

### Out of Memory

If services crash due to memory:

```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or limit service memory in docker-compose.yml
services:
  streamlit-app:
    mem_limit: 2g
```

### Service Won't Start

Check logs for errors:

```bash
docker-compose logs streamlit-app
docker-compose logs microservices
```

Rebuild images:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### OCR Not Working

OCR requires Tesseract, which is included in the Docker image. If it's not working:

1. Check if Tesseract is installed:
```bash
docker-compose exec streamlit-app tesseract --version
```

2. Verify language files:
```bash
docker-compose exec streamlit-app ls /usr/share/tesseract-ocr/*/tessdata
```

## Production Deployment

### Security Best Practices

1. **Use secrets for sensitive data**:
```yaml
services:
  streamlit-app:
    secrets:
      - app_secret
secrets:
  app_secret:
    file: ./secrets/app_secret.txt
```

2. **Run as non-root user**:
Add to Dockerfile:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

3. **Limit resources**:
```yaml
services:
  streamlit-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Using Docker Swarm

For production clustering:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml pdfapp

# Scale services
docker service scale pdfapp_microservices=3

# Remove stack
docker stack rm pdfapp
```

### Using Kubernetes

Convert to Kubernetes manifests:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.31.2/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert
kompose convert -f docker-compose.yml

# Deploy
kubectl apply -f .
```

## Performance Optimization

### Multi-stage Builds

The Dockerfiles use multi-stage builds to reduce image size:
- Frontend: ~50MB (nginx + static files)
- Backend: ~1.5GB (Python + dependencies + Tesseract)

### Image Caching

Speed up builds by ordering Dockerfile commands:
1. System dependencies
2. Requirements files
3. Application code

### Resource Limits

Set appropriate limits based on usage:

```yaml
services:
  streamlit-app:
    cpus: 2
    mem_limit: 2g
    mem_reservation: 1g
```

## Monitoring

### View Resource Usage
```bash
docker stats
```

### Export Logs
```bash
docker-compose logs --no-color > app.log
```

### Integrate with Monitoring Tools

- **Prometheus**: Add metrics exporters
- **Grafana**: Create dashboards
- **ELK Stack**: Centralized logging

## Backup and Restore

### Backup Volumes
```bash
docker run --rm -v idontlovepdfwebapp_temp:/data -v $(pwd):/backup alpine tar czf /backup/temp-backup.tar.gz /data
```

### Restore Volumes
```bash
docker run --rm -v idontlovepdfwebapp_temp:/data -v $(pwd):/backup alpine tar xzf /backup/temp-backup.tar.gz -C /
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: docker-compose build
      - name: Run tests
        run: docker-compose up -d && sleep 10 && curl -f http://localhost:8501
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Docker Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

## Support

For issues specific to Docker deployment:
1. Check the logs: `docker-compose logs`
2. Verify health: `docker-compose ps`
3. Open an issue on GitHub with logs and configuration
