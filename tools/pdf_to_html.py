"""Convert PDF to HTML."""
import os
import sys
import streamlit as st
import fitz  # PyMuPDF

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb


def pdf_to_html(input_path: str, output_path: str, include_images: bool = True) -> bool:
    """
    Convert PDF to HTML.
    
    Args:
        input_path: Input PDF path
        output_path: Output HTML path
        include_images: Whether to extract and embed images
    
    Returns:
        bool: Success status
    """
    try:
        # Open PDF
        pdf_document = fitz.open(input_path)
        
        # Start HTML
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PDF to HTML Conversion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .page {
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            background: #fff;
        }
        .page-number {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        img {
            max-width: 100%;
            height: auto;
            margin: 10px 0;
        }
        p {
            margin: 10px 0;
        }
    </style>
</head>
<body>
"""
        
        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            html_content += f'<div class="page">\n'
            html_content += f'<div class="page-number">Page {page_num + 1}</div>\n'
            
            # Extract text
            text = page.get_text("html")
            
            # Add text content
            if text.strip():
                html_content += text
            
            # Extract and embed images if requested
            if include_images:
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Convert to base64 for embedding
                        import base64
                        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        html_content += f'<img src="data:image/{image_ext};base64,{img_base64}" alt="Image {img_index + 1}" />\n'
                    except Exception as e:
                        # Skip problematic images
                        continue
            
            html_content += '</div>\n'
        
        # Close HTML
        html_content += """
</body>
</html>
"""
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        pdf_document.close()
        return True
        
    except Exception as e:
        st.error(f"Error converting PDF to HTML: {str(e)}")
        return False


def render_pdf_to_html_tool():
    """Render the PDF to HTML tool interface."""
    st.title("🌐 PDF to HTML")
    st.write("Convert your PDF to HTML format")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Select the PDF file you want to convert to HTML"
    )
    
    if uploaded_file:
        # Display file info
        file_size = get_file_size_mb(uploaded_file)
        st.info(f"📄 **{uploaded_file.name}** ({file_size:.2f} MB)")
        
        # Save uploaded file
        input_path = save_uploaded_file(uploaded_file, "pdf_to_html")
        
        if input_path:
            try:
                # Get page count
                pdf_doc = fitz.open(input_path)
                total_pages = len(pdf_doc)
                pdf_doc.close()
                
                st.success(f"✅ PDF loaded: {total_pages} pages")
                
                # Conversion settings
                st.write("### ⚙️ Conversion Settings")
                
                include_images = st.checkbox(
                    "Include images",
                    value=True,
                    help="Extract and embed images in the HTML file"
                )
                
                st.info("💡 **Note:** Complex layouts and formatting will be simplified. Images are embedded as base64.")
                
                # Convert button
                if st.button("🔄 Convert to HTML", type="primary", use_container_width=True):
                    with st.spinner("Converting PDF to HTML..."):
                        # Create output path
                        output_dir = os.path.join("output", "pdf_to_html")
                        os.makedirs(output_dir, exist_ok=True)
                        output_path = os.path.join(output_dir, get_unique_filename("converted.html"))
                        
                        # Convert PDF to HTML
                        success = pdf_to_html(input_path, output_path, include_images)
                        
                        if success:
                            st.success(f"✅ Successfully converted PDF to HTML!")
                            
                            # Read HTML content
                            with open(output_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            # Show preview
                            with st.expander("👁️ Preview HTML (first 2000 characters)"):
                                st.code(html_content[:2000] + ("..." if len(html_content) > 2000 else ""), language="html")
                            
                            # Show file info
                            output_size = os.path.getsize(output_path) / (1024 * 1024)
                            st.info(f"📄 Output HTML size: {output_size:.2f} MB")
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download HTML",
                                data=html_content,
                                file_name="converted.html",
                                mime="text/html",
                                use_container_width=True
                            )
                            
                            st.success("💡 **Tip:** Open the HTML file in any web browser to view it.")
                
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
    
    else:
        # Help section
        st.write("### 📖 How to use")
        st.markdown("""
        1. **Upload** your PDF file
        2. **Choose** whether to include images
        3. **Click** Convert to HTML
        4. **Download** your HTML file
        
        **What to expect:**
        - ✅ Text content extracted
        - ✅ Images embedded as base64 (if enabled)
        - ✅ Basic HTML structure
        - ⚠️ Complex layouts simplified
        
        **Best for:**
        - Converting documents for web viewing
        - Extracting text content
        - Creating web-readable versions
        
        **Output includes:**
        - Clean HTML5 structure
        - Embedded CSS styling
        - Page separation
        - Base64-encoded images
        """)


if __name__ == "__main__":
    render_pdf_to_html_tool()
