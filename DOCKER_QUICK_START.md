# Docker Quick Start Guide

Get IdontLovePDF running in Docker in 3 simple steps!

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/sid77x/idontlovepdfwebapp.git
cd idontlovepdfwebapp
```

### Step 2: Start the Application
```bash
# Linux/Mac
./docker-start.sh

# Windows
docker-start.bat

# Or use docker compose directly
docker compose up -d
```

### Step 3: Access the Application
- **Streamlit App** (Main UI): http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **React Frontend**: http://localhost:3000

## 📋 Common Commands

### Check Status
```bash
./docker-start.sh status
# or
docker compose ps
```

### View Logs
```bash
./docker-start.sh logs
# or
docker compose logs -f
```

### Stop Services
```bash
./docker-start.sh stop
# or
docker compose down
```

### Restart Services
```bash
./docker-start.sh restart
# or
docker compose restart
```

## 🔧 Development Mode

For development with hot-reload:
```bash
./docker-start.sh dev
# or
docker compose -f docker-compose.dev.yml up
```

## 📦 What's Running?

The application consists of three main services:

1. **Streamlit App** (Port 8501)
   - Main PDF manipulation interface
   - All PDF tools in one place
   - OCR, conversion, and more

2. **Microservices** (Port 8000-8003)
   - FastAPI backend
   - Individual services for each operation
   - API documentation at /docs

3. **React Frontend** (Port 3000)
   - Modern alternative UI
   - Optional component

## 🛠️ Troubleshooting

### Services won't start?
```bash
# Check if ports are in use
lsof -i :8501
lsof -i :8000

# Rebuild images
docker compose build --no-cache
docker compose up -d
```

### See more logs?
```bash
docker compose logs -f streamlit-app
docker compose logs -f microservices
```

### Clean everything and start fresh?
```bash
./docker-start.sh clean
./docker-start.sh
```

## 📚 More Information

For comprehensive documentation including:
- Environment configuration
- Production deployment
- CI/CD integration
- Performance optimization

See [DOCKER.md](DOCKER.md)

## 🎯 Key Features

✅ **Privacy-First**: All processing happens locally  
✅ **No Installation**: Just Docker required  
✅ **Cross-Platform**: Works on Linux, Mac, Windows  
✅ **Full Featured**: All PDF operations included  
✅ **Easy Updates**: `git pull && docker compose up -d`  

---

**Need Help?** Check [DOCKER.md](DOCKER.md) or open an issue!
