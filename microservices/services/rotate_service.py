"""PDF Rotate Microservice."""
import os
import time
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import (
    BasePDFMicroservice, PDFOperationType, RotateRequest, 
    PDFProcessingResponse, get_unique_filename, parse_page_range
)


class PDFRotateService(BasePDFMicroservice):
    """Microservice for rotating PDF pages."""
    
    def __init__(self, host: str = "localhost", port: int = 8002):
        super().__init__(
            service_name="rotate",
            operation_type=PDFOperationType.ROTATE,
            host=host,
            port=port,
            version="1.0.0"
        )
    
    def _register_service_routes(self):
        """Register rotate-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            rotation: int = Form(90),
            pages: str = Form(None)
        ):
            """Process PDF file - rotate pages."""
            try:
                # Validate rotation angle
                if rotation not in [90, 180, 270]:
                    raise HTTPException(
                        status_code=400,
                        detail="Rotation angle must be 90, 180, or 270 degrees"
                    )
                
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Get PDF info
                reader = PdfReader(str(input_path))
                total_pages = len(reader.pages)
                
                # Parse page selection
                pages_to_rotate = None
                if pages:
                    pages_to_rotate = parse_page_range(pages, total_pages)
                    if pages_to_rotate is None:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid page range specified"
                        )
                
                # Create output file path
                output_filename = f"rotated_{file.filename}"
                output_path = Path(get_unique_filename(output_filename, self.output_dir))
                
                # Rotate PDF
                success = self._rotate_pdf(
                    str(input_path), 
                    str(output_path), 
                    rotation, 
                    pages_to_rotate
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to rotate PDF")
                
                # Return the rotated file
                return FileResponse(
                    path=str(output_path),
                    media_type="application/pdf",
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/rotate", response_model=PDFProcessingResponse)
        async def rotate_pdf(request: RotateRequest):
            """Rotate pages in a PDF file."""
            start_time = time.time()
            
            try:
                # Validate input file exists
                input_path = self.get_file_path(request.file_name)
                if not os.path.exists(input_path):
                    raise HTTPException(
                        status_code=404, 
                        detail=f"File not found: {request.file_name}"
                    )
                
                # Validate rotation angle
                if request.rotation_angle not in [90, 180, 270]:
                    raise HTTPException(
                        status_code=400,
                        detail="Rotation angle must be 90, 180, or 270 degrees"
                    )
                
                # Get PDF info
                reader = PdfReader(input_path)
                total_pages = len(reader.pages)
                input_size = self.get_file_size_mb(input_path)
                
                # Parse page selection
                pages_to_rotate = None
                if request.pages:
                    pages_to_rotate = parse_page_range(request.pages, total_pages)
                    if pages_to_rotate is None:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid page range specified"
                        )
                
                self.logger.info(f"Rotating PDF: {request.file_name} ({total_pages} pages, {input_size:.2f} MB)")
                
                # Create output file path
                output_filename = f"rotated_{request.file_name}"
                output_path = get_unique_filename(output_filename, self.output_dir)
                
                # Rotate PDF
                success = self._rotate_pdf(
                    input_path, 
                    output_path, 
                    request.rotation_angle, 
                    pages_to_rotate
                )
                
                if not success:
                    return self.create_response(
                        success=False,
                        message="Failed to rotate PDF",
                        error_details="PDF rotation operation failed"
                    )
                
                # Calculate processing time and output info
                processing_time = (time.time() - start_time) * 1000
                output_size = self.get_file_size_mb(output_path)
                output_filename = os.path.basename(output_path)
                
                # Create download URL
                file_url = f"http://{self.host}:{self.port}/download/{output_filename}"
                
                pages_rotated = len(pages_to_rotate) if pages_to_rotate else total_pages
                self.logger.info(f"Rotation completed: {pages_rotated} pages rotated {request.rotation_angle}°")
                
                return self.create_response(
                    success=True,
                    message=f"Successfully rotated {pages_rotated} pages by {request.rotation_angle}°",
                    file_url=file_url,
                    file_size_mb=output_size,
                    processing_time_ms=processing_time,
                    metadata={
                        "rotation_angle": request.rotation_angle,
                        "pages_rotated": pages_rotated,
                        "total_pages": total_pages,
                        "output_filename": output_filename
                    }
                )
                
            except Exception as e:
                self.logger.error(f"Rotation failed: {str(e)}")
                return self.create_response(
                    success=False,
                    message="PDF rotation failed",
                    error_details=str(e),
                    processing_time_ms=(time.time() - start_time) * 1000
                )
    
    def _get_service_endpoints(self) -> List[str]:
        """Get rotate service specific endpoints."""
        return ["/rotate", "/process"]
    
    def _rotate_pdf(
        self, 
        input_path: str, 
        output_path: str, 
        rotation: int, 
        pages: Optional[List[int]] = None
    ) -> bool:
        """
        Rotate pages in a PDF file.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save rotated PDF
            rotation: Rotation angle (90, 180, 270)
            pages: List of page indices to rotate (0-indexed), None for all pages
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            total_pages = len(reader.pages)
            
            for page_num in range(total_pages):
                page = reader.pages[page_num]
                
                # Rotate page if it's in the selection (or all pages if pages is None)
                if pages is None or page_num in pages:
                    page.rotate(rotation)
                
                writer.add_page(page)
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rotating PDF: {str(e)}")
            return False


def create_rotate_service(**kwargs):
    """Factory function to create rotate service."""
    return PDFRotateService(**kwargs)


if __name__ == "__main__":
    service = PDFRotateService()
    service.run()