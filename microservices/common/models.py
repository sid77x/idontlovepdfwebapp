"""Common models and schemas for PDF microservices."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ServiceStatus(str, Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"


class PDFOperationType(str, Enum):
    """PDF operation types."""
    MERGE = "merge"
    SPLIT = "split"
    ROTATE = "rotate"
    PROTECT = "protect"
    UNLOCK = "unlock"
    COMPRESS = "compress"
    WATERMARK = "watermark"
    PAGE_NUMBERS = "page_numbers"
    CROP = "crop"
    REPAIR = "repair"
    PDF_TO_IMAGE = "pdf_to_image"
    IMAGE_TO_PDF = "image_to_pdf"
    PDF_TO_WORD = "pdf_to_word"
    WORD_TO_PDF = "word_to_pdf"
    PDF_TO_EXCEL = "pdf_to_excel"
    EXCEL_TO_PDF = "excel_to_pdf"
    PDF_TO_HTML = "pdf_to_html"
    HTML_TO_PDF = "html_to_pdf"
    PDF_TO_POWERPOINT = "pdf_to_powerpoint"
    POWERPOINT_TO_PDF = "powerpoint_to_pdf"
    OCR = "ocr"


class ServiceInfo(BaseModel):
    """Service information model."""
    service_id: str
    name: str
    version: str
    description: str
    operation_type: PDFOperationType
    host: str
    port: int
    status: ServiceStatus
    endpoints: List[str]


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    service_id: str
    status: ServiceStatus
    timestamp: str
    uptime_seconds: float
    version: str
    details: Optional[Dict[str, Any]] = None


class PDFProcessingRequest(BaseModel):
    """Base PDF processing request model."""
    operation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PDFProcessingResponse(BaseModel):
    """Base PDF processing response model."""
    success: bool
    operation_id: Optional[str] = None
    message: str
    file_url: Optional[str] = None
    file_size_mb: Optional[float] = None
    processing_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None


class MergeRequest(PDFProcessingRequest):
    """Merge PDF files request."""
    file_names: List[str] = Field(..., description="List of uploaded file names to merge")
    output_filename: Optional[str] = Field(default="merged.pdf", description="Output filename")


class SplitRequest(PDFProcessingRequest):
    """Split PDF file request."""
    file_name: str = Field(..., description="Name of uploaded PDF file to split")
    split_type: str = Field(..., description="Split type: 'pages' or 'ranges'")
    split_value: str = Field(..., description="Pages or ranges to split (e.g., '1-3,5,7-9')")


class RotateRequest(PDFProcessingRequest):
    """Rotate PDF pages request."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    rotation_angle: int = Field(..., description="Rotation angle: 90, 180, or 270")
    pages: Optional[str] = Field(default=None, description="Pages to rotate (e.g., '1-3,5'), None for all")


class ProtectRequest(PDFProcessingRequest):
    """Protect PDF with password request."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    user_password: str = Field(..., description="User password for opening the PDF")
    owner_password: Optional[str] = Field(default=None, description="Owner password for permissions")
    allow_printing: bool = Field(default=True, description="Allow printing")
    allow_modification: bool = Field(default=False, description="Allow modification")


class UnlockRequest(PDFProcessingRequest):
    """Unlock protected PDF request."""
    file_name: str = Field(..., description="Name of uploaded protected PDF file")
    password: str = Field(..., description="Password to unlock the PDF")


class CompressRequest(PDFProcessingRequest):
    """Compress PDF file request."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    quality: int = Field(default=50, ge=10, le=95, description="Compression quality (10-95)")


class WatermarkRequest(PDFProcessingRequest):
    """Add watermark to PDF request."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    watermark_text: str = Field(..., description="Watermark text")
    opacity: float = Field(default=0.3, ge=0.1, le=1.0, description="Watermark opacity (0.1-1.0)")
    font_size: int = Field(default=50, ge=10, le=200, description="Font size (10-200)")
    position: str = Field(default="center", description="Position: center, top-left, top-right, bottom-left, bottom-right")


class PageNumbersRequest(PDFProcessingRequest):
    """Add page numbers to PDF request."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    position: str = Field(default="bottom-right", description="Position: top-left, top-right, bottom-left, bottom-right, bottom-center")
    font_size: int = Field(default=12, ge=8, le=24, description="Font size (8-24)")
    start_page: int = Field(default=1, ge=1, description="Starting page number")


class CropRequest(PDFProcessingRequest):
    """Crop PDF pages request."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    crop_box: List[float] = Field(..., description="Crop box [left, bottom, right, top] in points")
    pages: Optional[str] = Field(default=None, description="Pages to crop (e.g., '1-3,5'), None for all")


class ConversionRequest(PDFProcessingRequest):
    """Base conversion request."""
    file_name: str = Field(..., description="Name of uploaded file")
    output_format: Optional[str] = Field(default=None, description="Output format")
    
    
class OCRRequest(PDFProcessingRequest):
    """OCR request for PDF text extraction."""
    file_name: str = Field(..., description="Name of uploaded PDF file")
    language: str = Field(default="eng", description="OCR language (e.g., 'eng', 'spa')")
    engine: str = Field(default="tesseract", description="OCR engine: 'tesseract' or 'easyocr'")
    output_format: str = Field(default="txt", description="Output format: 'txt' or 'json'")


class ServiceRegistry(BaseModel):
    """Service registry model."""
    services: Dict[str, ServiceInfo] = Field(default_factory=dict)
    
    def register_service(self, service: ServiceInfo):
        """Register a service."""
        self.services[service.service_id] = service
    
    def unregister_service(self, service_id: str):
        """Unregister a service."""
        if service_id in self.services:
            del self.services[service_id]
    
    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service by ID."""
        return self.services.get(service_id)
    
    def get_services_by_type(self, operation_type: PDFOperationType) -> List[ServiceInfo]:
        """Get all services for a specific operation type."""
        return [service for service in self.services.values() if service.operation_type == operation_type]
    
    def get_healthy_services(self) -> List[ServiceInfo]:
        """Get all healthy services."""
        return [service for service in self.services.values() if service.status == ServiceStatus.HEALTHY]