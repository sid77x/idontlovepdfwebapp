# PDF Microservices Architecture

## Overview

This project transforms the monolithic PDF tool suite into a microservices architecture using FastAPI. Each PDF operation runs as an independent service that can be scaled, deployed, and maintained separately.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Orchestrator  │    │  Merge Service  │    │ Rotate Service  │
│   Port: 8000    │────│   Port: 8001    │    │   Port: 8002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        
         └─────────────────┐      ┌─────────────────┐    
                          │      │  Split Service  │    
                          └──────│   Port: 8003    │    
                                 └─────────────────┘    
```

### Components

- **Orchestrator (Port 8000)**: Central service that coordinates all PDF operations
- **Merge Service (Port 8001)**: Handles PDF merging operations
- **Rotate Service (Port 8002)**: Handles PDF page rotation
- **Split Service (Port 8003)**: Handles PDF splitting operations
- **More services**: Additional services can be added for each PDF operation

## Features

### ✅ Implemented Services
- **PDF Merge**: Combine multiple PDF files into one
- **PDF Rotate**: Rotate specific pages or entire documents  
- **PDF Split**: Split PDFs by pages or page ranges
- **Service Discovery**: Automatic discovery and health monitoring
- **Load Balancing**: Route requests to healthy service instances

### 🚧 Coming Soon
- PDF Protection/Unlock
- PDF Compression
- Watermarking
- Page Numbers
- Cropping
- Format Conversion (PDF ↔ Word, Excel, etc.)
- OCR Services

## Quick Start

### 1. Install Dependencies

**Windows:**
```cmd
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**Manual installation:**
```bash
pip install -r requirements.txt
```

### 2. Start All Services

```bash
python start_services.py
```

This will start:
- Orchestrator at http://localhost:8000
- All PDF microservices on their respective ports

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Service Status**: http://localhost:8000/health
- **Available Services**: http://localhost:8000/services

## API Usage Examples

### Upload Files
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Merge PDFs
```bash
curl -X POST "http://localhost:8000/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "file_names": ["document1.pdf", "document2.pdf"],
    "output_filename": "merged_document.pdf"
  }'
```

### Rotate PDF Pages
```bash
curl -X POST "http://localhost:8000/rotate" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "document.pdf",
    "rotation_angle": 90,
    "pages": "1-3,5"
  }'
```

### Split PDF
```bash
curl -X POST "http://localhost:8000/split" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "document.pdf",
    "split_type": "ranges",
    "split_value": "1-3,5-7,10"
  }'
```

## Individual Service Usage

Each service can also be accessed directly:

### Merge Service (Port 8001)
```bash
curl -X POST "http://localhost:8001/merge" \
  -H "Content-Type: application/json" \
  -d '{"file_names": ["doc1.pdf", "doc2.pdf"]}'
```

### Rotate Service (Port 8002)  
```bash
curl -X POST "http://localhost:8002/rotate" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "doc.pdf", "rotation_angle": 180}'
```

## Architecture Benefits

### 🎯 **Scalability**
- Scale individual services based on demand
- Add multiple instances of high-usage services
- Independent resource allocation

### 🔧 **Maintainability**
- Isolated codebases for each operation
- Independent deployment and updates
- Easier testing and debugging

### 🚀 **Performance**
- Parallel processing of different operations
- Service-specific optimizations
- Reduced resource contention

### 🛡️ **Resilience**
- Service failure isolation
- Automatic health monitoring
- Service restart capabilities

## Service Development

### Adding a New Service

1. **Create service class** extending `BasePDFMicroservice`:
```python
from common import BasePDFMicroservice, PDFOperationType

class MyPDFService(BasePDFMicroservice):
    def __init__(self, host="localhost", port=8004):
        super().__init__(
            service_name="my_operation",
            operation_type=PDFOperationType.MY_OPERATION,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        @self.app.post("/my-endpoint")
        async def my_operation(request: MyRequest):
            # Implementation here
            pass
```

2. **Register in orchestrator** (`orchestrator/main.py`):
```python
self.known_services = {
    # ... existing services
    PDFOperationType.MY_OPERATION: [{"host": "localhost", "port": 8004}],
}
```

3. **Update service manager** (`start_services.py`):
```python
self.service_configs = {
    # ... existing services  
    "my_service": ("my_service.py", 8004),
}
```

## Configuration

### Environment Variables

- `PDF_HOST`: Host for services (default: localhost)
- `PDF_BASE_PORT`: Starting port number (default: 8000)
- `PDF_MAX_FILE_SIZE`: Maximum upload file size in MB (default: 100)
- `PDF_REQUEST_TIMEOUT`: Request timeout in seconds (default: 300)

### Service Ports

| Service | Default Port |
|---------|-------------|
| Orchestrator | 8000 |
| Merge | 8001 |
| Rotate | 8002 |
| Split | 8003 |
| Protect | 8004 |
| Compress | 8005 |

## Monitoring & Health Checks

### Health Endpoints

- **Orchestrator Health**: `GET /health`
- **Service Health**: `GET http://localhost:{port}/health`
- **Service Info**: `GET http://localhost:{port}/info`

### Service Discovery

The orchestrator automatically:
- Discovers available services on startup
- Monitors service health every 10 seconds
- Routes requests only to healthy services
- Provides service failover capabilities

## File Management

### Upload Directory Structure
```
temp/
├── orchestrator/     # Orchestrator uploads
├── merge/           # Merge service files  
├── rotate/          # Rotate service files
└── split/           # Split service files
```

### Output Directory Structure  
```
output/
├── merge/           # Merged PDF outputs
├── rotate/          # Rotated PDF outputs
└── split/           # Split PDF outputs (zip files)
```

## Error Handling

Services provide consistent error responses:
```json
{
  "success": false,
  "message": "Operation failed",
  "error_details": "Detailed error information",
  "processing_time_ms": 1234
}
```

## Security Considerations

- File upload size limits
- Temporary file cleanup
- Input validation on all endpoints  
- No persistent file storage (files are processed and removed)

## Performance Tips

1. **Upload files once** to orchestrator, then reference by filename
2. **Use appropriate split types** (pages vs ranges) based on needs
3. **Monitor service health** for optimal routing
4. **Scale services independently** based on usage patterns

## Troubleshooting

### Common Issues

**Services won't start:**
- Check if ports are already in use
- Verify Python dependencies are installed
- Check file permissions on script files

**File not found errors:**
- Ensure files are uploaded before processing
- Check file names match exactly (case-sensitive)
- Verify sufficient disk space for uploads

**Service communication errors:**
- Check service health endpoints
- Verify network connectivity between services
- Review orchestrator logs for routing issues

### Logs Location

Each service logs to console. For production deployment, configure proper logging:
- Service-specific log files
- Centralized logging (ELK stack, etc.)
- Log rotation and retention policies

## Next Steps

1. **Add remaining PDF services** (compress, watermark, etc.)
2. **Implement authentication** for production use
3. **Add database integration** for job tracking
4. **Create Docker containers** for easy deployment
5. **Set up monitoring** (Prometheus, Grafana)
6. **Implement rate limiting** and throttling
7. **Add async job processing** for large files