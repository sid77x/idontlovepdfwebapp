"""
Image to PDF Conversion Microservice
Handles converting image files to PDF.
"""
import os
import sys
import time
from pathlib import Path
from typing import List

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, ConversionRequest
)
from utils.file_ops import get_unique_filename


class ImageToPDFService(BasePDFMicroservice):
    """Image to PDF conversion microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8012):
        super().__init__(
            service_name="image-to-pdf-service",
            operation_type=PDFOperationType.IMAGE_TO_PDF,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/process")
        async def process_images(
            files: List[UploadFile] = File(...)
        ):
            """Process image files - convert to PDF."""
            try:
                if not files:
                    raise HTTPException(status_code=400, detail="At least one image file required")
                
                # Save all uploaded files
                input_paths = []
                for file in files:
                    # Check if file is an image
                    if not any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']):
                        raise HTTPException(status_code=400, detail=f"{file.filename} is not a valid image format")
                    
                    input_path = Path(self.upload_dir) / file.filename
                    with open(input_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    input_paths.append(str(input_path))
                
                # Generate output filename
                if len(input_paths) == 1:
                    output_filename = f"{Path(files[0].filename).stem}.pdf"
                else:
                    output_filename = "converted_images.pdf"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Convert single image or merge multiple images into PDF
                if len(input_paths) == 1:
                    success = await self._convert_image_to_pdf(input_paths[0], str(output_path))
                else:
                    success = await self._convert_multiple_images_to_pdf(input_paths, str(output_path))
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to convert images to PDF")
                
                # Return the PDF file
                return FileResponse(
                    path=str(output_path),
                    media_type="application/pdf",
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/image-to-pdf", response_model=PDFProcessingResponse)
        async def convert_image_to_pdf(request: ConversionRequest) -> PDFProcessingResponse:
            """Convert image file to PDF."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = Path(self.upload_dir) / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Check if file is an image
                if not self._is_image_file(str(input_path)):
                    raise HTTPException(status_code=400, detail="File is not a valid image format")
                
                # Generate output filename
                output_filename = f"{Path(request.file_name).stem}.pdf"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Convert image to PDF
                success = await self._convert_image_to_pdf(
                    str(input_path),
                    str(output_path)
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to convert image to PDF")
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get file size
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                return PDFProcessingResponse(
                    success=True,
                    message="Successfully converted image to PDF",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "image_to_pdf",
                        "input_file": request.file_name,
                        "output_file": output_path.name
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Image to PDF conversion error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to convert image to PDF",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/image-to-pdf", "/process"]
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is a valid image format."""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    async def _convert_multiple_images_to_pdf(self, input_paths: List[str], output_path: str) -> bool:
        """Convert multiple images into a single PDF."""
        try:
            from PyPDF2 import PdfWriter, PdfReader
            import io
            
            writer = PdfWriter()
            
            for img_path in input_paths:
                # Convert each image to a single-page PDF
                temp_pdf = io.BytesIO()
                
                with Image.open(img_path) as image:
                    # Convert to RGB if necessary
                    if image.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Get image dimensions and create PDF page
                    img_width, img_height = image.size
                    a4_width, a4_height = A4
                    
                    scale_w = a4_width / img_width
                    scale_h = a4_height / img_height
                    scale = min(scale_w, scale_h, 1.0)
                    
                    final_width = img_width * scale
                    final_height = img_height * scale
                    
                    # Create PDF page with this image
                    c = canvas.Canvas(temp_pdf, pagesize=(final_width, final_height))
                    temp_img = io.BytesIO()
                    image.save(temp_img, "JPEG", quality=85)
                    temp_img.seek(0)
                    
                    from reportlab.lib.utils import ImageReader
                    img_reader = ImageReader(temp_img)
                    c.drawImage(img_reader, 0, 0, width=final_width, height=final_height)
                    c.save()
                    
                    # Add page to writer
                    temp_pdf.seek(0)
                    page_reader = PdfReader(temp_pdf)
                    for page in page_reader.pages:
                        writer.add_page(page)
            
            # Write final PDF
            with open(output_path, "wb") as f:
                writer.write(f)
            
            return True
        except Exception as e:
            self.logger.error(f"Error converting multiple images to PDF: {str(e)}")
            return False
    
    async def _convert_image_to_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Convert an image file to PDF.
        
        Args:
            input_path: Path to input image
            output_path: Path to save PDF
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open and process image
            with Image.open(input_path) as image:
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Get image dimensions
                img_width, img_height = image.size
                
                # Calculate PDF page size to fit image
                # Use A4 as maximum size and scale down if necessary
                a4_width, a4_height = A4
                
                # Calculate scaling factor to fit image in A4
                scale_w = a4_width / img_width
                scale_h = a4_height / img_height
                scale = min(scale_w, scale_h, 1.0)  # Don't scale up
                
                # Calculate final dimensions
                final_width = img_width * scale
                final_height = img_height * scale
                
                # Create PDF
                c = canvas.Canvas(output_path, pagesize=(final_width, final_height))
                
                # Save image to temporary file for reportlab
                temp_img_path = str(Path(output_path).parent / "temp_image.jpg")
                image.save(temp_img_path, "JPEG", quality=85)
                
                # Draw image on PDF
                c.drawImage(temp_img_path, 0, 0, width=final_width, height=final_height)
                c.save()
                
                # Clean up temporary image
                try:
                    os.remove(temp_img_path)
                except:
                    pass
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error converting image to PDF: {str(e)}")
            return False


def main():
    """Run the Image to PDF service."""
    service = ImageToPDFService()
    service.run()


if __name__ == "__main__":
    main()