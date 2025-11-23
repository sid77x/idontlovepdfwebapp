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
- Node.js and npm (if you plan to modify frontend components)

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/sid77x/idontlovepdfwebapp.git
    cd idontlovepdfwebapp
    ```
2. **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **(Optional) Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    ```

### Running

1. **Start the backend:**
    ```bash
    python app.py
    ```
    or based on your project structure (e.g., Flask, Django), use the appropriate run command.

2. **Run the frontend (if separate):**
    ```bash
    cd frontend
    npm start
    ```

3. **Access the app:**
    Open [http://localhost:5000](http://localhost:5000) (or appropriate port).

---

## Project Structure

```
idontlovepdfwebapp/
├── app.py                # Python backend application
├── requirements.txt      # Python dependencies
├── static/               # Static files (JS, CSS, images)
├── templates/            # HTML templates
├── frontend/             # Frontend app (if applicable)
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