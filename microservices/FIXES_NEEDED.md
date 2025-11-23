# Microservices Fixes Needed

## Summary of Work Completed (November 14, 2025)

### Issue Diagnosed and Fixed
**Problem**: All microservices were returning 404 "Not Found" errors when called through the orchestrator, even though services were healthy and registered correctly.

**Root Cause**: The orchestrator was trying to call `/process` endpoints on microservices for file upload operations, but the services only had operation-specific endpoints (like `/compress`, `/rotate`, `/protect`) that expected JSON request bodies, not multipart/form-data file uploads.

**Solution**: Added `/process` endpoints to microservices that:
- Accept file uploads via multipart/form-data
- Handle Form parameters for operation-specific settings
- Return the processed PDF file directly as FileResponse
- Fixed directory references (`temp_dir` → `upload_dir`)

### Services Fixed Today
1. ✅ **Compress Service** (port 8005)
   - Added `/process` endpoint accepting `file` and `quality` parameters
   - Returns compressed PDF directly
   - Tested and working through orchestrator

2. ✅ **Rotate Service** (port 8002)
   - Added `/process` endpoint accepting `file`, `rotation`, and `pages` parameters
   - Returns rotated PDF directly
   - Ready for testing

3. ✅ **Protect Service** (port 8004)
   - Added `/process` endpoint accepting `file`, `user_password`, and `owner_password` parameters
   - Returns protected PDF directly
   - Fixed all `temp_dir` → `upload_dir` references
   - Ready for testing

### Test Results
- ✅ Compress service works directly: `http://localhost:8005/process`
- ✅ Compress works through orchestrator: `http://localhost:8000/compress`
- ✅ Returns valid PDF files
- ✅ Frontend at `http://localhost:3000` can now process files

---

## ✅ COMPLETED: Backend `/process` Endpoints

All core services now have `/process` endpoints with multipart/form-data file uploads!

### ✅ Services With `/process` Endpoint (DONE)

#### High Priority (Core Operations) - COMPLETED
- [x] **Merge Service** (port 8001)
  - ✅ `/process` accepting multiple files via multipart/form-data
  - Parameters: `files` (multiple UploadFile)
  
- [x] **Split Service** (port 8003)
  - ✅ `/process` accepting `file` and `split_type`, `pages` parameters
  - Parameters: `file` (UploadFile), `split_type` (Form string), `pages` (Form string)
  
- [x] **Watermark Service** (port 8006)
  - ✅ `/process` accepting `file`, `text`, `opacity`, `font_size`, `position`, `rotation`
  - Parameters: `file` (UploadFile), watermark settings as Form fields
  - Default: 45° rotation, 0.5 opacity, 60pt font

#### Medium Priority (Conversion Services) - COMPLETED
- [x] **OCR Service** (port 8010)
  - ✅ `/process` accepting `file`, `language`, `engine`, `output_format`
  - Parameters: `file` (UploadFile), `language` (Form string), `engine` (Form string), `output_format` (Form string)
  
- [x] **PDF to Image Service** (port 8011)
  - ✅ `/process` accepting `file`, `format`, `dpi`, `pages`
  - Parameters: `file` (UploadFile), `format` (Form string), `dpi` (Form int), `pages` (Form string)
  
- [x] **Image to PDF Service** (port 8012)
  - ✅ `/process` accepting single or multiple image files
  - Parameters: `files` (multiple UploadFile)

#### Lower Priority (Office Conversions)
- [ ] **PDF to Word Service** (port 8013)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)
  
- [ ] **Word to PDF Service** (port 8014)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)
  
- [ ] **PDF to Excel Service** (port 8015)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)
  
- [ ] **Excel to PDF Service** (port 8016)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)
  
- [ ] **PDF to HTML Service** (port 8017)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)
  
- [ ] **HTML to PDF Service** (port 8018)
  - Need: `/process` accepting `file` or `html_content`
  - Parameters: `file` (UploadFile, optional), `html_content` (Form string, optional)
  
- [ ] **PDF to PowerPoint Service** (port 8019)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)
  
- [ ] **PowerPoint to PDF Service** (port 8020)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)

#### Additional Services
- [ ] **Page Numbers Service** (port 8007)
  - Need: `/process` accepting `file`, `position`, `format`
  - Parameters: `file` (UploadFile), positioning and format as Form fields
  
- [ ] **Crop Service** (port 8008)
  - Need: `/process` accepting `file`, `top`, `bottom`, `left`, `right`
  - Parameters: `file` (UploadFile), crop dimensions as Form fields
  
- [ ] **Repair Service** (port 8009)
  - Need: `/process` accepting `file`
  - Parameters: `file` (UploadFile)

---

## Implementation Pattern (Copy from Compress Service)

For each service, follow this pattern:

### 1. Add imports
```python
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path
```

### 2. Add `/process` endpoint in `_register_service_routes()`
```python
@self.app.post("/process")
async def process_pdf(
    file: UploadFile = File(...),
    # Add service-specific Form parameters here
):
    """Process PDF file - [operation description]."""
    try:
        # Save uploaded file
        input_path = Path(self.upload_dir) / file.filename
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate output filename
        output_filename = f"[prefix]_{file.filename}"
        output_path = Path(get_unique_filename(output_filename, str(self.output_dir)))
        
        # Perform the operation
        success = await self._[operation]_file(
            str(input_path),
            str(output_path),
            # operation-specific parameters
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process PDF")
        
        # Return the processed file
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",  # or appropriate mime type
            filename=output_path.name
        )
        
    except Exception as e:
        self.logger.error(f"Process error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Update `_get_service_endpoints()`
```python
def _get_service_endpoints(self) -> list:
    """Get service-specific endpoints."""
    return ["/[original-endpoint]", "/process"]
```

### 4. Fix any `temp_dir` references
Search for `self.temp_dir` and replace with `Path(self.upload_dir)`

### 5. Restart the service
```bash
# Kill the service
netstat -ano | findstr :[PORT] | Select-String "LISTENING" | ForEach-Object { Stop-Process -Id ($_.ToString().Split()[-1]) -Force }

# Start the service
Start-Process python -ArgumentList "microservices\services\[service_name].py" -WindowStyle Hidden
```

### 6. Test the service
```bash
# Test directly
curl.exe -X POST "http://localhost:[PORT]/process" -F "file=@test.pdf" -F "[param]=value" --output "output.pdf"

# Test through orchestrator
curl.exe -X POST "http://localhost:8000/[operation]" -F "file=@test.pdf" -F "[param]=value" --output "output.pdf"
```

---

## Notes
- The orchestrator already has the correct multipart/form-data routes configured
- All services are already registered and healthy
- The frontend is already set up to send multipart/form-data requests
- Once all services have `/process` endpoints, the entire system will work end-to-end
- Services can keep their original JSON-based endpoints for backward compatibility

---

## Additional Frontend & Backend Improvements Needed

### Backend Issues
- [ ] **Fix Compress Service Compression**
  - Problem: Compress service only reduces file size by ~1KB (ineffective compression)
  - Location: `microservices/services/compress_service.py` - `_compress_pdf_file()` method
  - Need to: Implement better compression algorithms (pikepdf with higher compression, image resampling, etc.)
  - Consider: Quality presets (low=aggressive, medium=balanced, high=minimal)

- [x] **Fix Service Shutdown Behavior** ✅ COMPLETED
  - ✅ Created `stop_services.ps1` - PowerShell script to stop all services
  - ✅ Created `check_status.ps1` - Check which services are running
  - ✅ Created `stop_services.bat` - Batch file alternative
  - Solution: Scripts find processes by port and terminate them gracefully
  - Usage:
    - `.\stop_services.ps1` - Stop all running microservices
    - `.\check_status.ps1` - Check status of all services
  - Features:
    - Checks all 21 service ports (8000-8020)
    - Shows which services are running/stopped
    - Displays process IDs
    - Gracefully terminates all found processes
    - Summary of stopped services

### Frontend UX Improvements
- [ ] **Add Download Button After Processing**
  - Problem: Modal closes immediately after processing completes
  - Location: `frontend/src/components/ToolModal.jsx`
  - Need to: Show success state with download button instead of auto-closing
  - Features:
    - Keep modal open after success
    - Display "Processing Complete!" message
    - Show download button for processed file
    - Show file size of output
    - Add "Process Another File" button to reset
    - Add "Close" button

- [ ] **Display File Size Information**
  - Problem: No file size information shown after processing
  - Location: `frontend/src/components/ToolModal.jsx`
  - Need to: Display both input and output file sizes
  - Show: Original size, Final size, Size difference

- [ ] **Show Operation-Specific Results**
  - Problem: Generic success message doesn't show operation details
  - Location: `frontend/src/components/ToolModal.jsx`
  - Need to: Display operation-specific metrics
  - Examples:
    - Compress: "Reduced by 56KB (12% smaller)" or "Compressed from 500KB to 444KB"
    - Rotate: "Rotated 5 pages by 90°"
    - Protect: "Password protection added successfully"
    - Merge: "Merged 3 PDFs into 1 (1.2MB total)"
    - Split: "Created 10 files from 50 pages"
  - Implementation: Parse metadata from backend response and display user-friendly messages

- [ ] **Add PDF Preview Feature**
  - Problem: No way to preview PDF before or after processing
  - Location: Create new `frontend/src/components/PDFPreview.jsx`
  - Features:
    - Preview uploaded PDF before processing
    - Preview processed PDF after operation
    - Show first page thumbnail
    - Option to view full PDF in modal
  - Libraries: Consider using `react-pdf` or `pdfjs-dist`
  - Integration: Add preview option in ToolModal

- [x] **Add All Services to Frontend UI** ✅ COMPLETED
  - ✅ Added 11 new services to ToolGrid (21 total services now)
  - ✅ All working backend services now visible in frontend
  - Services added:
    - Page Numbers, Crop, Repair (marked "Coming Soon")
    - PDF-to-Word, Word-to-PDF (marked "Coming Soon")
    - PDF-to-Excel, Excel-to-PDF (marked "Coming Soon")
    - PDF-to-HTML (marked "Coming Soon")
    - PDF-to-PowerPoint, PowerPoint-to-PDF (marked "Coming Soon")
  - ✅ All 10 working services available: Merge, Split, Rotate, Protect, Compress, Watermark, OCR, PDF-to-Image, Image-to-PDF, HTML-to-PDF

- [x] **Add Download Button After Processing** ✅ COMPLETED
  - ✅ Modal now stays open after processing completes
  - ✅ Shows success icon with checkmark
  - ✅ Download button for processed file
  - ✅ "Process Another File" button to reset form
  - ✅ "Close" button to dismiss modal

- [x] **Display File Size Information** ✅ COMPLETED
  - ✅ Shows original file size
  - ✅ Shows final file size
  - ✅ Shows size difference for compress operations
  - ✅ Formatted in KB/MB/GB units

- [x] **Show Operation-Specific Results** ✅ COMPLETED
  - ✅ Compress: "Reduced by 56KB (12% smaller)"
  - ✅ Rotate: "Rotated all pages by 90°"
  - ✅ Protect: "Password protection added successfully"
  - ✅ Merge: "Merged 3 PDFs into 1 document"
  - ✅ Split: "PDF split successfully"
  - ✅ Watermark: "Watermark added successfully"
  - ✅ OCR: "Text extracted successfully"
  - ✅ PDF-to-Image: "PDF converted to images"
  - ✅ Image-to-PDF: "Converted 2 image(s) to PDF"
  - ✅ HTML-to-PDF: "HTML converted to PDF successfully"

### Implementation Priority
1. ~~**HIGH**: Add all services to frontend UI~~ ✅ DONE
2. ~~**HIGH**: Download button + file size display~~ ✅ DONE
3. ~~**HIGH**: Show operation-specific results~~ ✅ DONE
4. **HIGH**: Fix compress service (core functionality broken)
5. **MEDIUM**: Add PDF preview (nice-to-have feature)
6. **MEDIUM**: Fix service shutdown behavior

### Example: Updated Success State UI
```
┌─────────────────────────────────────┐
│  ✓ Compression Complete!            │
│                                     │
│  Original Size:    500 KB           │
│  Compressed Size:  444 KB           │
│  Reduced by:       56 KB (11.2%)    │
│                                     │
│  [Download Compressed PDF]          │
│  [Process Another File]  [Close]    │
└─────────────────────────────────────┘
```

---

## Quick Reference: Service Ports
- 8000: Orchestrator
- 8001: Merge
- 8002: Rotate ✅
- 8003: Split
- 8004: Protect ✅
- 8005: Compress ✅ (needs compression improvement)
- 8006: Watermark
- 8007: Page Numbers
- 8008: Crop
- 8009: Repair
- 8010: OCR
- 8011: PDF to Image
- 8012: Image to PDF
- 8013: PDF to Word
- 8014: Word to PDF
- 8015: PDF to Excel
- 8016: Excel to PDF
- 8017: PDF to HTML
- 8018: HTML to PDF
- 8019: PDF to PowerPoint
- 8020: PowerPoint to PDF
