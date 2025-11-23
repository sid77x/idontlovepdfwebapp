"""Add watermark to PDF pages."""
import os
import sys
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count
from utils.preview import show_pdf_preview


def create_text_watermark(text: str, opacity: float = 0.3, rotation: int = 45, 
                          font_size: int = 50, color: tuple = (0.5, 0.5, 0.5),
                          position: str = "center", page_width: float = None, 
                          page_height: float = None) -> BytesIO:
    """
    Create a watermark PDF with text that adapts to page dimensions.
    
    Args:
        text: Watermark text
        opacity: Transparency (0-1)
        rotation: Rotation angle in degrees
        font_size: Font size
        color: RGB color tuple (0-1 range)
        position: "center", "top", "bottom", "diagonal"
        page_width: Width of the page (if None, uses letter size)
        page_height: Height of the page (if None, uses letter size)
    
    Returns:
        BytesIO: PDF bytes with watermark
    """
    packet = BytesIO()
    
    # Use provided dimensions or default to letter size
    if page_width and page_height:
        pagesize = (page_width, page_height)
    else:
        pagesize = letter
    
    can = canvas.Canvas(packet, pagesize=pagesize)
    width, height = pagesize
    
    # Set transparency
    can.setFillColor(Color(color[0], color[1], color[2], alpha=opacity))
    
    # Set font
    can.setFont("Helvetica-Bold", font_size)
    
    # Calculate position
    text_width = can.stringWidth(text, "Helvetica-Bold", font_size)
    
    if position == "center":
        x = width / 2
        y = height / 2
    elif position == "top":
        x = width / 2
        y = height - 100
        rotation = 0
    elif position == "bottom":
        x = width / 2
        y = 50
        rotation = 0
    else:  # diagonal
        x = width / 2
        y = height / 2
    
    # Rotate and draw text (centered at rotation point)
    can.saveState()
    can.translate(x, y)
    can.rotate(rotation)
    # Draw text centered at origin after translation
    can.drawCentredString(0, 0, text)
    can.restoreState()
    
    can.save()
    packet.seek(0)
    
    return packet


def add_watermark_to_pdf(input_path: str, output_path: str, watermark_text: str,
                         opacity: float = 0.3, rotation: int = 45, font_size: int = 50,
                         color: tuple = (0.5, 0.5, 0.5), position: str = "center",
                         pages: str = "all") -> bool:
    """
    Add text watermark to PDF pages.
    
    Args:
        input_path: Input PDF path
        output_path: Output PDF path
        watermark_text: Text to watermark
        opacity: Transparency (0-1)
        rotation: Rotation angle
        font_size: Font size
        color: RGB color tuple
        position: Position on page
        pages: "all" or "odd" or "even"
    
    Returns:
        bool: Success status
    """
    try:
        # Read input PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Add watermark to each page
        for page_num, page in enumerate(reader.pages):
            # Check if we should watermark this page
            should_watermark = (
                pages == "all" or
                (pages == "odd" and (page_num + 1) % 2 == 1) or
                (pages == "even" and (page_num + 1) % 2 == 0)
            )
            
            if should_watermark:
                # Get page dimensions to detect orientation
                mediabox = page.mediabox
                page_width = float(mediabox.width)
                page_height = float(mediabox.height)
                
                # Create watermark with page-specific dimensions
                watermark_pdf = create_text_watermark(
                    watermark_text, opacity, rotation, font_size, color, position,
                    page_width, page_height
                )
                watermark_reader = PdfReader(watermark_pdf)
                watermark_page = watermark_reader.pages[0]
                
                # Merge watermark with page
                page.merge_page(watermark_page)
            
            writer.add_page(page)
        
        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        st.error(f"Error adding watermark: {str(e)}")
        return False


def render_watermark_tool():
    """Render the Watermark PDF tool interface."""
    st.title("💧 Watermark PDF")
    st.write("Add text watermark to your PDF pages.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=['pdf'],
        key="watermark_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        total_pages = get_pdf_page_count(temp_path)
        original_size = get_file_size_mb(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}** ({total_pages} pages, {original_size:.2f} MB)")
        
        # Watermark settings
        st.write("### Watermark Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            watermark_text = st.text_input(
                "Watermark Text",
                value="CONFIDENTIAL",
                key="watermark_text",
                help="Text to display as watermark"
            )
            
            font_size = st.slider(
                "Font Size",
                min_value=20,
                max_value=100,
                value=50,
                key="font_size"
            )
            
            opacity = st.slider(
                "Opacity",
                min_value=0.1,
                max_value=1.0,
                value=0.3,
                step=0.1,
                key="opacity",
                help="0.1 = very transparent, 1.0 = solid"
            )
        
        with col2:
            position = st.selectbox(
                "Position",
                ["center", "top", "bottom", "diagonal"],
                key="position",
                help="Where to place the watermark"
            )
            
            rotation = st.slider(
                "Rotation (degrees)",
                min_value=0,
                max_value=360,
                value=45,
                key="rotation"
            )
            
            pages_option = st.radio(
                "Apply to:",
                ["all", "odd", "even"],
                key="pages_option",
                horizontal=True
            )
        
        # Color picker
        st.write("### Color")
        color_preset = st.selectbox(
            "Color Preset",
            ["Gray", "Red", "Blue", "Green", "Black"],
            key="color_preset"
        )
        
        color_map = {
            "Gray": (0.5, 0.5, 0.5),
            "Red": (1.0, 0.0, 0.0),
            "Blue": (0.0, 0.0, 1.0),
            "Green": (0.0, 0.8, 0.0),
            "Black": (0.0, 0.0, 0.0)
        }
        
        color = color_map[color_preset]
        
        # Preview section - Always show preview
        st.write("### � Preview (First Page)")
        
        if watermark_text:
            with st.spinner("Generating preview..."):
                try:
                    import tempfile
                    
                    # Create watermarked version of first page only
                    preview_path = tempfile.mktemp(suffix=".pdf")
                    reader = PdfReader(temp_path)
                    writer = PdfWriter()
                    
                    # Add watermark to all pages for preview
                    watermark_pdf = create_text_watermark(
                        watermark_text, opacity, rotation, font_size, color, position
                    )
                    watermark_reader = PdfReader(watermark_pdf)
                    watermark_page = watermark_reader.pages[0]
                    
                    # Apply to pages based on selection
                    for i, page in enumerate(reader.pages):
                        if pages_option == "all":
                            should_watermark = True
                        elif pages_option == "odd":
                            should_watermark = (i + 1) % 2 == 1
                        else:  # even
                            should_watermark = (i + 1) % 2 == 0
                        
                        if should_watermark:
                            page.merge_page(watermark_page)
                        writer.add_page(page)
                    
                    with open(preview_path, "wb") as f:
                        writer.write(f)
                    
                    # Show preview embedded in page
                    with open(preview_path, "rb") as f:
                        preview_data = f.read()
                    
                    # Display PDF preview in browser
                    st.success(f"✅ Preview - {len(reader.pages)} pages with watermark")
                    show_pdf_preview(preview_data, height=1000)
                    
                    try:
                        os.remove(preview_path)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"❌ Preview generation failed: {str(e)}")
        else:
            st.info("💡 Enter watermark text above to see preview")
        
        # Add watermark button
        if st.button("💧 Add Watermark to All Pages", type="primary", use_container_width=True):
            if not watermark_text:
                st.warning("⚠️ Please enter watermark text.")
            else:
                with st.spinner("Adding watermark..."):
                    output_filename = f"watermarked_{uploaded_file.name}"
                    output_path = get_unique_filename(output_filename, "outputs")
                    
                    success = add_watermark_to_pdf(
                        temp_path,
                        output_path,
                        watermark_text,
                        opacity,
                        rotation,
                        font_size,
                        color,
                        position,
                        pages_option
                    )
                    
                    if success:
                        st.success("✅ Watermark added successfully!")
                        
                        # Display output info
                        output_size = get_file_size_mb(output_path)
                        st.write(f"**Output file size:** {output_size:.2f} MB")
                        
                        # Download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Watermarked PDF",
                                data=file,
                                file_name=output_filename,
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        # Clean up
                        try:
                            os.remove(output_path)
                        except:
                            pass
        
        # Clean up uploaded file
        try:
            os.remove(temp_path)
        except:
            pass


if __name__ == "__main__":
    render_watermark_tool()
