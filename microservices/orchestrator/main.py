"""PDF Microservices Orchestrator."""
import os
import time
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from pydantic import BaseModel
import uvicorn

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import (
    ServiceRegistry, ServiceInfo, ServiceStatus, PDFOperationType,
    HealthCheckResponse, PDFProcessingResponse, 
    MergeRequest, RotateRequest, SplitRequest, ProtectRequest, UnlockRequest,
    CompressRequest, WatermarkRequest, PageNumbersRequest, CropRequest,
    ConversionRequest, OCRRequest
)


class OrchestratorConfig(BaseModel):
    """Orchestrator configuration."""
    host: str = "localhost"
    port: int = 8000
    service_discovery_interval: int = 30
    health_check_interval: int = 10
    request_timeout: int = 300
    max_file_size_mb: int = 100


class PDFOrchestrator:
    """Main orchestrator for PDF microservices."""
    
    def __init__(self, config: OrchestratorConfig = None):
        self.config = config or OrchestratorConfig()
        self.service_registry = ServiceRegistry()
        self.app = FastAPI(
            title="PDF Microservices Orchestrator",
            description="Central orchestrator for PDF manipulation microservices",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # HTTP client for service communication
        self.http_client = httpx.AsyncClient(timeout=self.config.request_timeout)
        
        # Service discovery configuration
        self.known_services = {
            PDFOperationType.MERGE: [{"host": "localhost", "port": 8001}],
            PDFOperationType.ROTATE: [{"host": "localhost", "port": 8002}],
            PDFOperationType.SPLIT: [{"host": "localhost", "port": 8003}],
            PDFOperationType.PROTECT: [{"host": "localhost", "port": 8004}],
            PDFOperationType.COMPRESS: [{"host": "localhost", "port": 8005}],
            PDFOperationType.WATERMARK: [{"host": "localhost", "port": 8006}],
            PDFOperationType.PAGE_NUMBERS: [{"host": "localhost", "port": 8007}],
            PDFOperationType.CROP: [{"host": "localhost", "port": 8008}],
            PDFOperationType.REPAIR: [{"host": "localhost", "port": 8009}],
            PDFOperationType.OCR: [{"host": "localhost", "port": 8010}],
            PDFOperationType.PDF_TO_IMAGE: [{"host": "localhost", "port": 8011}],
            PDFOperationType.IMAGE_TO_PDF: [{"host": "localhost", "port": 8012}],
            PDFOperationType.PDF_TO_WORD: [{"host": "localhost", "port": 8013}],
            PDFOperationType.WORD_TO_PDF: [{"host": "localhost", "port": 8014}],
            PDFOperationType.PDF_TO_EXCEL: [{"host": "localhost", "port": 8015}],
            PDFOperationType.EXCEL_TO_PDF: [{"host": "localhost", "port": 8016}],
            PDFOperationType.PDF_TO_HTML: [{"host": "localhost", "port": 8017}],
            PDFOperationType.HTML_TO_PDF: [{"host": "localhost", "port": 8018}],
            PDFOperationType.PDF_TO_POWERPOINT: [{"host": "localhost", "port": 8019}],
            PDFOperationType.POWERPOINT_TO_PDF: [{"host": "localhost", "port": 8020}],
        }
        
        # Create directories
        os.makedirs("temp/orchestrator", exist_ok=True)
        
        # Register routes
        self._register_routes()
        
        # Register startup event to create background tasks
        @self.app.on_event("startup")
        async def startup_event():
            """Start background tasks when the app starts."""
            asyncio.create_task(self._service_discovery_loop())
            asyncio.create_task(self._health_check_loop())
    
    def _register_routes(self):
        """Register orchestrator routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information."""
            return {
                "service": "PDF Microservices Orchestrator",
                "version": "1.0.0",
                "status": "running",
                "available_operations": [op.value for op in PDFOperationType],
                "registered_services": len(self.service_registry.services)
            }
        
        @self.app.get("/health")
        async def health():
            """Orchestrator health check."""
            healthy_services = len(self.service_registry.get_healthy_services())
            total_services = len(self.service_registry.services)
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "services": {
                    "total": total_services,
                    "healthy": healthy_services,
                    "unhealthy": total_services - healthy_services
                }
            }
        
        @self.app.get("/services", response_model=List[ServiceInfo])
        async def list_services():
            """List all registered services."""
            return list(self.service_registry.services.values())
        
        @self.app.get("/services/{operation_type}")
        async def get_services_by_type(operation_type: str):
            """Get services for a specific operation type."""
            try:
                op_type = PDFOperationType(operation_type)
                services = self.service_registry.get_services_by_type(op_type)
                return services
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid operation type: {operation_type}")
        
        # File upload endpoint
        @self.app.post("/upload")
        async def upload_files(files: List[UploadFile] = File(...)):
            """Upload files to be processed."""
            uploaded_files = []
            
            for file in files:
                # Check file size
                content = await file.read()
                if len(content) > self.config.max_file_size_mb * 1024 * 1024:
                    raise HTTPException(
                        status_code=413, 
                        detail=f"File {file.filename} too large. Max size: {self.config.max_file_size_mb}MB"
                    )
                
                # Save file
                file_path = f"temp/orchestrator/{file.filename}"
                with open(file_path, "wb") as f:
                    f.write(content)
                
                uploaded_files.append({
                    "filename": file.filename,
                    "size_mb": len(content) / (1024 * 1024),
                    "path": file_path
                })
            
            return {
                "success": True,
                "message": f"Uploaded {len(uploaded_files)} files",
                "files": uploaded_files
            }
        
        # PDF Operations endpoints
        @self.app.post("/merge")
        async def merge_pdfs(files: List[UploadFile] = File(...)):
            """Merge PDF files."""
            return await self._proxy_multiple_files_request(
                PDFOperationType.MERGE,
                "/process",
                files
            )
        
        @self.app.post("/rotate")
        async def rotate_pdf(
            file: UploadFile = File(...),
            rotation: int = Form(90),
            pages: str = Form(None)
        ):
            """Rotate PDF pages."""
            params = {"rotation": str(rotation)}
            if pages:
                params["pages"] = pages
            return await self._proxy_file_request(
                PDFOperationType.ROTATE, 
                "/process",
                file,
                params
            )
        
        @self.app.post("/split")
        async def split_pdf(
            file: UploadFile = File(...),
            split_type: str = Form("pages"),
            pages: str = Form(None)
        ):
            """Split PDF file."""
            params = {"split_type": split_type}
            if pages:
                params["pages"] = pages
            return await self._proxy_file_request(
                PDFOperationType.SPLIT,
                "/process",
                file,
                params
            )
        
        @self.app.post("/protect")
        async def protect_pdf(
            file: UploadFile = File(...),
            user_password: str = Form(...),
            owner_password: str = Form(None)
        ):
            """Protect PDF with password."""
            params = {"user_password": user_password}
            if owner_password:
                params["owner_password"] = owner_password
            return await self._proxy_file_request(
                PDFOperationType.PROTECT, 
                "/process",
                file,
                params
            )
        
        @self.app.post("/unlock", response_model=PDFProcessingResponse)
        async def unlock_pdf(request: UnlockRequest):
            """Unlock protected PDF."""
            return await self._proxy_request(PDFOperationType.PROTECT, "/unlock", request.dict())
        
        @self.app.post("/compress")
        async def compress_pdf(
            file: UploadFile = File(...),
            quality: str = Form("medium")
        ):
            """Compress PDF file."""
            return await self._proxy_file_request(
                PDFOperationType.COMPRESS, 
                "/process",
                file,
                {"quality": quality}
            )
        
        @self.app.post("/watermark")
        async def watermark_pdf(
            file: UploadFile = File(...),
            text: str = Form(...),
            opacity: float = Form(0.3),
            font_size: int = Form(50),
            position: str = Form("center")
        ):
            """Add watermark to PDF."""
            params = {
                "text": text,
                "opacity": str(opacity),
                "font_size": str(font_size),
                "position": position
            }
            return await self._proxy_file_request(
                PDFOperationType.WATERMARK,
                "/process",
                file,
                params
            )
        
        @self.app.post("/page-numbers", response_model=PDFProcessingResponse)
        async def add_page_numbers(request: PageNumbersRequest):
            """Add page numbers to PDF."""
            return await self._proxy_request(PDFOperationType.PAGE_NUMBERS, "/page-numbers", request.dict())
        
        @self.app.post("/crop", response_model=PDFProcessingResponse)
        async def crop_pdf(request: CropRequest):
            """Crop PDF pages."""
            return await self._proxy_request(PDFOperationType.CROP, "/crop", request.dict())
        
        @self.app.post("/ocr")
        async def ocr_pdf(
            file: UploadFile = File(...),
            language: str = Form("eng"),
            engine: str = Form("tesseract"),
            output_format: str = Form("txt")
        ):
            """Extract text from PDF using OCR."""
            params = {
                "language": language,
                "engine": engine,
                "output_format": output_format
            }
            return await self._proxy_file_request(
                PDFOperationType.OCR,
                "/process",
                file,
                params
            )
        
        @self.app.post("/pdf-to-image")
        async def pdf_to_image(
            file: UploadFile = File(...),
            format: str = Form("png"),
            dpi: int = Form(200),
            pages: str = Form("all")
        ):
            """Convert PDF to images."""
            params = {
                "format": format,
                "dpi": str(dpi),
                "pages": pages
            }
            return await self._proxy_file_request(
                PDFOperationType.PDF_TO_IMAGE,
                "/process",
                file,
                params
            )
        
        @self.app.post("/image-to-pdf")
        async def image_to_pdf(files: List[UploadFile] = File(...)):
            """Convert image(s) to PDF."""
            return await self._proxy_multiple_files_request(
                PDFOperationType.IMAGE_TO_PDF,
                "/process",
                files
            )
        
        @self.app.post("/pdf-to-word", response_model=PDFProcessingResponse)
        async def pdf_to_word(request: ConversionRequest):
            """Convert PDF to Word document."""
            return await self._proxy_request(PDFOperationType.PDF_TO_WORD, "/pdf-to-word", request.dict())
        
        @self.app.post("/word-to-pdf", response_model=PDFProcessingResponse)
        async def word_to_pdf(request: ConversionRequest):
            """Convert Word document to PDF."""
            return await self._proxy_request(PDFOperationType.WORD_TO_PDF, "/word-to-pdf", request.dict())
        
        @self.app.post("/pdf-to-excel", response_model=PDFProcessingResponse)
        async def pdf_to_excel(request: ConversionRequest):
            """Convert PDF to Excel spreadsheet."""
            return await self._proxy_request(PDFOperationType.PDF_TO_EXCEL, "/pdf-to-excel", request.dict())
        
        @self.app.post("/excel-to-pdf", response_model=PDFProcessingResponse)
        async def excel_to_pdf(request: ConversionRequest):
            """Convert Excel spreadsheet to PDF."""
            return await self._proxy_request(PDFOperationType.EXCEL_TO_PDF, "/excel-to-pdf", request.dict())
        
        @self.app.post("/pdf-to-html", response_model=PDFProcessingResponse)
        async def pdf_to_html(request: ConversionRequest):
            """Convert PDF to HTML."""
            return await self._proxy_request(PDFOperationType.PDF_TO_HTML, "/pdf-to-html", request.dict())
        
        @self.app.post("/html-to-pdf", response_model=PDFProcessingResponse)
        async def html_to_pdf(request: ConversionRequest):
            """Convert HTML to PDF."""
            return await self._proxy_request(PDFOperationType.HTML_TO_PDF, "/html-to-pdf", request.dict())
        
        @self.app.post("/pdf-to-powerpoint", response_model=PDFProcessingResponse)
        async def pdf_to_powerpoint(request: ConversionRequest):
            """Convert PDF to PowerPoint presentation."""
            return await self._proxy_request(PDFOperationType.PDF_TO_POWERPOINT, "/pdf-to-powerpoint", request.dict())
        
        @self.app.post("/powerpoint-to-pdf", response_model=PDFProcessingResponse)
        async def powerpoint_to_pdf(request: ConversionRequest):
            """Convert PowerPoint presentation to PDF."""
            return await self._proxy_request(PDFOperationType.POWERPOINT_TO_PDF, "/powerpoint-to-pdf", request.dict())
    
    async def _proxy_file_request(self, operation_type: PDFOperationType, endpoint: str, file: UploadFile, params: dict = None):
        """Proxy file upload request to appropriate microservice."""
        services = self.service_registry.get_services_by_type(operation_type)
        healthy_services = [s for s in services if s.status == ServiceStatus.HEALTHY]
        
        if not healthy_services:
            raise HTTPException(
                status_code=503, 
                detail=f"No healthy services available for operation: {operation_type.value}"
            )
        
        # Use first healthy service (could implement load balancing here)
        service = healthy_services[0]
        service_url = f"http://{service.host}:{service.port}{endpoint}"
        
        try:
            # Read file content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Prepare files for upload
            files = {"file": (file.filename, file_content, file.content_type)}
            
            # Add form data if provided
            data = params if params else {}
            
            response = await self.http_client.post(service_url, files=files, data=data, timeout=300.0)
            
            if response.status_code == 200:
                # Return the file directly
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="processed_{file.filename}"'
                    }
                )
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Service request failed: {str(e)}")
    
    async def _proxy_multiple_files_request(self, operation_type: PDFOperationType, endpoint: str, files: List[UploadFile], params: dict = None):
        """Proxy multiple file upload request to appropriate microservice."""
        services = self.service_registry.get_services_by_type(operation_type)
        healthy_services = [s for s in services if s.status == ServiceStatus.HEALTHY]
        
        if not healthy_services:
            raise HTTPException(
                status_code=503, 
                detail=f"No healthy services available for operation: {operation_type.value}"
            )
        
        # Use first healthy service
        service = healthy_services[0]
        service_url = f"http://{service.host}:{service.port}{endpoint}"
        
        try:
            # Prepare all files for upload
            files_data = []
            for file in files:
                file_content = await file.read()
                files_data.append(("files", (file.filename, file_content, file.content_type)))
                await file.seek(0)
            
            # Add form data if provided
            data = params if params else {}
            
            response = await self.http_client.post(service_url, files=files_data, data=data, timeout=300.0)
            
            if response.status_code == 200:
                # Return the file directly
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="merged.pdf"'
                    }
                )
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Service request failed: {str(e)}")
    
    async def _proxy_request(self, operation_type: PDFOperationType, endpoint: str, data: dict) -> PDFProcessingResponse:
        """Proxy request to appropriate microservice."""
        services = self.service_registry.get_services_by_type(operation_type)
        healthy_services = [s for s in services if s.status == ServiceStatus.HEALTHY]
        
        if not healthy_services:
            raise HTTPException(
                status_code=503, 
                detail=f"No healthy services available for operation: {operation_type.value}"
            )
        
        # Use first healthy service (could implement load balancing here)
        service = healthy_services[0]
        service_url = f"http://{service.host}:{service.port}{endpoint}"
        
        try:
            response = await self.http_client.post(service_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                # Modify file URLs to go through orchestrator
                if "file_url" in result and result["file_url"]:
                    original_url = result["file_url"]
                    file_name = original_url.split("/")[-1]
                    result["file_url"] = f"http://{self.config.host}:{self.config.port}/download/{service.service_id}/{file_name}"
                
                return PDFProcessingResponse(**result)
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Service request failed: {str(e)}")
    
    async def _service_discovery_loop(self):
        """Background task for service discovery."""
        while True:
            await self._discover_services()
            await asyncio.sleep(self.config.service_discovery_interval)
    
    async def _discover_services(self):
        """Discover and register available services."""
        for operation_type, service_configs in self.known_services.items():
            for config in service_configs:
                service_url = f"http://{config['host']}:{config['port']}/info"
                
                try:
                    response = await self.http_client.get(service_url)
                    if response.status_code == 200:
                        service_info = ServiceInfo(**response.json())
                        self.service_registry.register_service(service_info)
                except Exception:
                    pass  # Service not available
    
    async def _health_check_loop(self):
        """Background task for health checking registered services."""
        while True:
            await self._check_services_health()
            await asyncio.sleep(self.config.health_check_interval)
    
    async def _check_services_health(self):
        """Check health of all registered services."""
        for service_id, service in list(self.service_registry.services.items()):
            health_url = f"http://{service.host}:{service.port}/health"
            
            try:
                response = await self.http_client.get(health_url)
                if response.status_code == 200:
                    health_data = response.json()
                    service.status = ServiceStatus(health_data.get("status", "unhealthy"))
                else:
                    service.status = ServiceStatus.UNHEALTHY
            except Exception:
                service.status = ServiceStatus.UNHEALTHY
    
    def run(self, host: str = None, port: int = None):
        """Run the orchestrator."""
        host = host or self.config.host
        port = port or self.config.port
        
        print(f"Starting PDF Orchestrator on {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )


def create_orchestrator(**kwargs):
    """Factory function to create orchestrator."""
    config = OrchestratorConfig(**kwargs)
    return PDFOrchestrator(config)


if __name__ == "__main__":
    orchestrator = PDFOrchestrator()
    orchestrator.run()