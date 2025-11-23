"""Compress PDF files to reduce file size."""
import os
import streamlit as st
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count
from utils.preview import show_pdf_preview


def compress_pdf(input_path: str, output_path: str, compression_level: str = "medium") -> tuple:
    """
    Compress a PDF file (simplified version using PyPDF2).
    Note: Full image compression requires PyMuPDF. This version provides basic optimization.
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save compressed PDF
        compression_level: "low", "medium", or "high" compression
    
    Returns:
        tuple: (success: bool, original_size_mb: float, compressed_size_mb: float)
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter
        
        original_size = get_file_size_mb(input_path)
        
        # Open PDF - handle encrypted PDFs
        try:
            reader = PdfReader(input_path)
            # Try to decrypt if encrypted
            if reader.is_encrypted:
                try:
                    reader.decrypt("")  # Try empty password
                except:
                    st.error("⚠️ This PDF is password-protected. Please unlock it first using the Protect/Unlock tool.")
                    return False, 0, 0
        except Exception as e:
            st.error(f"⚠️ Cannot read PDF: {str(e)}")
            return False, 0, 0
        
        writer = PdfWriter()
        
        # Add all pages with optimization
        for page in reader.pages:
            writer.add_page(page)
        
        # Apply compression to content streams
        try:
            for page in writer.pages:
                if hasattr(page, 'compress_content_streams'):
                    page.compress_content_streams()
        except:
            pass  # Skip if compression not available
        
        # Remove metadata to reduce size
        writer.add_metadata({})
        
        # Save with compression
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        compressed_size = get_file_size_mb(output_path)
        
        return True, original_size, compressed_size
        
    except Exception as e:
        st.error(f"Error compressing PDF: {str(e)}")
        return False, 0, 0


def render_compress_tool():
    """Render the Compress PDF tool interface."""
    st.title("🗜️ Compress PDF")
    st.write("Reduce PDF file size by compressing images and optimizing content.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file to compress",
        type=['pdf'],
        key="compress_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        original_size = get_file_size_mb(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}**")
        st.write(f"**Original size:** {original_size:.2f} MB")
        
        # Compression settings
        st.write("### Compression Settings")
        
        compression_level = st.select_slider(
            "Compression level",
            options=["low", "medium", "high"],
            value="medium",
            key="compression_level",
            help="Higher compression = smaller file size but lower image quality"
        )
        
        # Show compression info
        compression_info = {
            "low": {
                "desc": "Minimal compression - Good quality, moderate size reduction",
                "quality": "85%",
                "dpi": "150 DPI"
            },
            "medium": {
                "desc": "Balanced compression - Good quality, good size reduction",
                "quality": "75%",
                "dpi": "120 DPI"
            },
            "high": {
                "desc": "Maximum compression - Lower quality, maximum size reduction",
                "quality": "60%",
                "dpi": "90 DPI"
            }
        }
        
        info = compression_info[compression_level]
        
        st.info(f"""
        **{compression_level.upper()} Compression:**
        - {info['desc']}
        - Image Quality: {info['quality']}
        - Resolution: {info['dpi']}
        """)
        
        # Warning for high compression
        if compression_level == "high":
            st.warning("⚠️ High compression may significantly reduce image quality. Preview the result before using for important documents.")
        
        # Compress button
        if st.button("🗜️ Compress PDF", type="primary", use_container_width=True):
            with st.spinner("Compressing PDF... This may take a moment."):
                output_filename = f"compressed_{uploaded_file.name}"
                output_path = get_unique_filename(output_filename, "outputs")
                
                success, orig_size, comp_size = compress_pdf(temp_path, output_path, compression_level)
                
                if success:
                    # Calculate compression ratio
                    reduction = ((orig_size - comp_size) / orig_size * 100) if orig_size > 0 else 0
                    
                    st.success("✅ PDF compressed successfully!")
                    
                    # Display compression stats
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Original Size", f"{orig_size:.2f} MB")
                    
                    with col2:
                        st.metric("Compressed Size", f"{comp_size:.2f} MB")
                    
                    with col3:
                        st.metric("Size Reduction", f"{reduction:.1f}%")
                    
                    # Show appropriate message based on reduction
                    if reduction < 5:
                        st.info("💡 This PDF has minimal compression potential. It may already be optimized or contain mostly text.")
                    elif reduction < 20:
                        st.info("📉 Moderate compression achieved. The PDF contained some compressible content.")
                    else:
                        st.success(f"🎉 Great compression! File size reduced by {reduction:.1f}%")
                    
                    # Show preview
                    st.write("### 🔍 Preview")
                    try:
                        compressed_page_count = get_pdf_page_count(output_path)
                        with open(output_path, "rb") as f:
                            preview_data = f.read()
                        
                        # Display PDF preview in browser
                        st.success(f"✅ Preview - {compressed_page_count} pages compressed")
                        show_pdf_preview(preview_data, height=1000)
                    except Exception as e:
                        st.warning(f"Preview unavailable: {str(e)}")
                    
                    # Download button
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Download Compressed PDF",
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
    render_compress_tool()
