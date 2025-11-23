"""Repair corrupted PDF files."""
import os
import sys
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count


def repair_pdf(input_path: str, output_path: str) -> tuple[bool, str]:
    """
    Attempt to repair a PDF file by re-saving it with PyPDF2.
    
    Args:
        input_path: Input PDF path
        output_path: Output PDF path
    
    Returns:
        tuple: (success status, message)
    """
    try:
        # Try to read the PDF with strict mode off
        reader = PdfReader(input_path, strict=False)
        
        # Check if file can be read
        page_count = len(reader.pages)
        if page_count == 0:
            return False, "PDF has no pages"
        
        # Try to access metadata (common source of corruption)
        try:
            metadata = reader.metadata
        except:
            metadata = None
        
        # Create writer and copy all pages
        writer = PdfWriter()
        repaired_pages = 0
        failed_pages = []
        
        for i in range(page_count):
            try:
                page = reader.pages[i]
                # Try to access page content (tests for corruption)
                _ = page.extract_text()
                writer.add_page(page)
                repaired_pages += 1
            except Exception as e:
                failed_pages.append(i + 1)
                continue
        
        if repaired_pages == 0:
            return False, "Could not repair any pages"
        
        # Add metadata if available
        if metadata:
            try:
                for key, value in metadata.items():
                    writer.add_metadata({key: value})
            except:
                pass
        
        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        # Build result message
        if failed_pages:
            msg = f"Partially repaired: {repaired_pages}/{page_count} pages recovered. Failed pages: {', '.join(map(str, failed_pages))}"
        else:
            msg = f"Successfully repaired all {repaired_pages} pages"
        
        return True, msg
        
    except Exception as e:
        return False, f"Repair failed: {str(e)}"


def render_repair_tool():
    """Render the Repair PDF tool interface."""
    st.title("🔧 Repair PDF")
    st.write("Fix corrupted or damaged PDF files by re-saving them.")
    
    # Information box
    with st.expander("ℹ️ How does PDF repair work?"):
        st.markdown("""
        This tool attempts to repair PDFs by:
        
        - **Reading with error recovery** - Uses non-strict mode to skip errors
        - **Extracting readable pages** - Copies all accessible pages to new file
        - **Rebuilding structure** - Creates clean PDF structure
        - **Preserving metadata** - Keeps document information when possible
        
        **What it can fix:**
        - Minor corruption in PDF structure
        - Invalid cross-reference tables
        - Broken object streams
        - Damaged metadata
        
        **Limitations:**
        - Cannot recover severely damaged content
        - May lose some formatting or features
        - Cannot decrypt encrypted/protected PDFs
        """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file to repair",
        type=['pdf'],
        key="repair_uploader",
        help="Upload a corrupted or damaged PDF file"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        original_size = get_file_size_mb(temp_path)
        
        st.info(f"📄 Uploaded: **{uploaded_file.name}** ({original_size:.2f} MB)")
        
        # Try to diagnose the PDF
        st.write("### Diagnostic Report")
        
        diagnosis = []
        can_read = False
        page_count = 0
        
        try:
            # Try strict mode first
            try:
                reader = PdfReader(temp_path, strict=True)
                diagnosis.append("✅ PDF structure is valid (strict mode passed)")
                can_read = True
            except:
                diagnosis.append("⚠️ PDF has structural issues (strict mode failed)")
                # Try non-strict mode
                try:
                    reader = PdfReader(temp_path, strict=False)
                    diagnosis.append("✅ PDF can be read in recovery mode")
                    can_read = True
                except:
                    diagnosis.append("❌ PDF cannot be read even in recovery mode")
            
            if can_read:
                # Check page count
                page_count = len(reader.pages)
                diagnosis.append(f"📄 Page count: {page_count}")
                
                # Check metadata
                try:
                    metadata = reader.metadata
                    if metadata:
                        diagnosis.append(f"✅ Metadata is accessible ({len(metadata)} fields)")
                    else:
                        diagnosis.append("⚠️ No metadata found")
                except:
                    diagnosis.append("❌ Metadata is corrupted")
                
                # Check if encrypted
                if reader.is_encrypted:
                    diagnosis.append("🔒 PDF is encrypted (cannot repair)")
                else:
                    diagnosis.append("✅ PDF is not encrypted")
                
                # Test random pages
                test_pages = min(5, page_count)
                accessible_pages = 0
                for i in range(test_pages):
                    try:
                        page = reader.pages[i]
                        _ = page.extract_text()
                        accessible_pages += 1
                    except:
                        pass
                
                diagnosis.append(f"📊 Accessible pages: {accessible_pages}/{test_pages} tested")
        
        except Exception as e:
            diagnosis.append(f"❌ Critical error: {str(e)}")
        
        # Display diagnosis
        for item in diagnosis:
            if "✅" in item:
                st.success(item)
            elif "⚠️" in item:
                st.warning(item)
            elif "❌" in item:
                st.error(item)
            else:
                st.info(item)
        
        # Repair button
        st.write("### Repair PDF")
        
        if not can_read:
            st.error("❌ This PDF is too damaged to repair with available tools.")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write("The repair process will:")
                st.markdown("""
                - Extract all readable pages
                - Rebuild PDF structure
                - Create a clean output file
                """)
            
            with col2:
                st.metric("Pages", page_count)
            
            if st.button("🔧 Repair PDF", type="primary", use_container_width=True):
                with st.spinner("Repairing PDF..."):
                    output_filename = f"repaired_{uploaded_file.name}"
                    output_path = get_unique_filename(output_filename, "outputs")
                    
                    success, message = repair_pdf(temp_path, output_path)
                    
                    if success:
                        st.success(f"✅ {message}")
                        
                        # Display output info
                        output_size = get_file_size_mb(output_path)
                        repaired_pages = get_pdf_page_count(output_path)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Original Size", f"{original_size:.2f} MB")
                        with col2:
                            st.metric("Repaired Size", f"{output_size:.2f} MB")
                        
                        st.info(f"📄 Repaired PDF has {repaired_pages} pages")
                        
                        # Download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Repaired PDF",
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
                    else:
                        st.error(f"❌ {message}")
        
        # Clean up uploaded file
        try:
            os.remove(temp_path)
        except:
            pass


if __name__ == "__main__":
    render_repair_tool()
