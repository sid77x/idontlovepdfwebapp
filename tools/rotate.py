"""Rotate pages in a PDF file."""
import os
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count, parse_page_range
from utils.preview import show_pdf_preview


def rotate_pdf(input_path: str, output_path: str, rotation: int, pages: list = None) -> bool:
    """
    Rotate pages in a PDF file.
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save rotated PDF
        rotation: Rotation angle (90, 180, 270)
        pages: List of page indices to rotate (0-indexed), None for all pages
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            
            # Rotate page if it's in the selection (or all pages if pages is None)
            if pages is None or page_num in pages:
                page.rotate(rotation)
            
            writer.add_page(page)
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        st.error(f"Error rotating PDF: {str(e)}")
        return False


def render_rotate_tool():
    """Render the Rotate PDF tool interface."""
    st.title("🔄 Rotate PDF")
    st.write("Rotate pages in your PDF document.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file to rotate",
        type=['pdf'],
        key="rotate_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        total_pages = get_pdf_page_count(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}** ({total_pages} pages)")
        
        # Rotation settings
        st.write("### Rotation Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rotation_angle = st.selectbox(
                "Rotation angle",
                [90, 180, 270],
                format_func=lambda x: f"{x}° {'(Clockwise)' if x != 180 else ''}",
                key="rotation_angle"
            )
        
        with col2:
            rotate_mode = st.radio(
                "Apply to:",
                ["All pages", "Specific pages"],
                key="rotate_mode"
            )
        
        selected_pages = None
        
        if rotate_mode == "Specific pages":
            st.write("Enter page numbers or ranges (e.g., '1-3, 5, 7-9'):")
            page_input = st.text_input(
                "Pages to rotate",
                placeholder="1-3, 5, 7-9",
                key="page_input"
            )
            
            if page_input:
                pages = parse_page_range(page_input, total_pages)
                
                if pages:
                    selected_pages = pages
                    st.success(f"✅ Selected {len(pages)} page(s) to rotate")
                else:
                    st.warning("⚠️ Invalid page range. Please check your input.")
        
        # Rotation preview
        st.write("### Preview")
        
        if rotate_mode == "All pages":
            st.info(f"🔄 All {total_pages} pages will be rotated {rotation_angle}°")
        elif selected_pages:
            page_list = ", ".join([str(p + 1) for p in selected_pages[:10]])
            if len(selected_pages) > 10:
                page_list += f"... (+{len(selected_pages) - 10} more)"
            st.info(f"🔄 Pages {page_list} will be rotated {rotation_angle}°")
        
        # Rotate button
        if st.button("🔄 Rotate PDF", type="primary", use_container_width=True):
            if rotate_mode == "Specific pages" and not selected_pages:
                st.warning("⚠️ Please enter valid page numbers or select 'All pages'.")
            else:
                with st.spinner("Rotating PDF..."):
                    output_filename = f"rotated_{uploaded_file.name}"
                    output_path = get_unique_filename(output_filename, "outputs")
                    
                    # Rotate PDF
                    pages_to_rotate = selected_pages if rotate_mode == "Specific pages" else None
                    success = rotate_pdf(temp_path, output_path, rotation_angle, pages_to_rotate)
                    
                    if success:
                        st.success("✅ PDF rotated successfully!")
                        
                        # Display output info
                        output_size = get_file_size_mb(output_path)
                        rotated_page_count = get_pdf_page_count(output_path)
                        st.write(f"**Output:** {rotated_page_count} pages, {output_size:.2f} MB")
                        
                        # Show preview
                        st.write("### 🔍 Preview")
                        try:
                            with open(output_path, "rb") as f:
                                preview_data = f.read()
                            
                            # Display PDF preview in browser
                            st.success(f"✅ Preview - {rotated_page_count} pages rotated")
                            show_pdf_preview(preview_data, height=1000)
                        except Exception as e:
                            st.warning(f"Preview unavailable: {str(e)}")
                        
                        # Download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Rotated PDF",
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
    render_rotate_tool()
