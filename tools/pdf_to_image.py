"""Convert PDF pages to images."""
import os
import sys
import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image
import fitz  # PyMuPDF for better PDF to image conversion
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb


def pdf_to_images(input_path: str, output_dir: str, dpi: int = 200, 
                  image_format: str = "PNG", pages: str = "all") -> list:
    """
    Convert PDF pages to images.
    
    Args:
        input_path: Input PDF path
        output_dir: Output directory for images
        dpi: Resolution (dots per inch)
        image_format: Output format (PNG, JPG, JPEG)
        pages: "all" or comma-separated page numbers (e.g., "1,3,5" or "1-5")
    
    Returns:
        list: Paths to created image files
    """
    try:
        # Open PDF with PyMuPDF (fitz)
        pdf_document = fitz.open(input_path)
        total_pages = len(pdf_document)
        
        # Parse page selection
        if pages == "all":
            page_list = list(range(total_pages))
        else:
            page_list = []
            for part in pages.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-')
                    page_list.extend(range(int(start) - 1, int(end)))
                else:
                    page_list.append(int(part) - 1)
            # Filter valid pages
            page_list = [p for p in page_list if 0 <= p < total_pages]
        
        if not page_list:
            st.error("No valid pages selected")
            return []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = []
        zoom = dpi / 72  # Convert DPI to zoom factor (72 is default DPI)
        matrix = fitz.Matrix(zoom, zoom)
        
        for page_num in page_list:
            page = pdf_document[page_num]
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save image
            output_filename = f"page_{page_num + 1}.{image_format.lower()}"
            output_path = os.path.join(output_dir, output_filename)
            
            if image_format.upper() == "JPG":
                image_format = "JPEG"
            
            img.save(output_path, format=image_format.upper())
            output_files.append(output_path)
        
        pdf_document.close()
        return output_files
        
    except Exception as e:
        st.error(f"Error converting PDF to images: {str(e)}")
        return []


def render_pdf_to_image_tool():
    """Render the PDF to Image tool interface."""
    st.title("📸 PDF to Image")
    st.write("Convert your PDF pages to image files (PNG, JPG)")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Select the PDF file you want to convert to images"
    )
    
    if uploaded_file:
        # Display file info
        file_size = get_file_size_mb(uploaded_file)
        st.info(f"📄 **{uploaded_file.name}** ({file_size:.2f} MB)")
        
        # Save uploaded file
        input_path = save_uploaded_file(uploaded_file, "pdf_to_image")
        
        if input_path:
            try:
                # Get page count
                reader = PdfReader(input_path)
                total_pages = len(reader.pages)
                
                st.success(f"✅ PDF loaded: {total_pages} pages")
                
                # Conversion settings
                st.write("### ⚙️ Conversion Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    image_format = st.selectbox(
                        "Output Format",
                        ["PNG", "JPG"],
                        help="PNG: Higher quality, larger file size. JPG: Smaller size, slight compression"
                    )
                    
                    dpi = st.slider(
                        "Resolution (DPI)",
                        min_value=72,
                        max_value=300,
                        value=200,
                        step=10,
                        help="Higher DPI = better quality but larger files. 200 DPI is recommended."
                    )
                
                with col2:
                    page_option = st.radio(
                        "Pages to Convert",
                        ["All pages", "Custom range"],
                        help="Choose which pages to convert"
                    )
                    
                    if page_option == "Custom range":
                        pages_input = st.text_input(
                            "Page Numbers",
                            value="1",
                            help="Examples: '1,3,5' or '1-5' or '1,3-5,7'"
                        )
                    else:
                        pages_input = "all"
                
                # Convert button
                if st.button("🔄 Convert to Images", type="primary", use_container_width=True):
                    with st.spinner("Converting PDF to images..."):
                        # Create output directory
                        output_dir = os.path.join("output", "pdf_to_image", get_unique_filename("images"))
                        
                        # Convert PDF to images
                        output_files = pdf_to_images(
                            input_path,
                            output_dir,
                            dpi,
                            image_format,
                            pages_input
                        )
                        
                        if output_files:
                            st.success(f"✅ Successfully converted {len(output_files)} pages to images!")
                            
                            # Show preview of first image
                            st.write("### 🖼️ Preview (First Image)")
                            try:
                                first_image = Image.open(output_files[0])
                                st.image(first_image, caption=os.path.basename(output_files[0]), use_container_width=True)
                            except Exception as e:
                                st.warning(f"Preview unavailable: {str(e)}")
                            
                            # Create ZIP file with all images
                            zip_path = os.path.join(output_dir, "images.zip")
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for img_file in output_files:
                                    zipf.write(img_file, os.path.basename(img_file))
                            
                            # Download buttons
                            st.write("### 📥 Download")
                            
                            if len(output_files) == 1:
                                # Single file download
                                with open(output_files[0], "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download Image",
                                        data=f,
                                        file_name=os.path.basename(output_files[0]),
                                        mime=f"image/{image_format.lower()}",
                                        use_container_width=True
                                    )
                            else:
                                # Multiple files - offer ZIP
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    with open(zip_path, "rb") as f:
                                        st.download_button(
                                            label=f"📦 Download All ({len(output_files)} images as ZIP)",
                                            data=f,
                                            file_name="converted_images.zip",
                                            mime="application/zip",
                                            use_container_width=True
                                        )
                                
                                with col2:
                                    # Show file list
                                    with st.expander(f"📋 View {len(output_files)} files"):
                                        for img_file in output_files:
                                            file_size = os.path.getsize(img_file) / (1024 * 1024)
                                            st.write(f"- {os.path.basename(img_file)} ({file_size:.2f} MB)")
                            
                            # Cleanup info
                            st.info("💡 **Tip:** Images are temporarily stored. Download them now!")
                        
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
    
    else:
        # Help section
        st.write("### 📖 How to use")
        st.markdown("""
        1. **Upload** your PDF file
        2. **Choose** output format (PNG or JPG)
        3. **Select** resolution (DPI)
        4. **Pick** which pages to convert
        5. **Click** Convert and download your images
        
        **Tips:**
        - **PNG**: Best for documents with text and graphics
        - **JPG**: Best for photo-heavy documents (smaller file size)
        - **200 DPI**: Good balance between quality and file size
        - **300 DPI**: High quality for printing
        """)


if __name__ == "__main__":
    render_pdf_to_image_tool()
