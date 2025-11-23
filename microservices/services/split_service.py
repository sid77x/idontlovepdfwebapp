"""PDF Split Microservice."""
import os
import time
import zipfile
from typing import List, Optional
from pathlib import Path
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import (
    BasePDFMicroservice, PDFOperationType, SplitRequest, 
    PDFProcessingResponse, get_unique_filename, parse_page_range
)


class PDFSplitService(BasePDFMicroservice):
    """Microservice for splitting PDF files."""
    
    def __init__(self, host: str = "localhost", port: int = 8003):
        super().__init__(
            service_name="split",
            operation_type=PDFOperationType.SPLIT,
            host=host,
            port=port,
            version="1.0.0"
        )
    
    def _register_service_routes(self):
        """Register split-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            split_type: str = Form("pages"),
            pages: str = Form(None)
        ):
            """Process PDF file - split into multiple files."""
            try:
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Get PDF info
                reader = PdfReader(str(input_path))
                total_pages = len(reader.pages)
                
                # Parse split configuration
                if split_type == "each":
                    # Split each page into separate file
                    output_files = self._split_by_pages(str(input_path), total_pages)
                elif split_type == "pages" and pages:
                    # Extract specific pages
                    ranges = self._parse_split_ranges(pages, total_pages)
                    if not ranges:
                        raise HTTPException(status_code=400, detail="Invalid page specification")
                    output_files = self._split_by_ranges(str(input_path), ranges)
                elif split_type == "range" and pages:
                    # Split by page ranges
                    ranges = self._parse_split_ranges(pages, total_pages)
                    if not ranges:
                        raise HTTPException(status_code=400, detail="Invalid page ranges specified")
                    output_files = self._split_by_ranges(str(input_path), ranges)
                else:
                    raise HTTPException(status_code=400, detail="Split type must be 'each', 'pages', or 'range' with page specification")
                
                if not output_files:
                    raise HTTPException(status_code=500, detail="Failed to split PDF")
                
                # Create zip file with all outputs
                zip_filename = f"split_{Path(file.filename).stem}.zip"
                zip_path = Path(get_unique_filename(zip_filename, str(self.output_dir)))
                
                with zipfile.ZipFile(str(zip_path), 'w') as zipf:
                    for file_path in output_files:
                        zipf.write(file_path, os.path.basename(file_path))
                
                # Cleanup individual files
                self.cleanup_temp_files(*output_files)
                
                # Return the zip file
                return FileResponse(
                    path=str(zip_path),
                    media_type="application/zip",
                    filename=zip_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/split", response_model=PDFProcessingResponse)
        async def split_pdf(request: SplitRequest):
            """Split a PDF file into multiple files."""
            start_time = time.time()
            
            try:
                # Validate input file exists
                input_path = self.get_file_path(request.file_name)
                if not os.path.exists(input_path):
                    raise HTTPException(
                        status_code=404, 
                        detail=f"File not found: {request.file_name}"
                    )
                
                # Get PDF info
                reader = PdfReader(input_path)
                total_pages = len(reader.pages)
                input_size = self.get_file_size_mb(input_path)
                
                self.logger.info(f"Splitting PDF: {request.file_name} ({total_pages} pages, {input_size:.2f} MB)")
                
                # Parse split configuration
                if request.split_type == "pages":
                    # Split each page into separate file
                    output_files = self._split_by_pages(input_path, total_pages)
                elif request.split_type == "ranges":
                    # Split by page ranges
                    ranges = self._parse_split_ranges(request.split_value, total_pages)
                    if not ranges:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid page ranges specified"
                        )
                    output_files = self._split_by_ranges(input_path, ranges)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Split type must be 'pages' or 'ranges'"
                    )
                
                if not output_files:
                    return self.create_response(
                        success=False,
                        message="Failed to split PDF",
                        error_details="No output files were created"
                    )
                
                # Create zip file with all outputs
                zip_filename = f"split_{os.path.splitext(request.file_name)[0]}.zip"
                zip_path = get_unique_filename(zip_filename, self.output_dir)
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in output_files:
                        zipf.write(file_path, os.path.basename(file_path))
                
                # Calculate processing time and output info
                processing_time = (time.time() - start_time) * 1000
                output_size = self.get_file_size_mb(zip_path)
                zip_filename = os.path.basename(zip_path)
                
                # Create download URL
                file_url = f"http://{self.host}:{self.port}/download/{zip_filename}"
                
                # Cleanup individual files
                self.cleanup_temp_files(*output_files)
                
                self.logger.info(f"Split completed: {len(output_files)} files created")
                
                return self.create_response(
                    success=True,
                    message=f"Successfully split PDF into {len(output_files)} files",
                    file_url=file_url,
                    file_size_mb=output_size,
                    processing_time_ms=processing_time,
                    metadata={
                        "split_type": request.split_type,
                        "files_created": len(output_files),
                        "total_pages": total_pages,
                        "zip_filename": zip_filename
                    }
                )
                
            except Exception as e:
                self.logger.error(f"Split failed: {str(e)}")
                return self.create_response(
                    success=False,
                    message="PDF split failed",
                    error_details=str(e),
                    processing_time_ms=(time.time() - start_time) * 1000
                )
    
    def _get_service_endpoints(self) -> List[str]:
        """Get split service specific endpoints."""
        return ["/split", "/process"]
    
    def _split_by_pages(self, input_path: str, total_pages: int) -> List[str]:
        """Split PDF into individual pages."""
        try:
            reader = PdfReader(input_path)
            output_files = []
            
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                # Create output filename
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_filename = f"{base_name}_page_{page_num + 1}.pdf"
                output_path = get_unique_filename(output_filename, self.output_dir)
                
                # Write page to file
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
            
            return output_files
            
        except Exception as e:
            self.logger.error(f"Error splitting by pages: {str(e)}")
            return []
    
    def _split_by_ranges(self, input_path: str, ranges: List[tuple]) -> List[str]:
        """Split PDF by page ranges."""
        try:
            reader = PdfReader(input_path)
            output_files = []
            
            for i, (start_page, end_page) in enumerate(ranges):
                writer = PdfWriter()
                
                # Add pages in range
                for page_num in range(start_page, end_page + 1):
                    if page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
                
                # Create output filename
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_filename = f"{base_name}_part_{i + 1}_pages_{start_page + 1}-{end_page + 1}.pdf"
                output_path = get_unique_filename(output_filename, self.output_dir)
                
                # Write range to file
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
            
            return output_files
            
        except Exception as e:
            self.logger.error(f"Error splitting by ranges: {str(e)}")
            return []
    
    def _parse_split_ranges(self, ranges_str: str, total_pages: int) -> Optional[List[tuple]]:
        """Parse split ranges string into list of (start, end) tuples."""
        try:
            ranges = []
            parts = [part.strip() for part in ranges_str.split(',')]
            
            for part in parts:
                if '-' in part:
                    start, end = part.split('-', 1)
                    start_page = int(start.strip()) - 1  # Convert to 0-indexed
                    end_page = int(end.strip()) - 1      # Convert to 0-indexed
                    
                    if start_page < 0 or end_page >= total_pages or start_page > end_page:
                        return None
                    
                    ranges.append((start_page, end_page))
                else:
                    page_num = int(part.strip()) - 1  # Convert to 0-indexed
                    
                    if page_num < 0 or page_num >= total_pages:
                        return None
                    
                    ranges.append((page_num, page_num))
            
            return ranges
            
        except (ValueError, AttributeError):
            return None


def create_split_service(**kwargs):
    """Factory function to create split service."""
    return PDFSplitService(**kwargs)


if __name__ == "__main__":
    service = PDFSplitService()
    service.run()