"""Convert images to PDF."""
import os
import sys
import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfWriter, PdfReader
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.preview import show_pdf_preview


def image_to_pdf(image_paths: list, output_path: str, page_size: str = "auto",
                 fit_to_page: bool = True, maintain_aspect: bool = True) -> bool:
    """
    Convert images to a single PDF file.
    
    Args:
        image_paths: List of image file paths
        output_path: Output PDF path
        page_size: "auto", "letter", or "a4"
        fit_to_page: Scale images to fit page
        maintain_aspect: Maintain aspect ratio when scaling
    
    Returns:
        bool: Success status
    """
    try:
        pdf_writer = PdfWriter()
        
        for img_path in image_paths:
            # Open image
            img = Image.open(img_path)
            
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Determine page size
            img_width, img_height = img.size
            
            if page_size == "auto":
                # Use image dimensions
                page_width, page_height = img_width, img_height
            elif page_size == "letter":
                page_width, page_height = letter
            else:  # A4
                page_width, page_height = A4
            
            # Create a new PDF page
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            if fit_to_page and page_size != "auto":
                # Calculate scaling
                if maintain_aspect:
                    # Calculate aspect ratios
                    img_aspect = img_width / img_height
                    page_aspect = page_width / page_height
                    
                    if img_aspect > page_aspect:
                        # Image is wider - fit to width
                        draw_width = page_width
                        draw_height = page_width / img_aspect
                    else:
                        # Image is taller - fit to height
                        draw_height = page_height
                        draw_width = page_height * img_aspect
                    
                    # Center the image
                    x = (page_width - draw_width) / 2
                    y = (page_height - draw_height) / 2
                else:
                    # Stretch to fill page
                    draw_width = page_width
                    draw_height = page_height
                    x, y = 0, 0
            else:
                # No scaling
                draw_width = img_width
                draw_height = img_height
                x, y = 0, 0
            
            # Draw image on canvas
            c.drawImage(ImageReader(img), x, y, width=draw_width, height=draw_height)
            c.save()
            
            # Add page to PDF
            packet.seek(0)
            page_reader = PdfReader(packet)
            pdf_writer.add_page(page_reader.pages[0])
        
        # Write final PDF
        with open(output_path, 'wb') as f:
            pdf_writer.write(f)
        
        return True
        
    except Exception as e:
        st.error(f"Error converting images to PDF: {str(e)}")
        return False


def render_image_to_pdf_tool():
    """Render the Image to PDF tool interface."""
    st.title("🖼️ Image to PDF")
    st.write("Convert your images to a single PDF file")
    
    # File upload (multiple)
    uploaded_files = st.file_uploader(
        "Choose image files",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'],
        accept_multiple_files=True,
        help="Select one or more images to convert to PDF"
    )
    
    if uploaded_files:
        # Display file info
        st.info(f"📸 **{len(uploaded_files)} image(s)** uploaded")
        
        # Show thumbnails
        with st.expander("🖼️ View uploaded images", expanded=True):
            cols = st.columns(min(len(uploaded_files), 4))
            for idx, uploaded_file in enumerate(uploaded_files):
                with cols[idx % 4]:
                    img = Image.open(uploaded_file)
                    st.image(img, caption=uploaded_file.name, use_container_width=True)
                    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
                    st.caption(f"{img.width}×{img.height} - {file_size:.2f} MB")
        
        # Save uploaded files
        image_paths = []
        temp_dir = os.path.join("temp", "image_to_pdf", get_unique_filename("imgs"))
        os.makedirs(temp_dir, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(temp_path)
        
        # Reorder images
        st.write("### 📝 Image Order")
        st.info("💡 Images will be added to PDF in the order shown above. Re-upload to change order.")
        
        # Conversion settings
        st.write("### ⚙️ Conversion Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_size = st.selectbox(
                "Page Size",
                ["auto", "letter", "a4"],
                help="auto: Use image dimensions, letter: US Letter, a4: A4 size"
            )
            
            fit_to_page = st.checkbox(
                "Fit images to page",
                value=True,
                help="Scale images to fit within the page size",
                disabled=(page_size == "auto")
            )
        
        with col2:
            maintain_aspect = st.checkbox(
                "Maintain aspect ratio",
                value=True,
                help="Keep original image proportions when scaling",
                disabled=(not fit_to_page or page_size == "auto")
            )
        
        # Convert button
        if st.button("🔄 Convert to PDF", type="primary", use_container_width=True):
            with st.spinner("Converting images to PDF..."):
                # Create output path
                output_dir = os.path.join("output", "image_to_pdf")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, get_unique_filename("converted.pdf"))
                
                # Convert images to PDF
                success = image_to_pdf(
                    image_paths,
                    output_path,
                    page_size,
                    fit_to_page,
                    maintain_aspect
                )
                
                if success:
                    st.success(f"✅ Successfully created PDF with {len(uploaded_files)} images!")
                    
                    # Show preview
                    st.write("### 🔍 Preview")
                    try:
                        with open(output_path, "rb") as f:
                            preview_data = f.read()
                        
                        show_pdf_preview(preview_data, height=1000)
                    except Exception as e:
                        st.warning(f"Preview unavailable: {str(e)}")
                    
                    # Download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=f,
                            file_name="converted_images.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    # Show file size
                    output_size = os.path.getsize(output_path) / (1024 * 1024)
                    st.info(f"📄 Output PDF size: {output_size:.2f} MB")
    
    else:
        # Help section
        st.write("### 📖 How to use")
        st.markdown("""
        1. **Upload** one or more image files
        2. **Check** the preview to ensure correct order
        3. **Choose** page size and scaling options
        4. **Click** Convert to create your PDF
        5. **Download** your PDF file
        
        **Supported formats:**
        - PNG, JPG, JPEG, BMP, TIFF, WebP
        
        **Tips:**
        - **Auto page size**: Each image becomes its own size page
        - **Letter/A4**: All images scaled to standard page size
        - **Maintain aspect ratio**: Prevents image distortion
        - Upload images in the order you want them in the PDF
        """)


if __name__ == "__main__":
    render_image_to_pdf_tool()
