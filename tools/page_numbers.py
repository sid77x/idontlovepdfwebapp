"""Add page numbers to PDF pages."""
import os
import sys
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count
from utils.preview import show_pdf_preview


def create_page_number_overlay(page_num: int, total_pages: int, position: str = "bottom-center",
                               font_size: int = 12, format_style: str = "number",
                               start_from: int = 1, page_width: float = None,
                               page_height: float = None) -> BytesIO:
    """
    Create a PDF overlay with page number that adapts to page dimensions.
    
    Args:
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages
        position: Where to place the number
        font_size: Font size
        format_style: "number", "page_x", "page_x_of_y"
        start_from: Starting page number
        page_width: Width of the page (if None, uses letter size)
        page_height: Height of the page (if None, uses letter size)
    
    Returns:
        BytesIO: PDF bytes with page number
    """
    packet = BytesIO()
    
    # Use provided dimensions or default to letter size
    if page_width and page_height:
        pagesize = (page_width, page_height)
    else:
        pagesize = letter
    
    can = canvas.Canvas(packet, pagesize=pagesize)
    width, height = pagesize
    
    # Calculate actual page number
    actual_page = page_num - 1 + start_from
    
    # Format the page number text
    if format_style == "number":
        text = str(actual_page)
    elif format_style == "page_x":
        text = f"Page {actual_page}"
    else:  # page_x_of_y
        actual_total = total_pages - 1 + start_from
        text = f"Page {actual_page} of {actual_total}"
    
    # Set font
    can.setFont("Helvetica", font_size)
    
    # Calculate position with better margins
    text_width = can.stringWidth(text, "Helvetica", font_size)
    margin_horizontal = 50  # Increased from 30
    margin_vertical_bottom = 35    # Bottom margin
    margin_vertical_top = 50       # Top margin - slightly more space from top edge
    
    positions = {
        "bottom-left": (margin_horizontal, margin_vertical_bottom),
        "bottom-center": ((width - text_width) / 2, margin_vertical_bottom),
        "bottom-right": (width - text_width - margin_horizontal, margin_vertical_bottom),
        "top-left": (margin_horizontal, height - margin_vertical_top),
        "top-center": ((width - text_width) / 2, height - margin_vertical_top),
        "top-right": (width - text_width - margin_horizontal, height - margin_vertical_top),
    }
    
    x, y = positions.get(position, positions["bottom-center"])
    
    # Draw text
    can.drawString(x, y, text)
    can.save()
    packet.seek(0)
    
    return packet


def add_page_numbers_to_pdf(input_path: str, output_path: str, position: str = "bottom-center",
                            font_size: int = 12, format_style: str = "number",
                            start_from: int = 1, skip_first: bool = False) -> bool:
    """
    Add page numbers to PDF.
    
    Args:
        input_path: Input PDF path
        output_path: Output PDF path
        position: Position on page
        font_size: Font size
        format_style: Number format
        start_from: Starting number
        skip_first: Skip first page (for cover pages)
    
    Returns:
        bool: Success status
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        
        for page_num, page in enumerate(reader.pages, start=1):
            # Skip first page if requested
            if skip_first and page_num == 1:
                writer.add_page(page)
                continue
            
            # Get page dimensions to detect orientation
            mediabox = page.mediabox
            page_width = float(mediabox.width)
            page_height = float(mediabox.height)
            
            # Create page number overlay with page-specific dimensions
            page_number_pdf = create_page_number_overlay(
                page_num,
                total_pages,
                position,
                font_size,
                format_style,
                start_from,
                page_width,
                page_height
            )
            
            page_number_reader = PdfReader(page_number_pdf)
            page_number_page = page_number_reader.pages[0]
            
            # Merge page number with page
            page.merge_page(page_number_page)
            writer.add_page(page)
        
        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        st.error(f"Error adding page numbers: {str(e)}")
        return False


def render_page_numbers_tool():
    """Render the Page Numbers tool interface."""
    st.title("🔢 Add Page Numbers")
    st.write("Add page numbers to your PDF pages.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=['pdf'],
        key="page_numbers_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        total_pages = get_pdf_page_count(temp_path)
        original_size = get_file_size_mb(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}** ({total_pages} pages, {original_size:.2f} MB)")
        
        # Page number settings
        st.write("### Page Number Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            format_style = st.selectbox(
                "Format",
                ["number", "page_x", "page_x_of_y"],
                format_func=lambda x: {
                    "number": "1, 2, 3...",
                    "page_x": "Page 1, Page 2...",
                    "page_x_of_y": "Page 1 of 10..."
                }[x],
                key="format_style"
            )
            
            position = st.selectbox(
                "Position",
                ["bottom-center", "bottom-left", "bottom-right", 
                 "top-center", "top-left", "top-right"],
                key="position",
                format_func=lambda x: x.replace("-", " ").title()
            )
            
            font_size = st.slider(
                "Font Size",
                min_value=8,
                max_value=24,
                value=12,
                key="font_size"
            )
        
        with col2:
            start_from = st.number_input(
                "Start numbering from",
                min_value=1,
                max_value=1000,
                value=1,
                key="start_from",
                help="First page will be numbered with this value"
            )
            
            skip_first = st.checkbox(
                "Skip first page",
                value=False,
                key="skip_first",
                help="Don't add page number to the first page (useful for cover pages)"
            )
        
        # Preview section - Always show preview
        st.write("### 🔍 Preview (First 2 Pages)")
        
        if format_style == "number":
            preview_text = f"{start_from}, {start_from + 1}, {start_from + 2}..."
        elif format_style == "page_x":
            preview_text = f"Page {start_from}, Page {start_from + 1}..."
        else:
            preview_text = f"Page {start_from} of {total_pages}, Page {start_from + 1} of {total_pages}..."
        
        st.info(f"💡 Format: {preview_text}")
        
        if skip_first:
            st.warning(f"⚠️ First page will not have a page number")
        
        # Generate preview automatically
        with st.spinner("Generating preview..."):
            try:
                import tempfile
                
                # Create numbered version of ALL pages
                preview_path = tempfile.mktemp(suffix=".pdf")
                reader = PdfReader(temp_path)
                writer = PdfWriter()
                
                # Add all pages with numbers
                for i in range(total_pages):
                    page = reader.pages[i]
                    
                    # Skip first page if requested
                    if i == 0 and skip_first:
                        writer.add_page(page)
                        continue
                    
                    # Create page number overlay
                    page_num_pdf = create_page_number_overlay(
                        i + 1, total_pages, position, font_size, format_style, start_from
                    )
                    page_num_reader = PdfReader(page_num_pdf)
                    page_num_page = page_num_reader.pages[0]
                    
                    page.merge_page(page_num_page)
                    writer.add_page(page)
                
                with open(preview_path, "wb") as f:
                    writer.write(f)
                
                # Show preview embedded in page
                with open(preview_path, "rb") as f:
                    preview_data = f.read()
                
                # Display PDF preview in browser
                st.success(f"✅ Preview - {total_pages} pages with page numbers")
                show_pdf_preview(preview_data, height=1000)
                
                try:
                    os.remove(preview_path)
                except:
                    pass
                    
            except Exception as e:
                st.error(f"❌ Preview generation failed: {str(e)}")
        
        # Add page numbers button
        if st.button("🔢 Add Page Numbers to All Pages", type="primary", use_container_width=True):
            with st.spinner("Adding page numbers..."):
                output_filename = f"numbered_{uploaded_file.name}"
                output_path = get_unique_filename(output_filename, "outputs")
                
                success = add_page_numbers_to_pdf(
                    temp_path,
                    output_path,
                    position,
                    font_size,
                    format_style,
                    start_from,
                    skip_first
                )
                
                if success:
                    st.success("✅ Page numbers added successfully!")
                    
                    # Display output info
                    output_size = get_file_size_mb(output_path)
                    st.write(f"**Output file size:** {output_size:.2f} MB")
                    
                    # Download button
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Download PDF with Page Numbers",
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
    render_page_numbers_tool()
