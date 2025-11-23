"""Crop PDF pages by adjusting mediabox."""
import os
import sys
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import get_pdf_page_count
from utils.preview import show_pdf_preview


def crop_pdf(input_path: str, output_path: str, left: float = 0, top: float = 0,
             right: float = 0, bottom: float = 0, unit: str = "points") -> bool:
    """
    Crop PDF pages by adjusting the mediabox.
    
    Args:
        input_path: Input PDF path
        output_path: Output PDF path
        left: Crop from left (in points or inches)
        top: Crop from top
        right: Crop from right
        bottom: Crop from bottom
        unit: "points" or "inches" (1 inch = 72 points)
    
    Returns:
        bool: Success status
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Convert to points if needed
        if unit == "inches":
            left *= 72
            top *= 72
            right *= 72
            bottom *= 72
        
        for page in reader.pages:
            # Get current mediabox
            mediabox = page.mediabox
            
            # Calculate new dimensions
            new_lower_left_x = float(mediabox.lower_left[0]) + left
            new_lower_left_y = float(mediabox.lower_left[1]) + bottom
            new_upper_right_x = float(mediabox.upper_right[0]) - right
            new_upper_right_y = float(mediabox.upper_right[1]) - top
            
            # Validate dimensions
            if new_lower_left_x >= new_upper_right_x or new_lower_left_y >= new_upper_right_y:
                st.error("❌ Crop values are too large - resulting page would be empty!")
                return False
            
            # Set new mediabox
            page.mediabox.lower_left = (new_lower_left_x, new_lower_left_y)
            page.mediabox.upper_right = (new_upper_right_x, new_upper_right_y)
            
            writer.add_page(page)
        
        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        st.error(f"Error cropping PDF: {str(e)}")
        return False


def render_crop_tool():
    """Render the Crop PDF tool interface."""
    st.title("✂️ Crop PDF")
    st.write("Trim the edges of your PDF pages.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=['pdf'],
        key="crop_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        total_pages = get_pdf_page_count(temp_path)
        original_size = get_file_size_mb(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}** ({total_pages} pages, {original_size:.2f} MB)")
        
        # Get page dimensions
        try:
            reader = PdfReader(temp_path)
            first_page = reader.pages[0]
            mediabox = first_page.mediabox
            width_pts = float(mediabox.width)
            height_pts = float(mediabox.height)
            width_in = width_pts / 72
            height_in = height_pts / 72
            
            st.info(f"📐 Current page size: {width_in:.2f}\" × {height_in:.2f}\" ({width_pts:.0f} × {height_pts:.0f} points)")
        except:
            st.warning("⚠️ Could not read page dimensions")
        
        # Crop settings
        st.write("### Crop Settings")
        
        unit = st.radio(
            "Measurement unit",
            ["inches", "points"],
            key="unit",
            horizontal=True,
            help="1 inch = 72 points"
        )
        
        max_val = 5.0 if unit == "inches" else 360.0
        step = 0.1 if unit == "inches" else 10.0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Horizontal Margins**")
            left = st.number_input(
                f"Left ({unit})",
                min_value=0.0,
                max_value=max_val,
                value=0.0,
                step=step,
                key="left",
                help="Amount to trim from left edge"
            )
            
            right = st.number_input(
                f"Right ({unit})",
                min_value=0.0,
                max_value=max_val,
                value=0.0,
                step=step,
                key="right",
                help="Amount to trim from right edge"
            )
        
        with col2:
            st.write("**Vertical Margins**")
            top = st.number_input(
                f"Top ({unit})",
                min_value=0.0,
                max_value=max_val,
                value=0.0,
                step=step,
                key="top",
                help="Amount to trim from top edge"
            )
            
            bottom = st.number_input(
                f"Bottom ({unit})",
                min_value=0.0,
                max_value=max_val,
                value=0.0,
                step=step,
                key="bottom",
                help="Amount to trim from bottom edge"
            )
        
        # Quick presets
        st.write("### 🎯 Quick Presets")
        st.info("💡 Click a preset to apply uniform margins to all sides")
        
        # Initialize session state for preset values if not exists
        if 'preset_left' not in st.session_state:
            st.session_state.preset_left = 0.0
            st.session_state.preset_right = 0.0
            st.session_state.preset_top = 0.0
            st.session_state.preset_bottom = 0.0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        preset_applied = False
        
        with col1:
            if st.button("📏 Small (0.25\")", use_container_width=True, help="0.25 inch margins"):
                st.session_state.preset_left = 0.25 if unit == "inches" else 18.0
                st.session_state.preset_right = 0.25 if unit == "inches" else 18.0
                st.session_state.preset_top = 0.25 if unit == "inches" else 18.0
                st.session_state.preset_bottom = 0.25 if unit == "inches" else 18.0
                preset_applied = True
        
        with col2:
            if st.button("📐 Medium (0.5\")", use_container_width=True, help="0.5 inch margins"):
                st.session_state.preset_left = 0.5 if unit == "inches" else 36.0
                st.session_state.preset_right = 0.5 if unit == "inches" else 36.0
                st.session_state.preset_top = 0.5 if unit == "inches" else 36.0
                st.session_state.preset_bottom = 0.5 if unit == "inches" else 36.0
                preset_applied = True
        
        with col3:
            if st.button("📏 Large (1\")", use_container_width=True, help="1 inch margins"):
                st.session_state.preset_left = 1.0 if unit == "inches" else 72.0
                st.session_state.preset_right = 1.0 if unit == "inches" else 72.0
                st.session_state.preset_top = 1.0 if unit == "inches" else 72.0
                st.session_state.preset_bottom = 1.0 if unit == "inches" else 72.0
                preset_applied = True
        
        with col4:
            if st.button("📄 Top/Bottom", use_container_width=True, help="Trim 0.75\" from top and bottom"):
                st.session_state.preset_left = 0.0
                st.session_state.preset_right = 0.0
                st.session_state.preset_top = 0.75 if unit == "inches" else 54.0
                st.session_state.preset_bottom = 0.75 if unit == "inches" else 54.0
                preset_applied = True
        
        with col5:
            if st.button("🔄 Reset", use_container_width=True, help="Clear all values"):
                st.session_state.preset_left = 0.0
                st.session_state.preset_right = 0.0
                st.session_state.preset_top = 0.0
                st.session_state.preset_bottom = 0.0
                preset_applied = True
        
        # Additional row of presets
        col6, col7, col8 = st.columns(3)
        
        with col6:
            if st.button("📏 Extra Large (1.5\")", use_container_width=True, help="1.5 inch margins"):
                st.session_state.preset_left = 1.5 if unit == "inches" else 108.0
                st.session_state.preset_right = 1.5 if unit == "inches" else 108.0
                st.session_state.preset_top = 1.5 if unit == "inches" else 108.0
                st.session_state.preset_bottom = 1.5 if unit == "inches" else 108.0
                preset_applied = True
        
        with col7:
            if st.button("◀️ Left/Right", use_container_width=True, help="Trim 0.5\" from left and right"):
                st.session_state.preset_left = 0.5 if unit == "inches" else 36.0
                st.session_state.preset_right = 0.5 if unit == "inches" else 36.0
                st.session_state.preset_top = 0.0
                st.session_state.preset_bottom = 0.0
                preset_applied = True
        
        with col8:
            if st.button("📐 Narrow (0.1\")", use_container_width=True, help="0.1 inch margins"):
                st.session_state.preset_left = 0.1 if unit == "inches" else 7.2
                st.session_state.preset_right = 0.1 if unit == "inches" else 7.2
                st.session_state.preset_top = 0.1 if unit == "inches" else 7.2
                st.session_state.preset_bottom = 0.1 if unit == "inches" else 7.2
                preset_applied = True
        
        # Apply preset values if a button was clicked
        if preset_applied:
            left = st.session_state.preset_left
            right = st.session_state.preset_right
            top = st.session_state.preset_top
            bottom = st.session_state.preset_bottom
            st.success(f"✅ Preset applied! Values: {left if unit == 'inches' else left} {unit} on all sides")
            st.info("💡 Scroll down to see preview")
        
        # Preview dimensions
        if any([left, top, right, bottom]):
            left_pts = left * 72 if unit == "inches" else left
            top_pts = top * 72 if unit == "inches" else top
            right_pts = right * 72 if unit == "inches" else right
            bottom_pts = bottom * 72 if unit == "inches" else bottom
            
            new_width_pts = width_pts - left_pts - right_pts
            new_height_pts = height_pts - top_pts - bottom_pts
            new_width_in = new_width_pts / 72
            new_height_in = new_height_pts / 72
            
            if new_width_pts > 0 and new_height_pts > 0:
                st.success(f"📐 New page size: {new_width_in:.2f}\" × {new_height_in:.2f}\" ({new_width_pts:.0f} × {new_height_pts:.0f} points)")
                
                # Preview - Always show when crop values are set
                st.write("### 🔍 Preview (First Page)")
                with st.spinner("Generating preview..."):
                    try:
                        import tempfile
                        
                        # Create cropped version of first page only
                        preview_path = tempfile.mktemp(suffix=".pdf")
                        
                        success_preview = crop_pdf(
                            temp_path,
                            preview_path,
                            left,
                            top,
                            right,
                            bottom,
                            unit
                        )
                        
                        if success_preview:
                            # Show all pages cropped
                            with open(preview_path, "rb") as f:
                                preview_data = f.read()
                            
                            # Encode PDF to base64 for embedding
                            import base64
                            base64_pdf = base64.b64encode(preview_data).decode('utf-8')
                            
                            # Get page count
                            reader_preview = PdfReader(preview_path)
                            preview_page_count = len(reader_preview.pages)
                            
                            # Display PDF preview in browser
                            st.success(f"✅ Preview - {preview_page_count} pages cropped")
                            show_pdf_preview(preview_data, height=1000)
                            
                            try:
                                os.remove(preview_path)
                            except:
                                pass
                    except Exception as e:
                        st.error(f"❌ Preview generation failed: {str(e)}")
            else:
                st.error("❌ Crop values are too large!")
        
        # Crop button
        if st.button("✂️ Crop All Pages", type="primary", use_container_width=True):
            if not any([left, top, right, bottom]):
                st.warning("⚠️ Please set at least one crop value.")
            else:
                with st.spinner("Cropping PDF..."):
                    output_filename = f"cropped_{uploaded_file.name}"
                    output_path = get_unique_filename(output_filename, "outputs")
                    
                    success = crop_pdf(
                        temp_path,
                        output_path,
                        left,
                        top,
                        right,
                        bottom,
                        unit
                    )
                    
                    if success:
                        st.success("✅ PDF cropped successfully!")
                        
                        # Display output info
                        output_size = get_file_size_mb(output_path)
                        st.write(f"**Output file size:** {output_size:.2f} MB")
                        
                        # Download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Cropped PDF",
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
    render_crop_tool()
