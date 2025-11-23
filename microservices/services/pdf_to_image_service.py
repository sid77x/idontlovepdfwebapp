"""
PDF to Image Conversion Microservice
Handles converting PDF pages to image files.
"""
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, ConversionRequest
)
from utils.file_ops import get_unique_filename


class PDFToImageService(BasePDFMicroservice):
    """PDF to Image conversion microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8011):
        super().__init__(
            service_name="pdf-to-image-service",
            operation_type=PDFOperationType.PDF_TO_IMAGE,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            format: str = Form("png"),
            dpi: int = Form(200),
            pages: str = Form("all")
        ):
            """Process PDF file - convert to images."""
            try:
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Convert PDF to images
                image_paths = await self._convert_pdf_to_images(
                    str(input_path),
                    str(self.output_dir),
                    dpi=dpi,
                    image_format=format.upper(),
                    pages=pages
                )
                
                if not image_paths:
                    raise HTTPException(status_code=500, detail="Failed to convert PDF to images")
                
                # Create ZIP file if multiple images, otherwise return single image
                if len(image_paths) > 1:
                    zip_filename = f"{Path(file.filename).stem}_images.zip"
                    zip_path = Path(get_unique_filename(zip_filename, str(self.output_dir)))
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for img_path in image_paths:
                            zipf.write(img_path, Path(img_path).name)
                    
                    # Clean up individual image files
                    for img_path in image_paths:
                        try:
                            os.remove(img_path)
                        except:
                            pass
                    
                    # Return the zip file
                    return FileResponse(
                        path=str(zip_path),
                        media_type="application/zip",
                        filename=zip_path.name
                    )
                else:
                    # Return single image
                    media_type = "image/jpeg" if format.lower() in ["jpg", "jpeg"] else "image/png"
                    return FileResponse(
                        path=image_paths[0],
                        media_type=media_type,
                        filename=Path(image_paths[0]).name
                    )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/pdf-to-image", response_model=PDFProcessingResponse)
        async def convert_pdf_to_image(request: ConversionRequest) -> PDFProcessingResponse:
            """Convert PDF pages to images."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = Path(self.upload_dir) / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Set default output format if not specified
                output_format = request.output_format or "PNG"
                
                # Convert PDF to images
                image_paths = await self._convert_pdf_to_images(
                    str(input_path),
                    str(self.output_dir),
                    dpi=200,
                    image_format=output_format.upper(),
                    pages="all"
                )
                
                if not image_paths:
                    raise HTTPException(status_code=500, detail="Failed to convert PDF to images")
                
                # Create ZIP file if multiple images
                if len(image_paths) > 1:
                    zip_filename = f"{Path(request.file_name).stem}_images.zip"
                    zip_path = Path(get_unique_filename(zip_filename, str(self.output_dir)))
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for img_path in image_paths:
                            zipf.write(img_path, Path(img_path).name)
                    
                    # Clean up individual image files
                    for img_path in image_paths:
                        try:
                            os.remove(img_path)
                        except:
                            pass
                    
                    output_file = zip_path.name
                    file_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                else:
                    output_file = Path(image_paths[0]).name
                    file_size_mb = os.path.getsize(image_paths[0]) / (1024 * 1024)
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=True,
                    message=f"Successfully converted PDF to {len(image_paths)} image(s)",
                    file_url=f"/download/{output_file}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "pdf_to_image",
                        "input_file": request.file_name,
                        "output_file": output_file,
                        "images_created": len(image_paths),
                        "format": output_format,
                        "dpi": 200
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"PDF to image conversion error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to convert PDF to images",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/pdf-to-image", "/process"]
    
    async def _convert_pdf_to_images(self, input_path: str, output_dir: str, 
                                    dpi: int = 200, image_format: str = "PNG", 
                                    pages: str = "all") -> List[str]:
        """
        Convert PDF pages to images.
        
        Args:
            input_path: Input PDF path
            output_dir: Output directory for images
            dpi: Resolution (dots per inch)
            image_format: Output format (PNG, JPG, JPEG)
            pages: "all" or comma-separated page numbers
        
        Returns:
            List of paths to created image files
        """
        try:
            # Open PDF with PyMuPDF (fitz)
            pdf_document = fitz.open(input_path)
            total_pages = len(pdf_document)
            
            # Parse page selection
            if pages == "all":
                page_list = list(range(total_pages))
            else:
                page_list = []
                for part in pages.split(','):
                    part = part.strip()
                    if '-' in part:
                        try:
                            start, end = map(int, part.split('-'))
                            page_list.extend(range(start - 1, min(end, total_pages)))
                        except ValueError:
                            continue
                    else:
                        try:
                            page_num = int(part) - 1
                            if 0 <= page_num < total_pages:
                                page_list.append(page_num)
                        except ValueError:
                            continue
            
            # Remove duplicates and sort
            page_list = sorted(list(set(page_list)))
            
            if not page_list:
                raise Exception("No valid pages specified")
            
            # Convert pages to images
            image_paths = []
            base_name = Path(input_path).stem
            
            for i, page_num in enumerate(page_list):
                page = pdf_document[page_num]
                
                # Calculate matrix for DPI scaling
                zoom = dpi / 72  # 72 is default DPI
                mat = fitz.Matrix(zoom, zoom)
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat)
                
                # Generate output filename
                if len(page_list) == 1:
                    output_filename = f"{base_name}.{image_format.lower()}"
                else:
                    output_filename = f"{base_name}_page_{page_num + 1}.{image_format.lower()}"
                
                output_path = os.path.join(output_dir, output_filename)
                
                # Save image
                if image_format.upper() in ["JPG", "JPEG"]:
                    pix.save(output_path, output="jpeg")
                else:
                    pix.save(output_path, output="png")
                
                image_paths.append(output_path)
                
                # Release pixmap memory
                pix = None
            
            pdf_document.close()
            return image_paths
            
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {str(e)}")
            return []


def main():
    """Run the PDF to Image service."""
    service = PDFToImageService()
    service.run()


if __name__ == "__main__":
    main()