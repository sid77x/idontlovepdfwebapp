"""
PDF Compression Microservice
Handles compressing PDF files to reduce file size.
"""
import os
import sys
import time
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, CompressRequest
)
from utils.file_ops import get_unique_filename, get_file_size_mb


class PDFCompressService(BasePDFMicroservice):
    """PDF Compression microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8005):
        super().__init__(
            service_name="pdf-compress-service",
            operation_type=PDFOperationType.COMPRESS,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            quality: str = Form("medium")
        ):
            """Process PDF file - compress it."""
            try:
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Map quality string to numeric value
                quality_map = {"low": 30, "medium": 50, "high": 70, "maximum": 90}
                quality_value = quality_map.get(quality.lower(), 50)
                
                # Generate output filename
                output_filename = f"compressed_{file.filename}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Compress PDF
                success, original_size_mb, compressed_size_mb = await self._compress_pdf_file(
                    str(input_path),
                    str(output_path),
                    quality_value
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to compress PDF")
                
                # Return the compressed file
                return FileResponse(
                    path=str(output_path),
                    media_type="application/pdf",
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/compress", response_model=PDFProcessingResponse)
        async def compress_pdf(request: CompressRequest) -> PDFProcessingResponse:
            """Compress a PDF file to reduce its size."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = self.temp_dir / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Generate output filename
                output_filename = f"compressed_{request.file_name}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Compress PDF
                success, original_size_mb, compressed_size_mb = await self._compress_pdf_file(
                    str(input_path),
                    str(output_path),
                    request.quality
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to compress PDF")
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Calculate compression ratio
                compression_ratio = ((original_size_mb - compressed_size_mb) / original_size_mb) * 100 if original_size_mb > 0 else 0
                
                return PDFProcessingResponse(
                    success=True,
                    message=f"PDF compressed successfully. Size reduced by {compression_ratio:.1f}%",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=compressed_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "compress",
                        "input_file": request.file_name,
                        "output_file": output_path.name,
                        "original_size_mb": original_size_mb,
                        "compressed_size_mb": compressed_size_mb,
                        "compression_ratio_percent": round(compression_ratio, 1),
                        "quality": request.quality
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Compression error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to compress PDF",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/compress", "/process"]
    
    async def _compress_pdf_file(self, input_path: str, output_path: str, quality: int) -> tuple:
        """
        Compress a PDF file using PyPDF2 optimization.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save compressed PDF
            quality: Compression quality (10-95)
        
        Returns:
            tuple: (success: bool, original_size_mb: float, compressed_size_mb: float)
        """
        try:
            original_size = get_file_size_mb(input_path)
            
            # Open PDF - handle encrypted PDFs
            try:
                reader = PdfReader(input_path)
                # Try to decrypt if encrypted
                if reader.is_encrypted:
                    try:
                        reader.decrypt("")  # Try empty password
                    except:
                        self.logger.error("PDF is password-protected")
                        return False, 0, 0
            except Exception as e:
                self.logger.error(f"Cannot read PDF: {str(e)}")
                return False, 0, 0
            
            writer = PdfWriter()
            
            # Add all pages with optimization
            for page in reader.pages:
                writer.add_page(page)
            
            # Apply compression to content streams
            try:
                for page in writer.pages:
                    if hasattr(page, 'compress_content_streams'):
                        page.compress_content_streams()
            except:
                pass  # Skip if compression not available
            
            # Remove metadata to reduce size (if quality is high compression)
            if quality <= 50:  # High compression
                writer.add_metadata({})
            
            # Save with compression
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            compressed_size = get_file_size_mb(output_path)
            
            return True, original_size, compressed_size
            
        except Exception as e:
            self.logger.error(f"Error compressing PDF: {str(e)}")
            return False, 0, 0


def main():
    """Run the PDF Compression service."""
    service = PDFCompressService()
    service.run()


if __name__ == "__main__":
    main()