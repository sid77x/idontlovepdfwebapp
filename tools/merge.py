"""Merge multiple PDF files into one."""
import os
import streamlit as st
from PyPDF2 import PdfMerger
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count
from utils.preview import show_pdf_preview


def merge_pdfs(input_files: list, output_path: str) -> bool:
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        input_files: List of PDF file paths to merge
        output_path: Path where merged PDF will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        merger = PdfMerger()
        
        for pdf_file in input_files:
            merger.append(pdf_file)
        
        merger.write(output_path)
        merger.close()
        
        return True
    except Exception as e:
        st.error(f"Error merging PDFs: {str(e)}")
        return False


def render_merge_tool():
    """Render the Merge PDF tool interface."""
    st.title("📄 Merge PDF")
    st.write("Combine multiple PDF files into a single document.")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload PDF files to merge",
        type=['pdf'],
        accept_multiple_files=True,
        key="merge_uploader"
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) uploaded**")
        
        # Display uploaded files with reorder capability
        st.write("### Files to merge (in order):")
        
        for idx, file in enumerate(uploaded_files):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{idx + 1}. {file.name}")
            with col2:
                st.write(f"{file.size / 1024:.1f} KB")
        
        st.info("💡 Files will be merged in the order shown above.")
        
        # Merge button
        if st.button("🔗 Merge PDFs", type="primary", use_container_width=True):
            if len(uploaded_files) < 2:
                st.warning("⚠️ Please upload at least 2 PDF files to merge.")
            else:
                with st.spinner("Merging PDFs..."):
                    # Save uploaded files temporarily
                    temp_files = []
                    uploads_dir = "uploads"
                    
                    for uploaded_file in uploaded_files:
                        temp_path = save_uploaded_file(uploaded_file, uploads_dir)
                        temp_files.append(temp_path)
                    
                    # Merge PDFs
                    output_filename = "merged_output.pdf"
                    output_dir = "output"
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = get_unique_filename(output_filename, output_dir)
                    
                    success = merge_pdfs(temp_files, output_path)
                    
                    # Clean up temporary files
                    for temp_file in temp_files:
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                    
                    if success:
                        st.success("✅ PDFs merged successfully!")
                        
                        # Display output info
                        output_size = get_file_size_mb(output_path)
                        merged_page_count = get_pdf_page_count(output_path)
                        st.write(f"**Output:** {merged_page_count} pages, {output_size:.2f} MB")
                        
                        # Show preview
                        st.write("### 🔍 Preview")
                        try:
                            with open(output_path, "rb") as f:
                                preview_data = f.read()
                            
                            # Display PDF preview in browser
                            st.success(f"✅ Preview - All {merged_page_count} pages")
                            show_pdf_preview(preview_data, height=1000)
                        except Exception as e:
                            st.warning(f"Preview unavailable: {str(e)}")
                        
                        # Download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Merged PDF",
                                data=file,
                                file_name="merged_output.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        # Clean up output file after download
                        try:
                            os.remove(output_path)
                        except:
                            pass


if __name__ == "__main__":
    render_merge_tool()
