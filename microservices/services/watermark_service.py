"""
PDF Watermark Microservice
Handles adding watermarks to PDF files.
"""
import os
import sys
import time
from pathlib import Path
from io import BytesIO

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, WatermarkRequest
)
from utils.file_ops import get_unique_filename, get_file_size_mb


class PDFWatermarkService(BasePDFMicroservice):
    """PDF Watermark microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8006):
        super().__init__(
            service_name="pdf-watermark-service",
            operation_type=PDFOperationType.WATERMARK,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            text: str = Form(...),
            opacity: float = Form(0.5),
            font_size: int = Form(60),
            position: str = Form("center"),
            rotation: int = Form(45)
        ):
            """Process PDF file - add watermark."""
            try:
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Generate output filename
                output_filename = f"watermarked_{file.filename}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Add watermark to PDF
                success = await self._add_watermark_to_pdf(
                    str(input_path),
                    str(output_path),
                    text,
                    opacity,
                    font_size,
                    position,
                    rotation
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to add watermark to PDF")
                
                # Return the watermarked file
                return FileResponse(
                    path=str(output_path),
                    media_type="application/pdf",
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/watermark", response_model=PDFProcessingResponse)
        async def add_watermark(request: WatermarkRequest) -> PDFProcessingResponse:
            """Add a text watermark to a PDF file."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = Path(self.upload_dir) / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Generate output filename
                output_filename = f"watermarked_{request.file_name}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Add watermark to PDF
                success = await self._add_watermark_to_pdf(
                    str(input_path),
                    str(output_path),
                    request.watermark_text,
                    request.opacity,
                    request.font_size,
                    request.position
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to add watermark to PDF")
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get file size
                file_size_mb = get_file_size_mb(str(output_path))
                
                return PDFProcessingResponse(
                    success=True,
                    message="Watermark added successfully",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "watermark",
                        "input_file": request.file_name,
                        "output_file": output_path.name,
                        "watermark_text": request.watermark_text,
                        "opacity": request.opacity,
                        "font_size": request.font_size,
                        "position": request.position
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Watermark error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to add watermark",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/watermark", "/process"]
    
    def _create_text_watermark(self, text: str, opacity: float = 0.3, rotation: int = 45, 
                              font_size: int = 50, color: tuple = (0.5, 0.5, 0.5),
                              position: str = "center", page_width: float = None, 
                              page_height: float = None) -> BytesIO:
        """
        Create a watermark PDF with text that adapts to page dimensions.
        
        Args:
            text: Watermark text
            opacity: Transparency (0-1)
            rotation: Rotation angle in degrees
            font_size: Font size
            color: RGB color tuple (0-1 range)
            position: Position of watermark
            page_width: Width of the page
            page_height: Height of the page
        
        Returns:
            BytesIO: PDF bytes with watermark
        """
        packet = BytesIO()
        
        # Use provided dimensions or default to letter size
        if page_width and page_height:
            pagesize = (page_width, page_height)
        else:
            pagesize = letter
        
        can = canvas.Canvas(packet, pagesize=pagesize)
        width, height = pagesize
        
        # Set transparency and color
        can.setFillColor(Color(color[0], color[1], color[2], alpha=opacity))
        
        # Set font
        can.setFont("Helvetica-Bold", font_size)
        
        # Calculate position
        text_width = can.stringWidth(text, "Helvetica-Bold", font_size)
        
        if position == "center":
            x = (width - text_width) / 2
            y = height / 2
        elif position == "top-left":
            x = 50
            y = height - 50
        elif position == "top-right":
            x = width - text_width - 50
            y = height - 50
        elif position == "bottom-left":
            x = 50
            y = 50
        elif position == "bottom-right":
            x = width - text_width - 50
            y = 50
        else:  # default to center
            x = (width - text_width) / 2
            y = height / 2
        
        # Save current state
        can.saveState()
        
        # Move to position and rotate
        can.translate(x, y)
        can.rotate(rotation)
        
        # Draw text
        can.drawString(0, 0, text)
        
        # Restore state
        can.restoreState()
        can.save()
        
        packet.seek(0)
        return packet
    
    async def _add_watermark_to_pdf(self, input_path: str, output_path: str, 
                                   watermark_text: str, opacity: float,
                                   font_size: int, position: str, rotation: int = 0) -> bool:
        """
        Add watermark to all pages of a PDF file.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save watermarked PDF
            watermark_text: Text to use as watermark
            opacity: Watermark opacity (0-1)
            font_size: Font size for watermark
            position: Position of watermark
            rotation: Rotation angle in degrees (default 0 = horizontal)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open the PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                try:
                    # Get page dimensions
                    page_box = page.mediabox
                    page_width = float(page_box.width)
                    page_height = float(page_box.height)
                    
                    # Create watermark for this page size
                    watermark_pdf = self._create_text_watermark(
                        text=watermark_text,
                        opacity=opacity,
                        rotation=rotation,
                        font_size=font_size,
                        position=position,
                        page_width=page_width,
                        page_height=page_height
                    )
                    
                    # Read watermark PDF
                    watermark_reader = PdfReader(watermark_pdf)
                    watermark_page = watermark_reader.pages[0]
                    
                    # Merge watermark with page
                    page.merge_page(watermark_page)
                    writer.add_page(page)
                    
                except Exception as e:
                    self.logger.warning(f"Error adding watermark to page {page_num + 1}: {str(e)}")
                    # Add page without watermark if there's an error
                    writer.add_page(page)
            
            # Save the watermarked PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding watermark to PDF: {str(e)}")
            return False


def main():
    """Run the PDF Watermark service."""
    service = PDFWatermarkService()
    service.run()


if __name__ == "__main__":
    main()