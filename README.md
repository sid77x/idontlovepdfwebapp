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
- Convert to/from PDF (coming soon)
- Easy-to-use web interface
- Local file processing
- Written primarily in Python and JavaScript

---

## Getting Started

### Prerequisites

- Python 3.8+ installed
- `pip` for installing dependencies

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/sid77x/idontlovepdfwebapp.git
    cd idontlovepdfwebapp
    ```

2. **Install main application dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **(Optional) Install microservices dependencies:**
    
    **Windows:**
    ```cmd
    cd microservices
    install.bat
    ```
    
    **Linux/Mac:**
    ```bash
    cd microservices
    chmod +x install.sh
    ./install.sh
    ```

### Running the Application

This project has two components you can run:

#### Option 1: Main Web Application (Streamlit UI)

Start the Streamlit-based web interface:

```bash
streamlit run app.py
```

Then open your browser to [http://localhost:8501](http://localhost:8501)

#### Option 2: Microservices Architecture (FastAPI Backend)

Start all PDF microservices:

**Windows:**
```cmd
cd microservices
start_services.bat
```

**Linux/Mac:**
```bash
cd microservices
python start_services.py
```

**Services will be available at:**
- Orchestrator API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Merge Service: [http://localhost:8001/docs](http://localhost:8001/docs)
- Rotate Service: [http://localhost:8002/docs](http://localhost:8002/docs)
- Split Service: [http://localhost:8003/docs](http://localhost:8003/docs)

**To stop services:**

**Windows:**
```cmd
cd microservices
stop_services.bat
```

**Linux/Mac:**
```bash
cd microservices
python stop_services.py
```

**To check service status:**

**Windows:**
```cmd
cd microservices
service_status.bat
```

**Linux/Mac:**
```bash
cd microservices
python stop_services.py status
```

---

## Project Structure

```
idontlovepdfwebapp/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Main application dependencies
├── tools/                      # PDF manipulation tools/modules
├── utils/                      # Utility functions
├── microservices/              # FastAPI microservices architecture
│   ├── install.bat            # Windows installer for microservices
│   ├── install.sh             # Linux/Mac installer for microservices
│   ├── start_services.bat     # Windows: Start all microservices
│   ├── start_services.py      # Python: Start all microservices
│   ├── stop_services.bat      # Windows: Stop all microservices
│   ├── stop_services.py       # Python: Stop all microservices
│   ├── service_status.bat     # Windows: Check service status
│   ├── orchestrator/          # Main orchestrator service
│   ├── services/              # Individual PDF microservices
│   ├── common/                # Shared microservice code
│   ├── requirements.txt       # Microservices dependencies
│   └── README.md             # Detailed microservices documentation
├── frontend/                   # Frontend resources
└── README.md
```

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