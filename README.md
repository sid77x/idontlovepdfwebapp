# IDontLovePDF 📄

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**A modern, privacy-first PDF manipulation suite with a React frontend and FastAPI microservices backend.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API Docs](http://localhost:8000/docs) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### Core Operations
- ✅ **Merge PDF** - Combine multiple PDF files into one
- ✅ **Split PDF** - Split pages into separate files or by ranges
- ✅ **Rotate PDF** - Rotate specific pages or entire documents
- ✅ **Protect PDF** - Add password protection to your PDFs
- ✅ **Compress PDF** - Reduce file size while maintaining quality
- ✅ **Watermark PDF** - Add customizable text watermarks with rotation

### Conversion Tools
- ✅ **OCR** - Extract text from scanned PDFs
- ✅ **PDF to Image** - Convert PDF pages to PNG/JPG/TIFF
- ✅ **Image to PDF** - Convert multiple images to a single PDF
- ✅ **HTML to PDF** - Convert HTML content to PDF documents

### Coming Soon
- 📋 PDF to Word/Excel/PowerPoint and vice versa
- 📋 Page Numbers, Crop, Repair tools

## 🚀 Quick Start

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-16+-339933?style=for-the-badge&logo=node.js&logoColor=white)
![npm](https://img.shields.io/badge/npm-latest-CB3837?style=for-the-badge&logo=npm&logoColor=white)

### 1️⃣ Backend Setup (Microservices)

```bash
# Navigate to microservices directory
cd microservices

# Install Python dependencies
pip install -r requirements.txt

# Start all backend services
python start_services.py
```

The backend services will start on ports 8000-8012:
- **Orchestrator**: http://localhost:8000
- **Individual Services**: ports 8001-8012

**API Documentation**: http://localhost:8000/docs

### 2️⃣ Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at **http://localhost:3000**

### 🛑 Stopping Services

**Backend:**
```bash
cd microservices
.\stop_services.ps1    # PowerShell
# or
.\stop_services.bat    # Windows CMD
```

**Frontend:**
Press `Ctrl+C` in the terminal running the dev server

### 📊 Check Service Status

```bash
cd microservices
.\check_status.ps1
```

Shows all running services with their ports and process IDs.

## 📁 Project Structure

```
IDontLovePDF/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ToolGrid.jsx   # Service cards grid
│   │   │   ├── ToolModal.jsx  # Processing modal with file upload
│   │   │   └── FileUpload.jsx # Drag & drop file upload
│   │   ├── services/          # API client
│   │   │   └── api.js         # Axios API wrapper
│   │   ├── contexts/          # React contexts
│   │   └── App.jsx            # Main app component
│   ├── package.json
│   └── vite.config.js
│
├── microservices/              # FastAPI backend
│   ├── orchestrator/          # API Gateway
│   │   └── main.py           # Routes all requests to services
│   ├── services/             # Individual microservices
│   │   ├── merge_service.py      # Port 8001
│   │   ├── rotate_service.py     # Port 8002
│   │   ├── split_service.py      # Port 8003
│   │   ├── protect_service.py    # Port 8004
│   │   ├── compress_service.py   # Port 8005
│   │   ├── watermark_service.py  # Port 8006
│   │   ├── ocr_service.py        # Port 8010
│   │   ├── pdf_to_image_service.py   # Port 8011
│   │   ├── image_to_pdf_service.py   # Port 8012
│   │   └── html_to_pdf_service.py    # Port 8018
│   ├── common.py             # Shared base classes
│   ├── start_services.py     # Start all services
│   ├── stop_services.ps1     # Stop all services
│   ├── check_status.ps1      # Check service status
│   └── requirements.txt
│
├── tools/                     # Legacy Python tools
├── utils/                     # Utility functions
└── README.md
```

## 🏗️ Architecture

### Microservices Backend
- **Orchestrator (Port 8000)** - API Gateway that routes requests to services
- **Independent Services (Ports 8001-8020)** - Each operation runs as a separate microservice
- **Service Discovery** - Automatic health monitoring and failover
- **FastAPI** - Modern, fast, async Python web framework

### React Frontend
- **Modern UI** - Clean, responsive design with Tailwind CSS
- **Real-time Processing** - Live progress updates and file size tracking
- **Success States** - Shows operation results with download buttons
- **File Upload** - Drag & drop support with preview

## 🔒 Privacy First

<div align="center">

![Privacy](https://img.shields.io/badge/Privacy-100%25_Local-success?style=for-the-badge)
![No Cloud](https://img.shields.io/badge/Cloud-No_Uploads-critical?style=for-the-badge)
![No Tracking](https://img.shields.io/badge/Tracking-None-success?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open_Source-Yes-blue?style=for-the-badge)

</div>

- **100% Local Processing** - All files are processed on your machine
- **No Cloud Uploads** - Your files never leave your computer
- **No Tracking** - No analytics, no data collection
- **Open Source** - Full transparency

## 🛠️ Technology Stack

### Backend

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyPDF2](https://img.shields.io/badge/PyPDF2-PDF-red?style=for-the-badge)
![Pillow](https://img.shields.io/badge/Pillow-Image-blue?style=for-the-badge)

- **FastAPI** - High-performance async API framework
- **PyPDF2** - PDF manipulation
- **pikepdf** - Advanced PDF operations & password handling
- **reportlab** - PDF generation and overlays
- **Pillow** - Image processing
- **PyMuPDF (fitz)** - High-quality PDF rendering
- **pytesseract** - OCR text recognition
- **weasyprint** - HTML to PDF conversion

### Frontend

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Axios](https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white)

- **React** - Modern UI library
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)
- 100MB free disk space
- Modern web browser

## 🗺️ Roadmap

### ✅ Completed
- Modern React frontend with Tailwind CSS
- FastAPI microservices architecture
- 10 working PDF operations
- Service orchestrator with health monitoring
- File upload with drag & drop
- Success states with download buttons
- File size tracking and operation results
- Service management scripts (start/stop/status)

### 🚧 In Progress
- Fix compress service (improve compression ratios)
- Add office conversion services (Word, Excel, PowerPoint)
- Implement page numbers, crop, and repair services

### 📋 Coming Soon
- PDF preview feature
- Batch processing
- Job queue for large files
- Docker deployment
- Authentication & user accounts
- Persistent storage options

## 💡 Usage

1. **Start Backend**: Run `python start_services.py` in the `microservices` directory
2. **Start Frontend**: Run `npm run dev` in the `frontend` directory
3. **Open Browser**: Navigate to http://localhost:3000
4. **Select Tool**: Click on any PDF operation card
5. **Upload Files**: Drag & drop or click to upload your PDF(s)
6. **Configure Options**: Set operation-specific parameters
7. **Process**: Click "Process Files" and wait for completion
8. **Download**: Get your processed file with detailed statistics

### Features in Action

- **File Size Tracking** - See original vs. processed file sizes
- **Operation Results** - Get specific feedback for each operation
  - Compress: "Reduced by 56KB (12% smaller)"
  - Merge: "Merged 3 PDFs into 1 document"
  - Rotate: "Rotated all pages by 90°"
- **Download Button** - Keep modal open to download or process another file
- **Process Another** - Reset form without closing modal

## 🔧 API Usage

### Via cURL

```bash
# Merge PDFs
curl -X POST "http://localhost:8000/merge" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  --output merged.pdf

# Rotate PDF
curl -X POST "http://localhost:8000/rotate" \
  -F "file=@document.pdf" \
  -F "rotation=90" \
  -F "pages=1,3,5" \
  --output rotated.pdf

# Split PDF
curl -X POST "http://localhost:8000/split" \
  -F "file=@document.pdf" \
  -F "split_type=each" \
  --output split.zip

# Add Watermark
curl -X POST "http://localhost:8000/watermark" \
  -F "file=@document.pdf" \
  -F "text=CONFIDENTIAL" \
  -F "opacity=0.5" \
  -F "font_size=60" \
  --output watermarked.pdf
```

### API Documentation
Interactive API docs available at: http://localhost:8000/docs

## 🐛 Troubleshooting

### Backend Issues

**Services won't start**
```bash
# Check if ports are in use
netstat -ano | findstr "8000 8001 8002"

# Stop conflicting services
.\microservices\stop_services.ps1

# Restart services
python microservices/start_services.py
```

**Check service status**
```bash
cd microservices
.\check_status.ps1
```

**Individual service errors**
- Check `microservices/services/temp/` for temporary files
- Ensure Python dependencies are installed: `pip install -r microservices/requirements.txt`
- Check service logs in the terminal

### Frontend Issues

**Frontend won't start**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**API connection errors**
- Ensure backend is running on port 8000
- Check `frontend/src/services/api.js` for correct API URL
- Verify CORS is enabled in backend

**File upload fails**
- Check file size limits (default: 100MB)
- Ensure file format is supported
- Check browser console for errors

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📸 Screenshots

### Frontend Interface
- Modern card-based UI with 21 PDF tools
- Real-time processing with progress indicators
- Success states showing file sizes and download buttons
- Drag & drop file upload with previews

### API Documentation
- Interactive Swagger UI at http://localhost:8000/docs
- Complete API reference with examples
- Test endpoints directly from browser

## 🤝 Contributing

![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)
![Issues](https://img.shields.io/badge/Issues-welcome-blue.svg?style=flat-square)

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. ✨ Make your changes
4. ✅ Test thoroughly (backend and frontend)
5. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
6. 📤 Push to the branch (`git push origin feature/amazing-feature`)
7. 🎉 Open a Pull Request

## 📄 License

This project is open source and available for personal and commercial use.

## 👨‍💻 Author

Built with ❤️ for privacy-conscious PDF users

---

<div align="center">

### ⭐ Star this repo if you find it useful!

![GitHub stars](https://img.shields.io/github/stars/sid77x/idontlovepdfwebapp?style=social)
![GitHub forks](https://img.shields.io/github/forks/sid77x/idontlovepdfwebapp?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/sid77x/idontlovepdfwebapp?style=social)

**10 PDF tools available** • **Microservices architecture** • **Modern React UI** • **100% Local Processing**

Made with ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white) ![React](https://img.shields.io/badge/-React-61DAFB?style=flat&logo=react&logoColor=black) ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)

</div>
