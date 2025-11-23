"""PDF Merge Microservice."""
import os
import time
from typing import List
from pathlib import Path
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import (
    BasePDFMicroservice, PDFOperationType, MergeRequest, 
    PDFProcessingResponse, get_unique_filename
)


class PDFMergeService(BasePDFMicroservice):
    """Microservice for merging PDF files."""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        super().__init__(
            service_name="merge",
            operation_type=PDFOperationType.MERGE,
            host=host,
            port=port,
            version="1.0.0"
        )
    
    def _register_service_routes(self):
        """Register merge-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            files: List[UploadFile] = File(...)
        ):
            """Process PDF files - merge multiple PDFs into one."""
            try:
                if len(files) < 2:
                    raise HTTPException(status_code=400, detail="At least 2 files required for merging")
                
                # Save all uploaded files
                input_paths = []
                for file in files:
                    input_path = Path(self.upload_dir) / file.filename
                    with open(input_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    input_paths.append(str(input_path))
                
                # Generate output filename
                output_filename = "merged.pdf"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Merge PDFs
                success = self._merge_pdf_files(input_paths, str(output_path))
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to merge PDFs")
                
                # Return the merged file
                return FileResponse(
                    path=str(output_path),
                    media_type="application/pdf",
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/merge", response_model=PDFProcessingResponse)
        async def merge_pdfs(request: MergeRequest):
            """Merge multiple PDF files."""
            start_time = time.time()
            
            try:
                # Validate input files exist
                input_files = []
                total_size = 0
                
                for file_name in request.file_names:
                    file_path = self.get_file_path(file_name)
                    if not os.path.exists(file_path):
                        raise HTTPException(
                            status_code=404, 
                            detail=f"File not found: {file_name}"
                        )
                    input_files.append(file_path)
                    total_size += self.get_file_size_mb(file_path)
                
                self.logger.info(f"Merging {len(input_files)} files, total size: {total_size:.2f} MB")
                
                # Create output file path
                output_filename = request.output_filename or "merged.pdf"
                output_path = get_unique_filename(output_filename, self.output_dir)
                
                # Merge PDFs
                success = self._merge_pdf_files(input_files, output_path)
                
                if not success:
                    return self.create_response(
                        success=False,
                        message="Failed to merge PDF files",
                        error_details="PDF merging operation failed"
                    )
                
                # Calculate processing time and output info
                processing_time = (time.time() - start_time) * 1000
                output_size = self.get_file_size_mb(output_path)
                output_filename = os.path.basename(output_path)
                
                # Create download URL
                file_url = f"http://{self.host}:{self.port}/download/{output_filename}"
                
                self.logger.info(f"Merge completed: {output_filename} ({output_size:.2f} MB)")
                
                return self.create_response(
                    success=True,
                    message=f"Successfully merged {len(input_files)} PDF files",
                    file_url=file_url,
                    file_size_mb=output_size,
                    processing_time_ms=processing_time,
                    metadata={
                        "input_files_count": len(input_files),
                        "output_filename": output_filename,
                        "total_input_size_mb": total_size
                    }
                )
                
            except Exception as e:
                self.logger.error(f"Merge failed: {str(e)}")
                return self.create_response(
                    success=False,
                    message="PDF merge failed",
                    error_details=str(e),
                    processing_time_ms=(time.time() - start_time) * 1000
                )
    
    def _get_service_endpoints(self) -> List[str]:
        """Get merge service specific endpoints."""
        return ["/merge", "/process"]
    
    def _merge_pdf_files(self, input_files: List[str], output_path: str) -> bool:
        """
        Merge multiple PDF files into a single PDF.
        
        Args:
            input_files: List of input PDF file paths
            output_path: Output PDF file path
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            writer = PdfWriter()
            
            for file_path in input_files:
                self.logger.info(f"Processing: {os.path.basename(file_path)}")
                
                reader = PdfReader(file_path)
                
                # Add all pages from this PDF
                for page_num in range(len(reader.pages)):
                    writer.add_page(reader.pages[page_num])
            
            # Write merged PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            self.logger.info(f"Merge successful: {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error merging PDFs: {str(e)}")
            return False


def create_merge_service(**kwargs):
    """Factory function to create merge service."""
    return PDFMergeService(**kwargs)


if __name__ == "__main__":
    service = PDFMergeService()
    service.run()