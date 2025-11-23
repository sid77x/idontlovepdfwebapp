# OCR Setup Guide

The OCR tool supports two engines:
- **Tesseract OCR** (CPU-only, lightweight, fast)
- **EasyOCR** (CPU/GPU, more accurate, supports 80+ languages)

## Installation

### 1. Install Python Dependencies

```bash
pip install pytesseract easyocr torch numpy
```

### 2. Install Tesseract OCR (System Dependency)

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

#### Windows
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path (e.g., `C:\Program Files\Tesseract-OCR`)
3. Add the installation path to your system PATH environment variable

### 3. Verify Installation

```bash
tesseract --version
```

You should see the Tesseract version information.

## GPU Acceleration (Optional)

EasyOCR can use GPU acceleration for faster processing if you have an NVIDIA GPU with CUDA support.

### Check GPU Availability

```python
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
print(f"GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
```

### Install CUDA Support

If you want GPU acceleration:

1. Install NVIDIA CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Install PyTorch with CUDA support:

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

The OCR tool will automatically detect and use GPU if available!

## Language Support

### Tesseract Languages

To add more languages to Tesseract:

#### Ubuntu/Debian
```bash
# For example, to add French, German, and Spanish
sudo apt-get install tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa
```

#### macOS
```bash
brew install tesseract-lang
```

### EasyOCR Languages

EasyOCR supports 80+ languages out of the box. Just select them in the UI!

Supported languages include:
- English, Spanish, French, German, Italian, Portuguese
- Chinese (Simplified & Traditional), Japanese, Korean
- Arabic, Russian, Hindi, and many more

## Performance Tips

### For Best Results

1. **Use High DPI**: Set DPI to 300-600 for better accuracy
2. **Clean Scans**: Use high-quality, well-lit scans with good contrast
3. **Choose Right Engine**:
   - Tesseract: Fast, good for English documents
   - EasyOCR: More accurate, better for multi-language and complex layouts

### Speed Optimization

- **CPU**: Tesseract is typically faster on CPU for simple documents
- **GPU**: EasyOCR with GPU is much faster for complex documents
- **Batch Processing**: Process multiple pages in one go rather than one at a time

## Troubleshooting

### Tesseract Not Found Error

**Windows**: Make sure Tesseract is in your PATH. You can also set it manually in Python:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac**: Install Tesseract using the package manager (see above)

### GPU Not Detected

1. Check if CUDA is installed: `nvidia-smi`
2. Verify PyTorch can see GPU: `python -c "import torch; print(torch.cuda.is_available())"`
3. Make sure you installed the CUDA version of PyTorch (not CPU-only)

### Out of Memory Error

If you get OOM errors with GPU:
1. Reduce the DPI setting
2. Process fewer pages at once
3. Use CPU instead (slower but uses system RAM)

## Usage in the App

1. Select **OCR (Text Recognition)** from the tool menu
2. Choose your OCR engine (Tesseract or EasyOCR)
3. For EasyOCR: Select languages to recognize
4. Set image quality (DPI): 300 is good, 600 for high accuracy
5. Choose output format:
   - **Text File**: Extract all text to a .txt file
   - **Searchable PDF**: Add invisible text layer to PDF (makes it searchable/selectable)
6. Upload your scanned PDF
7. Click "Extract Text with OCR"

The tool will automatically use GPU if available for EasyOCR!

## Comparison: Tesseract vs EasyOCR

| Feature | Tesseract | EasyOCR |
|---------|-----------|---------|
| Speed (CPU) | Fast | Moderate |
| Speed (GPU) | N/A | Very Fast |
| Accuracy | Good | Excellent |
| Languages | 100+ (requires download) | 80+ (built-in) |
| Setup | Requires system install | Python only |
| Multi-language | Single language at a time | Multiple languages simultaneously |
| Best for | English documents, fast processing | Complex layouts, mixed languages |

Choose based on your needs:
- **Quick English documents**: Use Tesseract
- **Multi-language documents**: Use EasyOCR
- **Highest accuracy**: Use EasyOCR with GPU
- **No GPU available**: Both work fine on CPU
