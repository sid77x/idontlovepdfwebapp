"""
PDF Preview Utilities
Provides reusable preview functions for displaying PDFs in the browser
"""

import streamlit as st
import base64
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO


def show_pdf_preview(pdf_data: bytes, height: int = 1000, title: str = None, max_pages: int = 5):
    """
    Display a PDF preview in the browser without requiring download.
    Shows only the first few pages to keep preview lightweight.
    
    Args:
        pdf_data: The PDF file content as bytes
        height: Height of the iframe in pixels (default: 1000)
        title: Optional title to display above the preview
        max_pages: Maximum number of pages to show in preview (default: 5)
    """
    if title:
        st.subheader(title)
    
    try:
        # Read the PDF to get page count
        pdf_reader = PdfReader(BytesIO(pdf_data))
        total_pages = len(pdf_reader.pages)
        
        # If PDF has more than max_pages, create a preview with only first max_pages
        if total_pages > max_pages:
            pdf_writer = PdfWriter()
            for i in range(max_pages):
                pdf_writer.add_page(pdf_reader.pages[i])
            
            # Write preview PDF to bytes
            preview_buffer = BytesIO()
            pdf_writer.write(preview_buffer)
            preview_data = preview_buffer.getvalue()
            
            st.info(f"📄 Showing first {max_pages} pages of {total_pages} total pages")
        else:
            preview_data = pdf_data
            st.info(f"📄 Showing all {total_pages} pages")
        
        # Encode PDF to base64
        base64_pdf = base64.b64encode(preview_data).decode("utf-8")
        
        # Create iframe with embedded PDF
        pdf_display = f'''
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" 
                height="{height}px"
                style="border: 2px solid #e0e0e0; border-radius: 8px;"
                type="application/pdf">
            </iframe>
        '''
        
        # Display using unsafe_allow_html to bypass Streamlit's security restrictions
        st.markdown(pdf_display, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error creating preview: {str(e)}")


def show_pdf_preview_from_file(file_path: str, height: int = 1000, title: str = None, max_pages: int = 5):
    """
    Display a PDF preview from a file path.
    Shows only the first few pages to keep preview lightweight.
    
    Args:
        file_path: Path to the PDF file
        height: Height of the iframe in pixels (default: 1000)
        title: Optional title to display above the preview
        max_pages: Maximum number of pages to show in preview (default: 5)
    """
    try:
        with open(file_path, "rb") as f:
            pdf_data = f.read()
        show_pdf_preview(pdf_data, height, title, max_pages)
    except Exception as e:
        st.error(f"❌ Error loading preview: {str(e)}")
