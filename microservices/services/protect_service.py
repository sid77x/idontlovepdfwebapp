"""
PDF Protection/Unlock Microservice
Handles adding and removing password protection from PDF files.
"""
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Optional

import pikepdf
from fastapi import UploadFile, HTTPException, File, Form
from fastapi.responses import FileResponse

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from microservices.common.base_service import BasePDFMicroservice
from microservices.common.models import (
    PDFOperationType, PDFProcessingResponse, 
    ProtectRequest, UnlockRequest
)
from utils.file_ops import get_unique_filename, get_file_size_mb


class PDFProtectService(BasePDFMicroservice):
    """PDF Protection/Unlock microservice."""
    
    def __init__(self, host: str = "localhost", port: int = 8004):
        super().__init__(
            service_name="pdf-protect-service",
            operation_type=PDFOperationType.PROTECT,
            host=host,
            port=port
        )
    
    def _register_service_routes(self):
        """Register service-specific routes."""
        
        @self.app.post("/process")
        async def process_pdf(
            file: UploadFile = File(...),
            user_password: str = Form(...),
            owner_password: str = Form(None)
        ):
            """Process PDF file - add password protection."""
            try:
                # Save uploaded file
                input_path = Path(self.upload_dir) / file.filename
                with open(input_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Check if file is already encrypted
                try:
                    with pikepdf.open(input_path) as test_pdf:
                        pass  # File is not encrypted
                except pikepdf.PasswordError:
                    raise HTTPException(status_code=400, detail="PDF is already password-protected")
                
                # Generate output filename
                output_filename = f"protected_{file.filename}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Protect PDF
                success = await self._protect_pdf_file(
                    str(input_path),
                    str(output_path),
                    user_password,
                    owner_password,
                    allow_printing=True,
                    allow_modification=False
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to protect PDF")
                
                # Return the protected file
                return FileResponse(
                    path=str(output_path),
                    media_type="application/pdf",
                    filename=output_path.name
                )
                
            except Exception as e:
                self.logger.error(f"Process error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/protect", response_model=PDFProcessingResponse)
        async def protect_pdf(request: ProtectRequest) -> PDFProcessingResponse:
            """Add password protection to a PDF file."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = Path(self.upload_dir) / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Check if file is already encrypted
                try:
                    with pikepdf.open(input_path) as test_pdf:
                        pass  # File is not encrypted
                except pikepdf.PasswordError:
                    raise HTTPException(status_code=400, detail="PDF is already password-protected")
                
                # Generate output filename
                output_filename = f"protected_{request.file_name}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Protect PDF
                success = await self._protect_pdf_file(
                    str(input_path),
                    str(output_path),
                    request.user_password,
                    request.owner_password,
                    request.allow_printing,
                    request.allow_modification
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to protect PDF")
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get file size
                file_size_mb = get_file_size_mb(str(output_path))
                
                return PDFProcessingResponse(
                    success=True,
                    message="PDF protected successfully",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "protect",
                        "input_file": request.file_name,
                        "output_file": output_path.name,
                        "allow_printing": request.allow_printing,
                        "allow_modification": request.allow_modification
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Protection error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to protect PDF",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
        
        @self.app.post("/unlock", response_model=PDFProcessingResponse)
        async def unlock_pdf(request: UnlockRequest) -> PDFProcessingResponse:
            """Remove password protection from a PDF file."""
            start_time = time.time()
            
            try:
                # Validate file exists
                input_path = Path(self.upload_dir) / request.file_name
                if not input_path.exists():
                    raise HTTPException(status_code=404, detail=f"File {request.file_name} not found")
                
                # Generate output filename
                output_filename = f"unlocked_{request.file_name}"
                output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
                
                # Unlock PDF
                success = await self._unlock_pdf_file(
                    str(input_path),
                    str(output_path),
                    request.password
                )
                
                if not success:
                    raise HTTPException(status_code=401, detail="Incorrect password or failed to unlock PDF")
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get file size
                file_size_mb = get_file_size_mb(str(output_path))
                
                return PDFProcessingResponse(
                    success=True,
                    message="PDF unlocked successfully",
                    file_url=f"/download/{output_path.name}",
                    file_size_mb=file_size_mb,
                    processing_time_ms=processing_time,
                    operation_id=request.operation_id,
                    metadata={
                        "operation": "unlock",
                        "input_file": request.file_name,
                        "output_file": output_path.name
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Unlock error: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return PDFProcessingResponse(
                    success=False,
                    message="Failed to unlock PDF",
                    processing_time_ms=processing_time,
                    error_details=str(e)
                )
    
    def _get_service_endpoints(self) -> list:
        """Get service-specific endpoints."""
        return ["/protect", "/unlock", "/process"]
    
    async def _protect_pdf_file(self, input_path: str, output_path: str, 
                               user_password: str, owner_password: Optional[str],
                               allow_printing: bool, allow_modification: bool) -> bool:
        """
        Add password protection to a PDF file.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save protected PDF
            user_password: Password to open the PDF
            owner_password: Password for owner permissions
            allow_printing: Allow printing
            allow_modification: Allow modifications
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with pikepdf.open(input_path) as pdf:
                # Set permissions
                permissions = pikepdf.Permissions(
                    print_lowres=allow_printing,
                    print_highres=allow_printing,
                    modify_annotation=allow_modification,
                    modify_form=allow_modification,
                    modify_other=allow_modification,
                    extract=True,  # Always allow text extraction
                    accessibility=True  # Always allow accessibility
                )
                
                # Prepare encryption settings
                encryption_kwargs = {
                    "owner": owner_password if owner_password else user_password,
                    "user": user_password,
                }
                
                if allow_printing or allow_modification:
                    encryption_kwargs["allow"] = permissions
                
                # Save with encryption
                pdf.save(output_path, encryption=pikepdf.Encryption(**encryption_kwargs))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error protecting PDF: {str(e)}")
            return False
    
    async def _unlock_pdf_file(self, input_path: str, output_path: str, password: str) -> bool:
        """
        Remove password protection from a PDF file.
        
        Args:
            input_path: Path to encrypted PDF
            output_path: Path to save unlocked PDF
            password: Password to open the PDF
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with pikepdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
            
            return True
            
        except pikepdf.PasswordError:
            self.logger.warning("Incorrect password provided")
            return False
        except Exception as e:
            self.logger.error(f"Error unlocking PDF: {str(e)}")
            return False


def main():
    """Run the PDF Protection service."""
    service = PDFProtectService()
    service.run()


if __name__ == "__main__":
    main()