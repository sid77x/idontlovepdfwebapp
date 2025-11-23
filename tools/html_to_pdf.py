"""Convert HTML to PDF."""
import os
import sys
import streamlit as st
from io import BytesIO

# Try to import WeasyPrint with graceful error handling
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.preview import show_pdf_preview


def html_to_pdf(input_path: str = None, html_string: str = None, output_path: str = None, 
                base_url: str = None) -> bool:
    """
    Convert HTML to PDF.
    
    Args:
        input_path: Input HTML file path (if converting from file)
        html_string: HTML string content (if converting from string)
        output_path: Output PDF path
        base_url: Base URL for resolving relative paths in HTML
    
    Returns:
        bool: Success status
    """
    if not WEASYPRINT_AVAILABLE:
        st.error("WeasyPrint is not available. Please install required dependencies.")
        return False
        
    try:
        if input_path:
            # Convert from file
            html = HTML(filename=input_path, base_url=base_url)
        elif html_string:
            # Convert from string
            html = HTML(string=html_string, base_url=base_url)
        else:
            st.error("No HTML input provided")
            return False
        
        # Generate PDF
        html.write_pdf(output_path)
        
        return True
        
    except Exception as e:
        st.error(f"Error converting HTML to PDF: {str(e)}")
        return False


def render_html_to_pdf_tool():
    """Render the HTML to PDF tool interface."""
    st.title("🌐 HTML to PDF")
    st.write("Convert HTML files or code to PDF format")
    
    # Check if WeasyPrint is available
    if not WEASYPRINT_AVAILABLE:
        st.error("🚫 WeasyPrint is not available")
        
        with st.expander("❗ Installation Required"):
            st.markdown(f"""
            **Error:** {WEASYPRINT_ERROR}
            
            **WeasyPrint requires additional system libraries on Windows:**
            
            ```bash
            # Install via conda (recommended for Windows)
            conda install -c conda-forge weasyprint gtk3 pango cairo glib
            
            # Or via pip + manual GTK installation
            pip install weasyprint
            # Then install GTK3 runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
            ```
            
            **Alternative Solutions:**
            1. Use the **PDF to HTML** tool for reverse conversion
            2. Use online HTML to PDF converters temporarily
            3. Install GTK3 runtime and restart the application
            
            **For detailed instructions, visit:**
            - [WeasyPrint Installation Guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)
            - [Windows Troubleshooting](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting)
            """)
        
        return
    
    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["Upload HTML File", "Paste HTML Code"],
        horizontal=True
    )
    
    html_content = None
    input_path = None
    
    if input_method == "Upload HTML File":
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an HTML file",
            type=['html', 'htm'],
            help="Select the HTML file you want to convert to PDF"
        )
        
        if uploaded_file:
            # Display file info
            file_size = get_file_size_mb(uploaded_file)
            st.info(f"🌐 **{uploaded_file.name}** ({file_size:.2f} MB)")
            
            # Save uploaded file
            input_path = save_uploaded_file(uploaded_file, "html_to_pdf")
            
            # Read content for preview
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            with st.expander("👁️ View HTML source"):
                st.code(html_content[:1000] + ("..." if len(html_content) > 1000 else ""), language="html")
    
    else:  # Paste HTML Code
        html_content = st.text_area(
            "Paste your HTML code",
            height=300,
            placeholder="""<!DOCTYPE html>
<html>
<head>
    <title>My Document</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a sample HTML document.</p>
</body>
</html>""",
            help="Enter or paste your HTML code here"
        )
    
    if html_content or input_path:
        # Conversion settings
        st.write("### ⚙️ Conversion Settings")
        
        base_url = st.text_input(
            "Base URL (optional)",
            placeholder="https://example.com/",
            help="Base URL for resolving relative paths (images, CSS, etc.)"
        )
        
        if not base_url:
            base_url = None
        
        # Convert button
        if st.button("🔄 Convert to PDF", type="primary", use_container_width=True):
            with st.spinner("Converting HTML to PDF..."):
                # Create output path
                output_dir = os.path.join("output", "html_to_pdf")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, get_unique_filename("converted.pdf"))
                
                # Convert HTML to PDF
                if input_method == "Upload HTML File":
                    success = html_to_pdf(input_path=input_path, output_path=output_path, base_url=base_url)
                else:
                    success = html_to_pdf(html_string=html_content, output_path=output_path, base_url=base_url)
                
                if success:
                    st.success(f"✅ Successfully converted HTML to PDF!")
                    
                    # Show preview
                    st.write("### 🔍 Preview")
                    try:
                        with open(output_path, "rb") as f:
                            preview_data = f.read()
                        
                        show_pdf_preview(preview_data, height=1000)
                    except Exception as e:
                        st.warning(f"Preview unavailable: {str(e)}")
                    
                    # Show file info
                    output_size = os.path.getsize(output_path) / (1024 * 1024)
                    st.info(f"📄 Output PDF size: {output_size:.2f} MB")
                    
                    # Download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=f,
                            file_name="converted.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
    
    else:
        # Help section
        st.write("### 📖 How to use")
        st.markdown("""
        1. **Choose** input method (Upload file or Paste code)
        2. **Provide** your HTML content
        3. **Optionally** set a base URL for relative paths
        4. **Click** Convert to PDF
        5. **Download** your PDF file
        
        **Features:**
        - ✅ Full CSS support
        - ✅ Embedded images (if accessible)
        - ✅ Custom fonts (if properly linked)
        - ✅ Responsive layouts
        
        **Tips:**
        - Use absolute URLs for external resources
        - Provide a base URL if your HTML uses relative paths
        - Inline CSS works best for simple documents
        - External stylesheets must be accessible
        
        **Best for:**
        - Web pages and articles
        - Reports with HTML formatting
        - Documentation with code samples
        - Styled content from CMS
        """)


if __name__ == "__main__":
    render_html_to_pdf_tool()
