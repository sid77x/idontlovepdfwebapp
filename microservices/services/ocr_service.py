"""
PDF OCR Microservice
Handles optical character recognition (text extraction) from PDF files.
"""
import os
import sys
import time
import json
from pathlib import Path
from typing import Optional, List

import fitz  # PyMuPDF
from PIL import Image
import io
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, OCRRequest
)
from utils.file_ops import get_unique_filename


class PDFOCRService(BasePDFMicroservice):
    """PDF OCR microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8010):
        super().__init__(
            service_name="pdf-ocr-service",
            operation_type=PDFOperationType.OCR,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            language: str = Form("eng"),
            engine: str = Form("tesseract"),
            output_format: str = Form("txt")
        ):
            """Process PDF file - perform OCR."""
            try:
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Perform OCR
                ocr_result = await self._perform_ocr_on_pdf(
                    str(input_path),
                    language,
                    engine,
                    output_format
                )
                
                if not ocr_result:
                    raise HTTPException(status_code=500, detail="Failed to perform OCR on PDF")
                
                # Save results
                if output_format == "json":
                    output_filename = f"ocr_{Path(file.filename).stem}.json"
                    output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(ocr_result, f, indent=2, ensure_ascii=False)
                    media_type = "application/json"
                else:
                    output_filename = f"ocr_{Path(file.filename).stem}.txt"
                    output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        if isinstance(ocr_result, dict):
                            for page_data in ocr_result.get("pages", []):
                                f.write(f"Page {page_data.get('page_number', '?')}:\n")
                                f.write(page_data.get("text", "") + "\n\n")
                        else:
                            f.write(str(ocr_result))
                    media_type = "text/plain"
                
                # Return the OCR result file
                return FileResponse(
                    path=str(output_path),
                    media_type=media_type,
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/ocr", response_model=PDFProcessingResponse)
        async def perform_ocr(request: OCRRequest) -> PDFProcessingResponse:
            """Extract text from PDF using OCR."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = Path(self.upload_dir) / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Perform OCR
                ocr_result = await self._perform_ocr_on_pdf(
                    str(input_path),
                    request.language,
                    request.engine,
                    request.output_format
                )
                
                if not ocr_result:
                    raise HTTPException(status_code=500, detail="Failed to perform OCR on PDF")
                
                # Save results
                if request.output_format == "json":
                    output_filename = f"ocr_{Path(request.file_name).stem}.json"
                    output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(ocr_result, f, indent=2, ensure_ascii=False)
                else:
                    output_filename = f"ocr_{Path(request.file_name).stem}.txt"
                    output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        if isinstance(ocr_result, dict):
                            # If JSON format requested but saved as TXT, extract text
                            for page_data in ocr_result.get("pages", []):
                                f.write(f"Page {page_data.get('page_number', '?')}:\n")
                                f.write(page_data.get("text", "") + "\n\n")
                        else:
                            f.write(str(ocr_result))
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get file size
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                # Count extracted text
                if isinstance(ocr_result, dict):
                    total_chars = sum(len(page.get("text", "")) for page in ocr_result.get("pages", []))
                    page_count = len(ocr_result.get("pages", []))
                else:
                    total_chars = len(str(ocr_result))
                    page_count = 1
                
                return PDFProcessingResponse(
                    success=True,
                    message=f"OCR completed successfully. Extracted {total_chars} characters from {page_count} pages",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "ocr",
                        "input_file": request.file_name,
                        "output_file": output_path.name,
                        "language": request.language,
                        "engine": request.engine,
                        "output_format": request.output_format,
                        "pages_processed": page_count,
                        "characters_extracted": total_chars
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"OCR error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to perform OCR",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/ocr", "/process"]
    
    def _check_tesseract_available(self) -> bool:
        """Check if Tesseract is installed and available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def _check_easyocr_available(self) -> bool:
        """Check if EasyOCR is available."""
        try:
            import easyocr
            return True
        except ImportError:
            return False
    
    def _perform_ocr_tesseract(self, image) -> Optional[str]:
        """Perform OCR using Tesseract (CPU-based)."""
        try:
            import pytesseract
            from PIL import Image
            
            # Convert to PIL Image if needed
            if not isinstance(image, Image.Image):
                image = Image.open(io.BytesIO(image))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            self.logger.error(f"Tesseract OCR error: {str(e)}")
            return None
    
    def _perform_ocr_easyocr(self, image, language: str = "en") -> Optional[str]:
        """Perform OCR using EasyOCR (GPU-capable)."""
        try:
            import easyocr
            from PIL import Image
            import numpy as np
            
            # Convert to numpy array if needed
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                pil_image = Image.open(io.BytesIO(image))
                image_array = np.array(pil_image)
            
            # Initialize reader (will use GPU if available)
            reader = easyocr.Reader([language])
            
            # Perform OCR
            results = reader.readtext(image_array)
            
            # Extract text from results
            text = " ".join([result[1] for result in results])
            return text
            
        except Exception as e:
            self.logger.error(f"EasyOCR error: {str(e)}")
            return None
    
    async def _perform_ocr_on_pdf(self, pdf_path: str, language: str = "eng", 
                                 engine: str = "tesseract", output_format: str = "txt"):
        """
        Perform OCR on all pages of a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            language: OCR language code
            engine: OCR engine ('tesseract' or 'easyocr')
            output_format: Output format ('txt' or 'json')
        
        Returns:
            OCR results as string or dictionary
        """
        try:
            # Check engine availability
            if engine == "tesseract" and not self._check_tesseract_available():
                raise Exception("Tesseract not available. Please install tesseract-ocr.")
            elif engine == "easyocr" and not self._check_easyocr_available():
                raise Exception("EasyOCR not available. Please install easyocr package.")
            
            # Open PDF
            pdf_document = fitz.open(pdf_path)
            
            if output_format == "json":
                results = {
                    "file_name": Path(pdf_path).name,
                    "pages": [],
                    "total_pages": pdf_document.page_count
                }
            else:
                results = ""
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better OCR
                img_data = pix.tobytes("png")
                
                # Perform OCR
                if engine == "tesseract":
                    # Convert language code (tesseract uses different codes)
                    tesseract_lang = "eng" if language in ["en", "eng"] else language
                    text = self._perform_ocr_tesseract(img_data)
                else:  # easyocr
                    # Convert language code (easyocr uses different codes)
                    easyocr_lang = "en" if language in ["eng", "en"] else language
                    text = self._perform_ocr_easyocr(img_data, easyocr_lang)
                
                if text is None:
                    text = f"[OCR failed for page {page_num + 1}]"
                
                # Add to results
                if output_format == "json":
                    results["pages"].append({
                        "page_number": page_num + 1,
                        "text": text.strip(),
                        "character_count": len(text.strip())
                    })
                else:
                    results += f"Page {page_num + 1}:\n{text.strip()}\n\n"
            
            pdf_document.close()
            return results
            
        except Exception as e:
            self.logger.error(f"OCR processing error: {str(e)}")
            return None


def main():
    """Run the PDF OCR service."""
    service = PDFOCRService()
    service.run()


if __name__ == "__main__":
    main()