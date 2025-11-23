"""
IdontLovePDF - A Local PDF Manipulation Suite
Phase 1: Core PDF Operations (Merge, Split, Rotate, Protect, Compress)
Phase 2: Layout & Annotation Tools (Watermark, Page Numbers, Crop, Repair)
Phase 3: Conversion Layer (PDF ↔ Images, Documents)
"""

import streamlit as st
from tools.merge import render_merge_tool
from tools.split import render_split_tool
from tools.rotate import render_rotate_tool
from tools.protect import render_protect_tool
from tools.compress import render_compress_tool
from tools.watermark import render_watermark_tool
from tools.page_numbers import render_page_numbers_tool
from tools.crop import render_crop_tool
from tools.repair import render_repair_tool
from tools.pdf_to_image import render_pdf_to_image_tool
from tools.image_to_pdf import render_image_to_pdf_tool
from tools.pdf_to_word import render_pdf_to_word_tool
from tools.word_to_pdf import render_word_to_pdf_tool
from tools.pdf_to_excel import render_pdf_to_excel_tool
from tools.excel_to_pdf import render_excel_to_pdf_tool
from tools.pdf_to_html import render_pdf_to_html_tool
from tools.html_to_pdf import render_html_to_pdf_tool
from tools.pdf_to_powerpoint import render_pdf_to_powerpoint_tool
from tools.powerpoint_to_pdf import render_powerpoint_to_pdf_tool
from tools.ocr import ocr_tool


# Page configuration
st.set_page_config(
    page_title="IdontLovePDF - PDF Tools",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .tool-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


# Sidebar navigation
with st.sidebar:
    st.markdown("# 📄 IdontLovePDF")
    st.markdown("### Local PDF Manipulation Suite")
    st.markdown("---")
    
    # Tool selection with selectbox for better navigation
    st.markdown("**Select a Tool:**")
    
    selected_tool = st.selectbox(
        "Tool",
        [
            "🏠 Home",
            "📄 Merge PDF",
            "✂️ Split PDF",
            "🔄 Rotate PDF",
            "🔒 Protect / Unlock PDF",
            "🗜️ Compress PDF",
            "💧 Watermark PDF",
            "🔢 Page Numbers",
            "✂️ Crop PDF",
            "🔧 Repair PDF",
            "� OCR (Text Recognition)",
            "�📸 PDF to Image",
            "🖼️ Image to PDF",
            "📝 PDF to Word",
            "📄 Word to PDF",
            "📊 PDF to Excel",
            "📈 Excel to PDF",
            "🌐 PDF to HTML",
            "🌍 HTML to PDF",
            "📊 PDF to PowerPoint",
            "📽️ PowerPoint to PDF"
        ],
        key="tool_selector",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Phase info
    with st.expander("📊 Phase 1 - Core Operations"):
        st.write("""
        ✅ Merge PDF
        ✅ Split PDF
        ✅ Rotate PDF
        ✅ Protect/Unlock PDF
        ✅ Compress PDF
        """)
    
    with st.expander("🎨 Phase 2 - Layout & Annotation"):
        st.write("""
        ✅ Watermark PDF
        ✅ Page Numbers
        ✅ Crop PDF
        ✅ Repair PDF
        """)
    
    # About section
    with st.expander("ℹ️ About"):
        st.write("""
        **IdontLovePDF** is a local, privacy-first PDF manipulation suite.
        
        All processing happens on your machine - no files are uploaded to any server.
        
        **Current Phase:** Phase 2 (Layout & Annotation)
        - Built with Python, Streamlit, PyPDF2, pikepdf, and reportlab
        """)
    
    st.markdown("---")
    st.caption("🔒 Privacy-first • 100% Local Processing")


# Main content area
def render_home():
    """Render the home page."""
    st.markdown('<div class="main-header">📄 IdontLovePDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your Local PDF Manipulation Suite - Privacy First</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Welcome message
    st.write("### Welcome! 👋")
    st.write("""
    **IdontLovePDF** is a powerful, privacy-focused PDF manipulation suite that runs entirely on your local machine.
    No uploads, no cloud processing - your files stay on your computer.
    """)
    
    st.write("### 🚀 Available Tools")
    
    # Tool cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Phase 1: Core Operations**")
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 📄 Merge PDF")
        st.write("Combine multiple PDF files into a single document.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### ✂️ Split PDF")
        st.write("Split a PDF into multiple files by pages or ranges.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 🔄 Rotate PDF")
        st.write("Rotate pages in your PDF documents.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 🔒 Protect / Unlock PDF")
        st.write("Add or remove password protection from PDFs.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 🗜️ Compress PDF")
        st.write("Reduce PDF file size by compressing images.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("**Phase 2: Layout & Annotation**")
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 💧 Watermark PDF")
        st.write("Add text watermarks to your PDF pages.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 🔢 Page Numbers")
        st.write("Add customizable page numbers to PDF pages.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### ✂️ Crop PDF")
        st.write("Trim the edges of your PDF pages.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 🔧 Repair PDF")
        st.write("Fix corrupted or damaged PDF files.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("**Phase 3: Conversion Tools** 🆕")
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 📸 PDF ↔ Image")
        st.write("Convert PDF to PNG/JPG or images to PDF.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 📝 PDF ↔ Word")
        st.write("Convert PDF to editable Word or Word to PDF.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### � PDF ↔ Excel")
        st.write("Extract tables to Excel or convert Excel to PDF.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 📽️ PDF ↔ PowerPoint")
        st.write("Convert presentations between PDF and PPTX.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("#### 🌐 PDF ↔ HTML")
        st.write("Convert PDF to HTML or HTML to PDF.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting started
    st.write("### 🎯 Getting Started")
    st.write("""
    1. Select a tool from the sidebar
    2. Upload your PDF file(s)
    3. Configure settings (if applicable)
    4. Process and download your result
    
    **That's it!** All processing happens locally on your machine.
    """)
    
    # Features
    st.write("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("🔒 **100% Private**")
        st.write("All files processed locally")
    
    with col2:
        st.write("⚡ **Fast Processing**")
        st.write("No upload/download delays")
    
    with col3:
        st.write("🆓 **Free & Open**")
        st.write("No limits, no subscriptions")
    
    st.markdown("---")
    
    # Roadmap
    with st.expander("🗺️ Development Roadmap"):
        st.write("""
        **Phase 1: Core PDF Operations** ✅ Complete
        - Merge, Split, Rotate, Protect, Compress
        
        **Phase 2: Layout & Annotation Tools** ✅ Complete
        - Watermark, Page Numbers, Crop, Repair
        
        **Phase 3: Conversion Layer** ✅ Complete
        - ✅ PDF ↔ Image (PNG, JPG)
        - ✅ PDF ↔ Word (DOCX)
        - ✅ PDF ↔ Excel (XLSX)
        - ✅ PDF ↔ PowerPoint (PPTX)
        - ✅ PDF ↔ HTML
        
        **Phase 4: Intelligence Layer** 🚧 In Progress
        - ✅ OCR (CPU/GPU with Tesseract & EasyOCR)
        - 📋 Redaction, PDF/A, Compare (Coming Soon)
        
        **Phase 5: Automation & Integration** (Coming Soon)
        - Workflows, Digital Signatures, Advanced Editing
        """)


# Route to appropriate tool
if selected_tool == "🏠 Home":
    render_home()
elif selected_tool == "📄 Merge PDF":
    render_merge_tool()
elif selected_tool == "✂️ Split PDF":
    render_split_tool()
elif selected_tool == "🔄 Rotate PDF":
    render_rotate_tool()
elif selected_tool == "🔒 Protect / Unlock PDF":
    render_protect_tool()
elif selected_tool == "🗜️ Compress PDF":
    render_compress_tool()
elif selected_tool == "💧 Watermark PDF":
    render_watermark_tool()
elif selected_tool == "🔢 Page Numbers":
    render_page_numbers_tool()
elif selected_tool == "✂️ Crop PDF":
    render_crop_tool()
elif selected_tool == "🔧 Repair PDF":
    render_repair_tool()
elif selected_tool == "� OCR (Text Recognition)":
    ocr_tool()
elif selected_tool == "�📸 PDF to Image":
    render_pdf_to_image_tool()
elif selected_tool == "🖼️ Image to PDF":
    render_image_to_pdf_tool()
elif selected_tool == "📝 PDF to Word":
    render_pdf_to_word_tool()
elif selected_tool == "📄 Word to PDF":
    render_word_to_pdf_tool()
elif selected_tool == "📊 PDF to Excel":
    render_pdf_to_excel_tool()
elif selected_tool == "📈 Excel to PDF":
    render_excel_to_pdf_tool()
elif selected_tool == "🌐 PDF to HTML":
    render_pdf_to_html_tool()
elif selected_tool == "🌍 HTML to PDF":
    render_html_to_pdf_tool()
elif selected_tool == "📊 PDF to PowerPoint":
    render_pdf_to_powerpoint_tool()
elif selected_tool == "📽️ PowerPoint to PDF":
    render_powerpoint_to_pdf_tool()
else:
    render_home()


# Footer
st.markdown("---")
st.caption("Built with ❤️ using Python, Streamlit, PyPDF2, pikepdf, reportlab, PyMuPDF, and more")
