"""Split PDF into separate files."""
import os
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import sys
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename
from utils.pdf_ops import get_pdf_page_count, parse_page_range
from utils.preview import show_pdf_preview


def split_pdf_by_pages(input_path: str, output_dir: str, mode: str = "all", page_ranges: list = None) -> list:
    """
    Split PDF into separate files.
    
    Args:
        input_path: Path to input PDF
        output_dir: Directory to save split PDFs
        mode: "all" (one file per page), "ranges" (custom ranges), "chunks" (fixed size chunks)
        page_ranges: List of page ranges for custom split
    
    Returns:
        list: Paths to generated PDF files
    """
    try:
        reader = PdfReader(input_path)
        
        # Handle encrypted PDFs
        if reader.is_encrypted:
            try:
                reader.decrypt("")  # Try empty password
            except:
                st.error("⚠️ This PDF is password-protected. Please unlock it first using the Protect/Unlock tool.")
                return []
        
        total_pages = len(reader.pages)
        output_files = []
        
        if mode == "all":
            # Split every page into separate file
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_filename = f"page_{page_num + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        elif mode == "ranges" and page_ranges:
            # Split by custom page ranges
            for idx, pages in enumerate(page_ranges):
                writer = PdfWriter()
                
                for page_num in pages:
                    if 0 <= page_num < total_pages:
                        writer.add_page(reader.pages[page_num])
                
                output_filename = f"split_{idx + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        elif mode == "chunks":
            # Split into fixed-size chunks
            chunk_size = page_ranges if isinstance(page_ranges, int) else 1
            
            for chunk_idx in range(0, total_pages, chunk_size):
                writer = PdfWriter()
                
                for page_num in range(chunk_idx, min(chunk_idx + chunk_size, total_pages)):
                    writer.add_page(reader.pages[page_num])
                
                output_filename = f"chunk_{chunk_idx // chunk_size + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        return output_files
        
    except Exception as e:
        st.error(f"Error splitting PDF: {str(e)}")
        return []


def create_zip_file(files: list, zip_path: str) -> bool:
    """Create a zip file containing all split PDFs."""
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                zipf.write(file_path, os.path.basename(file_path))
        return True
    except Exception as e:
        st.error(f"Error creating zip file: {str(e)}")
        return False


def render_split_tool():
    """Render the Split PDF tool interface."""
    st.title("✂️ Split PDF")
    st.write("Split a PDF file into multiple documents.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file to split",
        type=['pdf'],
        key="split_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        total_pages = get_pdf_page_count(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}** ({total_pages} pages)")
        
        # Split mode selection
        st.write("### Split Options")
        
        split_mode = st.radio(
            "Choose split mode:",
            ["All pages separately", "Custom page ranges", "Fixed chunks"],
            key="split_mode"
        )
        
        page_ranges = None
        
        if split_mode == "All pages separately":
            st.info(f"📄 This will create {total_pages} separate PDF files (one per page).")
            mode = "all"
        
        elif split_mode == "Custom page ranges":
            st.write("Enter page ranges to split into separate files:")
            st.caption("Examples: '1-3' = pages 1-3 in one file | '1-3, 5-7' = two files | '1,2,3' = three files")
            range_input = st.text_input(
                "Page ranges (comma-separated)",
                placeholder="1-3, 5-7, 9",
                key="range_input"
            )
            
            if range_input:
                # Parse each range/page as a separate group
                page_ranges = []
                range_parts = [part.strip() for part in range_input.split(',')]
                
                for part in range_parts:
                    if '-' in part:
                        # It's a range like "1-3"
                        try:
                            start, end = part.split('-')
                            start = int(start.strip())
                            end = int(end.strip())
                            if 1 <= start <= total_pages and 1 <= end <= total_pages and start <= end:
                                # Add as a group (0-indexed)
                                page_ranges.append(list(range(start - 1, end)))
                            else:
                                st.warning(f"⚠️ Invalid range: {part}")
                        except:
                            st.warning(f"⚠️ Invalid range format: {part}")
                    else:
                        # It's a single page like "5"
                        try:
                            page_num = int(part.strip())
                            if 1 <= page_num <= total_pages:
                                # Add as a single-page group (0-indexed)
                                page_ranges.append([page_num - 1])
                            else:
                                st.warning(f"⚠️ Page {page_num} is out of range (1-{total_pages})")
                        except:
                            st.warning(f"⚠️ Invalid page number: {part}")
                
                if page_ranges:
                    total_selected = sum(len(group) for group in page_ranges)
                    st.success(f"✅ Will create {len(page_ranges)} PDF file(s) with {total_selected} total pages")
                    
                    # Show what will be created
                    with st.expander("📋 Preview output files"):
                        for idx, group in enumerate(page_ranges):
                            pages_str = ", ".join([str(p + 1) for p in group])
                            st.write(f"File {idx + 1}: Pages {pages_str}")
                else:
                    st.warning("⚠️ No valid page ranges entered.")
            
            mode = "ranges"
        
        else:  # Fixed chunks
            chunk_size = st.number_input(
                "Pages per file",
                min_value=1,
                max_value=total_pages,
                value=min(5, total_pages),
                key="chunk_size"
            )
            
            num_chunks = (total_pages + chunk_size - 1) // chunk_size
            st.info(f"📚 This will create {num_chunks} PDF file(s) with {chunk_size} pages each (last file may have fewer pages).")
            
            mode = "chunks"
            page_ranges = chunk_size
        
        # Split button
        if st.button("✂️ Split PDF", type="primary", use_container_width=True):
            if split_mode == "Custom page ranges" and not page_ranges:
                st.warning("⚠️ Please enter valid page ranges.")
            else:
                with st.spinner("Splitting PDF..."):
                    output_dir = "outputs/split"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Split PDF
                    output_files = split_pdf_by_pages(temp_path, output_dir, mode, page_ranges)
                    
                    if output_files:
                        st.success(f"✅ PDF split successfully into {len(output_files)} file(s)!")
                        
                        # Show file list
                        with st.expander(f"📋 Split Files ({len(output_files)} files)"):
                            for idx, file_path in enumerate(output_files):
                                file_size = os.path.getsize(file_path) / 1024  # KB
                                page_count = get_pdf_page_count(file_path)
                                st.write(f"{idx + 1}. {os.path.basename(file_path)} ({page_count} pages, {file_size:.1f} KB)")
                        
                        # Show preview of first split file
                        st.write("### 🔍 Preview (First Split File)")
                        try:
                            with open(output_files[0], "rb") as f:
                                preview_data = f.read()
                            
                            first_file_pages = get_pdf_page_count(output_files[0])
                            
                            # Display PDF preview in browser
                            st.success(f"✅ First split file - {first_file_pages} pages")
                            show_pdf_preview(preview_data, height=1000)
                        except Exception as e:
                            st.warning(f"Preview unavailable: {str(e)}")
                        
                        # Create zip file
                        zip_filename = f"split_{uploaded_file.name.replace('.pdf', '')}.zip"
                        zip_path = get_unique_filename(zip_filename, "outputs")
                        
                        if create_zip_file(output_files, zip_path):
                            # Read zip file into memory before cleanup
                            with open(zip_path, "rb") as file:
                                zip_data = file.read()
                            
                            # Download button with data from memory
                            st.download_button(
                                label=f"⬇️ Download All ({len(output_files)} files as ZIP)",
                                data=zip_data,
                                file_name=zip_filename,
                                mime="application/zip",
                                use_container_width=True
                            )
                            
                            # Clean up files
                            for file_path in output_files:
                                try:
                                    os.remove(file_path)
                                except:
                                    pass
                            
                            try:
                                os.remove(zip_path)
                            except:
                                pass


if __name__ == "__main__":
    render_split_tool()
