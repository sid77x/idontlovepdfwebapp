"""
PDF OCR Tool - Extract text from scanned PDFs or images in PDFs.
Supports both CPU (Tesseract) and GPU (EasyOCR with automatic GPU detection).
"""
import streamlit as st
import fitz  # PyMuPDF
import os
from PIL import Image
import io
from datetime import datetime

from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.preview import show_pdf_preview_from_file


def check_gpu_available():
    """Check if GPU is available for EasyOCR."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def check_tesseract_available():
    """Check if Tesseract is installed and available."""
    try:
        import pytesseract
        # Try to get version to verify installation
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def perform_ocr_tesseract(image):
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
    except ImportError:
        return None
    except Exception as e:
        return None


def perform_ocr_easyocr(image, languages=['en'], use_gpu=True):
    """Perform OCR using EasyOCR (supports GPU)."""
    try:
        import easyocr
        from PIL import Image
        import numpy as np
        
        # Convert to PIL Image if needed
        if not isinstance(image, Image.Image):
            image = Image.open(io.BytesIO(image))
        
        # Convert PIL Image to numpy array
        image_np = np.array(image)
        
        # Initialize reader (will automatically use GPU if available and use_gpu=True)
        reader = easyocr.Reader(languages, gpu=use_gpu)
        
        # Perform OCR
        results = reader.readtext(image_np)
        
        # Extract text from results
        text = '\n'.join([result[1] for result in results])
        return text
    except ImportError:
        st.error("EasyOCR is not installed. Please install easyocr.")
        return None
    except Exception as e:
        st.error(f"EasyOCR error: {str(e)}")
        return None


def extract_text_with_ocr(pdf_path, ocr_engine='tesseract', languages=['en'], dpi=300):
    """
    Extract text from PDF using OCR.
    
    Args:
        pdf_path: Path to the PDF file
        ocr_engine: 'tesseract' or 'easyocr'
        languages: List of language codes for OCR
        dpi: Resolution for rendering PDF pages to images
    
    Returns:
        Dictionary with page numbers as keys and extracted text as values
    """
    extracted_text = {}
    
    try:
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        
        # Check if GPU is available for EasyOCR
        use_gpu = False
        if ocr_engine == 'easyocr':
            use_gpu = check_gpu_available()
            if use_gpu:
                st.info("🚀 GPU detected! Using GPU acceleration for OCR.")
            else:
                st.info("💻 Using CPU for OCR processing.")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each page
        for page_num in range(total_pages):
            status_text.text(f"Processing page {page_num + 1} of {total_pages}...")
            
            page = pdf_document[page_num]
            
            # Render page to image
            zoom = dpi / 72  # Standard PDF DPI is 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Perform OCR based on selected engine
            if ocr_engine == 'tesseract':
                text = perform_ocr_tesseract(img)
            else:  # easyocr
                text = perform_ocr_easyocr(img, languages=languages, use_gpu=use_gpu)
            
            if text:
                extracted_text[page_num + 1] = text
            
            # Update progress
            progress_bar.progress((page_num + 1) / total_pages)
        
        pdf_document.close()
        progress_bar.empty()
        status_text.empty()
        
        return extracted_text
        
    except Exception as e:
        st.error(f"Error during OCR: {str(e)}")
        return None


def create_searchable_pdf(pdf_path, extracted_text, output_path):
    """
    Create a searchable PDF by adding OCR text as an invisible layer.
    
    Args:
        pdf_path: Path to the original PDF
        extracted_text: Dictionary with page numbers and extracted text
        output_path: Path for the output PDF
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Open original PDF
        pdf_document = fitz.open(pdf_path)
        
        # Add text layer to each page
        for page_num, text in extracted_text.items():
            if text.strip():  # Only add if there's text
                page = pdf_document[page_num - 1]
                
                # Add invisible text layer
                # This makes the PDF searchable while keeping the original appearance
                text_page = page.search_for(" ")  # Dummy search to enable text layer
                
                # Insert text at the top of the page (invisible)
                rect = page.rect
                page.insert_textbox(
                    rect,
                    text,
                    fontsize=1,  # Very small, nearly invisible
                    color=(1, 1, 1),  # White color
                    overlay=False
                )
        
        # Save the searchable PDF
        pdf_document.save(output_path)
        pdf_document.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating searchable PDF: {str(e)}")
        return False


def ocr_tool():
    """Main OCR tool interface."""
    st.title("🔍 PDF OCR")
    st.markdown("Extract text from scanned PDFs or images using OCR (Optical Character Recognition)")
    
    # Check OCR engine availability
    tesseract_available = check_tesseract_available()
    
    # Show installation status
    if not tesseract_available:
        st.warning("""
        ⚠️ **Tesseract OCR is not installed!**
        
        To use Tesseract OCR, please install it:
        - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
        - **macOS**: `brew install tesseract`
        - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
        
        You can still use **EasyOCR** which works without Tesseract.
        """)
    
    # OCR Engine Selection
    st.subheader("⚙️ OCR Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter available engines
        available_engines = []
        if tesseract_available:
            available_engines.append("tesseract")
        available_engines.append("easyocr")
        
        # Default to easyocr if tesseract is not available
        default_engine = "tesseract" if tesseract_available else "easyocr"
        
        ocr_engine = st.selectbox(
            "OCR Engine",
            available_engines,
            index=0 if default_engine in available_engines else 0,
            help="Tesseract (CPU-only, fast) or EasyOCR (CPU/GPU, more accurate)"
        )
        
        if ocr_engine == "tesseract" and not tesseract_available:
            st.error("❌ Tesseract is not installed. Please install it or use EasyOCR.")
    
    with col2:
        if ocr_engine == 'easyocr':
            # Language selection for EasyOCR
            language_options = {
                "English": "en",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
                "Italian": "it",
                "Portuguese": "pt",
                "Chinese (Simplified)": "ch_sim",
                "Chinese (Traditional)": "ch_tra",
                "Japanese": "ja",
                "Korean": "ko",
                "Arabic": "ar",
                "Russian": "ru"
            }
            selected_langs = st.multiselect(
                "Languages",
                options=list(language_options.keys()),
                default=["English"],
                help="Select languages to recognize"
            )
            languages = [language_options[lang] for lang in selected_langs]
        else:
            # Tesseract supports language specification but in a different way
            languages = ['eng']  # Default to English for Tesseract
    
    # DPI/Quality setting
    dpi = st.slider(
        "Image Quality (DPI)",
        min_value=150,
        max_value=600,
        value=300,
        step=50,
        help="Higher DPI = better quality but slower processing"
    )
    
    # Output format selection
    output_format = st.radio(
        "Output Format",
        ["Text File (.txt)", "Searchable PDF"],
        help="Text file: Extract text only. Searchable PDF: Add invisible text layer to original PDF."
    )
    
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload PDF file",
        type=['pdf'],
        help="Upload a scanned PDF or PDF with images"
    )
    
    if uploaded_file:
        # Display file info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Size", f"{get_file_size_mb(uploaded_file):.2f} MB")
        
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "temp/ocr")
        
        # Get page count
        try:
            pdf_doc = fitz.open(temp_path)
            page_count = len(pdf_doc)
            pdf_doc.close()
            
            with col2:
                st.metric("Pages", page_count)
            
            with col3:
                st.metric("OCR Engine", ocr_engine.upper())
        
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return
        
        # Preview
        st.subheader("📄 PDF Preview")
        show_pdf_preview_from_file(temp_path, max_pages=3)
        
        # Process button
        if st.button("🔍 Extract Text with OCR", type="primary", use_container_width=True):
            # Validate OCR engine is available
            if ocr_engine == "tesseract" and not tesseract_available:
                st.error("❌ Cannot use Tesseract OCR - it's not installed. Please install Tesseract or switch to EasyOCR.")
            else:
                with st.spinner(f"Performing OCR using {ocr_engine.upper()}..."):
                    
                    # Perform OCR
                    extracted_text = extract_text_with_ocr(
                        temp_path,
                        ocr_engine=ocr_engine,
                        languages=languages,
                        dpi=dpi
                    )
                    
                    if extracted_text:
                        st.success(f"✅ OCR completed! Extracted text from {len(extracted_text)} pages.")
                        
                        # Display extracted text preview
                        st.subheader("📝 Extracted Text Preview")
                        
                        # Show first page text as preview
                        if extracted_text:
                            first_page = list(extracted_text.keys())[0]
                            preview_text = extracted_text[first_page][:500]
                            if len(extracted_text[first_page]) > 500:
                                preview_text += "..."
                            
                            st.text_area(
                                f"Page {first_page} (preview)",
                                preview_text,
                                height=200,
                                disabled=True
                            )
                        
                        # Generate output
                        output_dir = "output/ocr"
                        os.makedirs(output_dir, exist_ok=True)
                        
                        if output_format == "Text File (.txt)":
                            # Create text file
                            output_filename = get_unique_filename(f"ocr_{uploaded_file.name.rsplit('.', 1)[0]}.txt")
                            output_path = os.path.join(output_dir, output_filename)
                            
                            with open(output_path, 'w', encoding='utf-8') as f:
                                for page_num in sorted(extracted_text.keys()):
                                    f.write(f"\n{'='*50}\n")
                                    f.write(f"PAGE {page_num}\n")
                                    f.write(f"{'='*50}\n\n")
                                    f.write(extracted_text[page_num])
                                    f.write("\n\n")
                            
                            # Provide download
                            with open(output_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Text File",
                                    data=f,
                                    file_name=output_filename,
                                    mime="text/plain",
                                    use_container_width=True
                                )
                        
                        else:  # Searchable PDF
                            # Create searchable PDF
                            output_filename = get_unique_filename(f"searchable_{uploaded_file.name}")
                            output_path = os.path.join(output_dir, output_filename)
                            
                            with st.spinner("Creating searchable PDF..."):
                                success = create_searchable_pdf(temp_path, extracted_text, output_path)
                            
                            if success:
                                st.success("✅ Searchable PDF created!")
                                
                                # Provide download
                                with open(output_path, 'rb') as f:
                                    st.download_button(
                                        label="📥 Download Searchable PDF",
                                        data=f,
                                        file_name=output_filename,
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                
                                # Preview searchable PDF
                                st.subheader("📄 Searchable PDF Preview")
                                show_pdf_preview_from_file(output_path, max_pages=3)
                    
                    else:
                        st.error("❌ OCR failed. Please check your file and try again.")
    
    # Information section
    st.markdown("---")
    st.markdown("""
    ### ℹ️ About OCR Engines
    
    **Tesseract OCR** (CPU-only):
    - Fast and lightweight
    - Good for simple documents
    - Lower resource usage
    - Best for English text
    
    **EasyOCR** (CPU/GPU):
    - More accurate for complex documents
    - Supports 80+ languages
    - Automatically uses GPU if available
    - Better for multi-language documents
    - Slower on CPU, much faster on GPU
    
    ### 💡 Tips for Best Results
    - Use higher DPI (300-600) for better accuracy
    - Ensure the scanned document has good contrast
    - Clean, well-lit scans produce better results
    - For mixed languages, use EasyOCR with multiple language selection
    """)


if __name__ == "__main__":
    ocr_tool()
