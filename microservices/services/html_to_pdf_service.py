"""
HTML to PDF Conversion Microservice
Handles converting HTML content or files to PDF.
"""
import os
import sys
import time
from pathlib import Path

import weasyprint
from fastapi import HTTPException

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, ConversionRequest
)
from utils.file_ops import get_unique_filename


class HTMLToPDFService(BasePDFMicroservice):
    """HTML to PDF conversion microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8018):
        super().__init__(
            service_name="html-to-pdf-service",
            operation_type=PDFOperationType.HTML_TO_PDF,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/html-to-pdf", response_model=PDFProcessingResponse)
        async def convert_html_to_pdf(request: ConversionRequest) -> PDFProcessingResponse:
            """Convert HTML file to PDF."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = self.temp_dir / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Check if file is HTML
                if not input_path.suffix.lower() in ['.html', '.htm']:
                    raise HTTPException(status_code=400, detail="File must be an HTML file")
                
                # Generate output filename
                output_filename = f"{Path(request.file_name).stem}.pdf"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Convert HTML to PDF
                success = await self._convert_html_to_pdf(
                    str(input_path),
                    str(output_path)
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get file size
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                return PDFProcessingResponse(
                    success=True,
                    message="Successfully converted HTML to PDF",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "html_to_pdf",
                        "input_file": request.file_name,
                        "output_file": output_path.name
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"HTML to PDF conversion error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to convert HTML to PDF",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/html-to-pdf"]
    
    async def _convert_html_to_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Convert HTML file to PDF using WeasyPrint.
        
        Args:
            input_path: Path to input HTML file
            output_path: Path to save PDF
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read HTML content
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Convert HTML to PDF using WeasyPrint
            html_doc = weasyprint.HTML(string=html_content, base_url=str(Path(input_path).parent))
            pdf_bytes = html_doc.write_pdf()
            
            # Write PDF to output file
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting HTML to PDF: {str(e)}")
            return False


def main():
    """Run the HTML to PDF service."""
    service = HTMLToPDFService()
    service.run()


if __name__ == "__main__":
    main()