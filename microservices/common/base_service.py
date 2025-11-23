"""Base microservice class with common functionality."""
import os
import time
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from .models import (
    ServiceInfo, HealthCheckResponse, ServiceStatus, 
    PDFOperationType, PDFProcessingResponse
)


class BasePDFMicroservice(ABC):
    """Base class for PDF microservices."""
    
    def __init__(
        self,
        service_name: str,
        operation_type: PDFOperationType,
        host: str = "localhost",
        port: int = 8000,
        version: str = "1.0.0"
    ):
        self.service_id = f"{service_name}-{uuid.uuid4().hex[:8]}"
        self.service_name = service_name
        self.operation_type = operation_type
        self.host = host
        self.port = port
        self.version = version
        self.start_time = time.time()
        self.status = ServiceStatus.STARTING
        
        # Create FastAPI app
        self.app = FastAPI(
            title=f"PDF {service_name.title()} Service",
            description=f"Microservice for PDF {service_name.lower()} operations",
            version=version
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"pdf-{service_name}")
        
        # Create directories
        self.upload_dir = f"temp/{service_name}"
        self.output_dir = f"output/{service_name}"
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Register routes
        self._register_routes()
        
        # Set status to healthy after initialization
        self.status = ServiceStatus.HEALTHY
    
    def _register_routes(self):
        """Register common routes for the service."""
        
        @self.app.get("/health", response_model=HealthCheckResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthCheckResponse(
                service_id=self.service_id,
                status=self.status,
                timestamp=datetime.utcnow().isoformat(),
                uptime_seconds=time.time() - self.start_time,
                version=self.version,
                details={
                    "service_name": self.service_name,
                    "operation_type": self.operation_type.value,
                    "upload_dir": self.upload_dir,
                    "output_dir": self.output_dir
                }
            )
        
        @self.app.get("/info", response_model=ServiceInfo)
        async def service_info():
            """Get service information."""
            return ServiceInfo(
                service_id=self.service_id,
                name=self.service_name,
                version=self.version,
                description=f"PDF {self.service_name.lower()} microservice",
                operation_type=self.operation_type,
                host=self.host,
                port=self.port,
                status=self.status,
                endpoints=self._get_endpoints()
            )
        
        @self.app.post("/upload")
        async def upload_file(file: UploadFile = File(...)):
            """Upload a file for processing."""
            try:
                # Save uploaded file
                file_path = os.path.join(self.upload_dir, file.filename)
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                file_size_mb = len(content) / (1024 * 1024)
                
                self.logger.info(f"File uploaded: {file.filename} ({file_size_mb:.2f} MB)")
                
                return {
                    "success": True,
                    "message": f"File {file.filename} uploaded successfully",
                    "file_name": file.filename,
                    "file_size_mb": file_size_mb,
                    "upload_path": file_path
                }
            except Exception as e:
                self.logger.error(f"Upload failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        @self.app.get("/download/{file_name}")
        async def download_file(file_name: str):
            """Download a processed file."""
            file_path = os.path.join(self.output_dir, file_name)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            return FileResponse(
                path=file_path,
                filename=file_name,
                media_type='application/octet-stream'
            )
        
        # Register service-specific routes
        self._register_service_routes()
    
    @abstractmethod
    def _register_service_routes(self):
        """Register service-specific routes. To be implemented by subclasses."""
        pass
    
    def _get_endpoints(self) -> list:
        """Get list of available endpoints."""
        endpoints = ["/health", "/info", "/upload", "/download/{file_name}"]
        endpoints.extend(self._get_service_endpoints())
        return endpoints
    
    @abstractmethod
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints. To be implemented by subclasses."""
        return []
    
    def create_response(
        self,
        success: bool,
        message: str,
        file_url: Optional[str] = None,
        file_size_mb: Optional[float] = None,
        processing_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error_details: Optional[str] = None
    ) -> PDFProcessingResponse:
        """Create a standardized processing response."""
        return PDFProcessingResponse(
            success=success,
            message=message,
            file_url=file_url,
            file_size_mb=file_size_mb,
            processing_time_ms=processing_time_ms,
            metadata=metadata,
            error_details=error_details
        )
    
    def get_file_path(self, filename: str, is_output: bool = False) -> str:
        """Get full path for a file."""
        directory = self.output_dir if is_output else self.upload_dir
        return os.path.join(directory, filename)
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB."""
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return 0.0
    
    def cleanup_temp_files(self, *file_paths: str):
        """Clean up temporary files."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {file_path}: {str(e)}")
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """Run the microservice."""
        host = host or self.host
        port = port or self.port
        
        self.logger.info(f"Starting {self.service_name} service on {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )


def create_microservice_app(service_class, **kwargs) -> FastAPI:
    """Factory function to create a microservice app."""
    service = service_class(**kwargs)
    return service.app