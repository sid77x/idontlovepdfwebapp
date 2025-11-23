# IDontLovePDF 📄

A local, privacy-first PDF manipulation suite built with Python and Streamlit.

## 🎯 Features

### Phase 1 - Core Operations ✅

✅ **Merge PDF** - Combine multiple PDF files into one  
✅ **Split PDF** - Split pages into separate files  
✅ **Rotate PDF** - Rotate specific or all pages  
✅ **Protect/Unlock PDF** - Add or remove password protection  
✅ **Compress PDF** - Reduce file size by compressing images

### Phase 2 - Layout & Annotation ✅

✅ **Watermark PDF** - Add customizable text watermarks  
✅ **Page Numbers** - Add page numbers in multiple formats  
✅ **Crop PDF** - Trim the edges of PDF pages  
✅ **Repair PDF** - Fix corrupted or damaged PDFs

### Phase 3 - Conversion Layer ✅

✅ **PDF to Image** - Convert PDF pages to PNG or JPG  
✅ **Image to PDF** - Convert multiple images to a single PDF  
✅ **PDF to Word** - Extract text and images to DOCX format  
✅ **Word to PDF** - Convert Word documents to PDF  
✅ **PDF to Excel** - Extract tables and data to XLSX  
✅ **Excel to PDF** - Convert spreadsheets to PDF  
✅ **PDF to HTML** - Convert PDF content to HTML  
✅ **HTML to PDF** - Convert HTML pages to PDF  
✅ **PDF to PowerPoint** - Convert PDF pages to PPTX slides  
✅ **PowerPoint to PDF** - Convert presentations to PDF

### Phase 4 - Intelligence Layer 🚧

✅ **OCR (Text Recognition)** - Extract text from scanned PDFs with CPU/GPU support  

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
IdontLovePDF/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── tools/             # PDF manipulation tools
│   ├── merge.py       # Merge PDFs
│   ├── split.py       # Split PDFs
│   ├── rotate.py      # Rotate pages
│   ├── protect.py     # Password protection
│   ├── compress.py    # File compression
│   ├── watermark.py   # Add watermarks
│   ├── page_numbers.py # Add page numbers
│   ├── crop.py        # Crop PDF pages
│   ├── repair.py      # Repair corrupted PDFs
│   ├── pdf_to_image.py # PDF to Image
│   ├── image_to_pdf.py # Image to PDF
│   ├── pdf_to_word.py  # PDF to Word
│   ├── word_to_pdf.py  # Word to PDF
│   ├── pdf_to_excel.py # PDF to Excel
│   ├── excel_to_pdf.py # Excel to PDF
│   ├── pdf_to_html.py  # PDF to HTML
│   ├── html_to_pdf.py  # HTML to PDF
│   ├── pdf_to_powerpoint.py # PDF to PowerPoint
│   ├── powerpoint_to_pdf.py # PowerPoint to PDF
│   └── ocr.py          # OCR Text Recognition
├── utils/             # Utility functions
│   ├── file_ops.py    # File operations
│   └── pdf_ops.py     # PDF operations
├── uploads/           # Temporary upload storage
├── outputs/           # Processed file storage
└── temp/              # Temporary files
```

## 🔒 Privacy First

- **100% Local Processing** - All files are processed on your machine
- **No Cloud Uploads** - Your files never leave your computer
- **No Tracking** - No analytics, no data collection
- **Open Source** - Full transparency

## 🛠️ Technology Stack

- **Python 3.8+**
- **Streamlit** - Web interface
- **PyPDF2** - PDF manipulation
- **pikepdf** - Advanced PDF operations & password handling
- **reportlab** - PDF generation for overlays
- **Pillow** - Image processing support
- **PyMuPDF (fitz)** - High-quality PDF rendering
- **python-docx** - Word document handling
- **openpyxl** - Excel file processing
- **python-pptx** - PowerPoint file handling
- **weasyprint** - HTML to PDF conversion
- **pytesseract** - Tesseract OCR for text recognition
- **easyocr** - Advanced OCR with GPU support
- **torch** - PyTorch for GPU acceleration

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)
- 100MB free disk space
- Modern web browser

## 🗺️ Development Roadmap

### Phase 1: Core PDF Operations ✅ Complete
- Merge, Split, Rotate, Protect, Compress

### Phase 2: Layout & Annotation Tools ✅ Complete
- Watermark, Page Numbers, Crop, Repair

### Phase 3: Conversion Layer ✅ Complete
- PDF ↔ Image, Word, Excel, PowerPoint, HTML

### Phase 4: Intelligence Layer 🚧 In Progress
- ✅ OCR (CPU/GPU with Tesseract & EasyOCR)
- 📋 Redaction, PDF/A, Compare (Coming Soon)

### Phase 5: Automation & Integration (Coming Soon)
- Workflows, Digital Signatures, Advanced Editing

## 💡 Usage Tips

### Phase 1 Tools
1. **Merge PDF**: Upload files in the order you want them merged
2. **Split PDF**: Choose between splitting all pages, custom ranges, or fixed chunks
3. **Rotate PDF**: Select specific pages or rotate all at once
4. **Protect PDF**: Set user password and configure permissions
5. **Compress PDF**: Use low/medium compression for documents, high for images

### Phase 2 Tools
6. **Watermark PDF**: Customize text, opacity, rotation, color, and position
7. **Page Numbers**: Choose from multiple formats and 6 position options
8. **Crop PDF**: Trim edges with quick presets or custom values
9. **Repair PDF**: Fix structural issues and recover readable pages

### Phase 3 Tools
10. **PDF to Image**: Convert pages to PNG/JPG with adjustable DPI
11. **Image to PDF**: Combine multiple images into one PDF
12. **PDF to Word**: Extract text and images to editable DOCX
13. **Word to PDF**: Convert DOCX files to PDF format
14. **PDF to Excel**: Extract tables and data to XLSX spreadsheets
15. **Excel to PDF**: Convert spreadsheets to PDF with styling
16. **PDF to HTML**: Convert PDF content to web-friendly HTML
17. **HTML to PDF**: Convert HTML pages/code to PDF
18. **PDF to PowerPoint**: Convert pages to PPTX slides
19. **PowerPoint to PDF**: Convert presentations to PDF format
20. **OCR**: Extract text from scanned PDFs using CPU or GPU acceleration

## 🐛 Troubleshooting

**Issue**: App won't start  
**Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Upload fails  
**Solution**: Ensure the `uploads/` directory exists and is writable

**Issue**: Compression not effective  
**Solution**: Text-heavy PDFs compress less than image-heavy ones

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👨‍💻 Author

Built with ❤️ for privacy-conscious PDF users

---

**Note**: Phases 1, 2, and 3 are complete! Phase 4 started with OCR! 20 tools available!
