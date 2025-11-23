# idontlovepdfwebapp

![Languages](https://img.shields.io/badge/Python-83.8%25-blue?logo=python)
![Languages](https://img.shields.io/badge/JavaScript-14.8%25-yellow?logo=javascript)
![Languages](https://img.shields.io/badge/PowerShell-0.5%25-blue?logo=powershell)
![Languages](https://img.shields.io/badge/Batchfile-0.3%25-lightgrey?logo=windows)
![Languages](https://img.shields.io/badge/Shell-0.3%25-black?logo=gnu-bash)
![Languages](https://img.shields.io/badge/CSS-0.2%25-blue?logo=css3)
![Languages](https://img.shields.io/badge/HTML-0.1%25-orange?logo=html5)

## Webapp for idontlovepdf

This repository contains the codebase for **idontlovepdfwebapp**, a web application for managing PDF files with an attitude! The main focus is on processing PDFs without relying on typical online services, making it ideal for privacy-conscious users or specific workflow requirements.

---

## Features

- Merge PDFs
- Split PDFs
- Rotate & Crop PDFs
- Protect/Unlock PDFs
- Compress PDFs
- Add Watermarks & Page Numbers
- OCR (Text Recognition)
- PDF ↔ Image/Word/Excel/PowerPoint/HTML conversion
- Easy-to-use web interface
- Local file processing - 100% privacy-focused
- Microservices architecture
- Written primarily in Python and JavaScript

---

## Getting Started

### 🐳 Quick Start with Docker (Recommended)

The easiest way to run IdontLovePDF is using Docker:

```bash
# Clone the repository
git clone https://github.com/sid77x/idontlovepdfwebapp.git
cd idontlovepdfwebapp

# Start all services with Docker Compose
docker-compose up -d

# Access the applications:
# - Streamlit App: http://localhost:8501
# - Microservices API: http://localhost:8000
# - React Frontend: http://localhost:3000
```

**For detailed Docker instructions**, see [DOCKER.md](DOCKER.md)

### 📦 Manual Installation

If you prefer to run without Docker:

#### Prerequisites

- Python 3.8+ installed
- `pip` for installing dependencies
- Node.js and npm (if you plan to run the frontend)
- Tesseract OCR (for OCR features)

#### Installation Steps

1. **Clone the repository:**
    ```bash
    git clone https://github.com/sid77x/idontlovepdfwebapp.git
    cd idontlovepdfwebapp
    ```

2. **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Install Tesseract OCR (for OCR features):**
    - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
    - **macOS:** `brew install tesseract`
    - **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

4. **(Optional) Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    ```

#### Running the Application

**Option 1: Streamlit App (Main UI)**
```bash
streamlit run app.py
```
Access at [http://localhost:8501](http://localhost:8501)

**Option 2: Microservices Backend**
```bash
cd microservices
python start_services.py
```
API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

**Option 3: React Frontend**
```bash
cd frontend
npm run dev
```
Access at [http://localhost:3000](http://localhost:3000)

---

## Project Structure

```
idontlovepdfwebapp/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration for Streamlit app
├── docker-compose.yml        # Docker Compose orchestration
├── DOCKER.md                 # Docker setup guide
├── tools/                    # PDF manipulation tools
├── utils/                    # Utility functions
├── microservices/            # FastAPI microservices
│   ├── Dockerfile            # Docker configuration for microservices
│   ├── orchestrator/         # Service orchestrator
│   ├── services/             # Individual PDF services
│   └── start_services.py     # Service startup script
├── frontend/                 # React frontend (optional)
│   ├── Dockerfile            # Production Docker configuration
│   ├── Dockerfile.dev        # Development Docker configuration
│   ├── src/                  # React source code
│   └── package.json          # Node.js dependencies
└── README.md
```

## 🐳 Docker Deployment

This application is fully dockerized for easy deployment:

- **Streamlit App**: Main PDF manipulation interface
- **Microservices**: FastAPI-based backend services
- **Frontend**: Modern React interface

See [DOCKER.md](DOCKER.md) for comprehensive Docker documentation including:
- Production deployment
- Development setup
- Environment configuration
- Health checks and monitoring
- Troubleshooting guide

---

## Contributing

Contributions, suggestions, and improvements are welcome!
- Fork this repo
- Create a branch for your feature/fix
- Submit a pull request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Contact

For questions or support, open an issue or contact [sid77x](https://github.com/sid77x).