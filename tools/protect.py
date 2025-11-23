"""Protect and unlock PDF files with passwords."""
import os
import streamlit as st
import pikepdf
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_ops import save_uploaded_file, get_unique_filename, get_file_size_mb
from utils.pdf_ops import is_pdf_encrypted, get_pdf_page_count
from utils.preview import show_pdf_preview


def protect_pdf(input_path: str, output_path: str, user_password: str = "", owner_password: str = "", 
                allow_printing: bool = True, allow_modification: bool = False) -> bool:
    """
    Add password protection to a PDF file.
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save protected PDF
        user_password: Password to open the PDF
        owner_password: Password for owner permissions
        allow_printing: Allow printing
        allow_modification: Allow modifications
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with pikepdf.open(input_path) as pdf:
            # Set permissions
            permissions = pikepdf.Permissions(
                print_lowres=allow_printing,
                print_highres=allow_printing,
                modify_annotation=allow_modification,
                modify_form=allow_modification,
                modify_other=allow_modification,
                extract=True,  # Always allow text extraction
                accessibility=True  # Always allow accessibility
            )
            
            # Prepare encryption settings
            encryption_kwargs = {
                "owner": owner_password if owner_password else user_password,
                "user": user_password,
            }
            
            if allow_printing or allow_modification:
                encryption_kwargs["allow"] = permissions
            
            # Save with encryption
            pdf.save(output_path, encryption=pikepdf.Encryption(**encryption_kwargs))
        
        return True
        
    except Exception as e:
        st.error(f"Error protecting PDF: {str(e)}")
        return False


def unlock_pdf(input_path: str, output_path: str, password: str) -> bool:
    """
    Remove password protection from a PDF file.
    
    Args:
        input_path: Path to encrypted PDF
        output_path: Path to save unlocked PDF
        password: Password to open the PDF
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path)
        
        return True
        
    except pikepdf.PasswordError:
        st.error("❌ Incorrect password. Please try again.")
        return False
    except Exception as e:
        st.error(f"Error unlocking PDF: {str(e)}")
        return False


def render_protect_tool():
    """Render the Protect/Unlock PDF tool interface."""
    st.title("🔒 Protect / Unlock PDF")
    st.write("Add or remove password protection from your PDF documents.")
    
    # Mode selection
    mode = st.radio(
        "Choose operation:",
        ["🔒 Protect PDF (Add Password)", "🔓 Unlock PDF (Remove Password)"],
        key="protect_mode"
    )
    
    st.write("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=['pdf'],
        key="protect_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file
        temp_path = save_uploaded_file(uploaded_file, "uploads")
        is_encrypted = is_pdf_encrypted(temp_path)
        
        st.success(f"✅ Uploaded: **{uploaded_file.name}**")
        
        if is_encrypted:
            st.warning("⚠️ This PDF is password-protected.")
        
        if mode == "🔒 Protect PDF (Add Password)":
            st.write("### Password Settings")
            
            if is_encrypted:
                st.info("💡 This PDF is already protected. You can add a new password by unlocking it first.")
            
            # Password input
            col1, col2 = st.columns(2)
            
            with col1:
                user_password = st.text_input(
                    "User Password (required to open PDF)",
                    type="password",
                    key="user_password",
                    help="Users will need this password to open the PDF"
                )
            
            with col2:
                owner_password = st.text_input(
                    "Owner Password (optional)",
                    type="password",
                    key="owner_password",
                    help="Separate password for changing permissions"
                )
            
            # Permissions
            st.write("### Permissions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                allow_printing = st.checkbox(
                    "Allow Printing",
                    value=True,
                    key="allow_printing"
                )
            
            with col2:
                allow_modification = st.checkbox(
                    "Allow Modifications",
                    value=False,
                    key="allow_modification"
                )
            
            st.info("📌 Text extraction and accessibility are always enabled.")
            
            # Protect button
            if st.button("🔒 Protect PDF", type="primary", use_container_width=True):
                if not user_password:
                    st.warning("⚠️ Please enter a user password.")
                else:
                    with st.spinner("Protecting PDF..."):
                        output_filename = f"protected_{uploaded_file.name}"
                        output_path = get_unique_filename(output_filename, "outputs")
                        
                        success = protect_pdf(
                            temp_path,
                            output_path,
                            user_password,
                            owner_password,
                            allow_printing,
                            allow_modification
                        )
                        
                        if success:
                            st.success("✅ PDF protected successfully!")
                            st.warning("🔐 **Important:** Save your password securely. You'll need it to open the PDF.")
                            
                            # Display output info
                            output_size = get_file_size_mb(output_path)
                            protected_page_count = get_pdf_page_count(output_path)
                            st.write(f"**Output:** {protected_page_count} pages, {output_size:.2f} MB")
                            
                            st.info("💡 Preview not available for password-protected PDFs (security feature)")
                            
                            # Download button
                            with open(output_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Protected PDF",
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
        
        else:  # Unlock PDF
            st.write("### Unlock PDF")
            
            if not is_encrypted:
                st.info("✅ This PDF is not password-protected. No unlock needed.")
            else:
                # Password input
                password = st.text_input(
                    "Enter PDF Password",
                    type="password",
                    key="unlock_password",
                    help="Enter the password to unlock this PDF"
                )
                
                # Unlock button
                if st.button("🔓 Unlock PDF", type="primary", use_container_width=True):
                    if not password:
                        st.warning("⚠️ Please enter the password.")
                    else:
                        with st.spinner("Unlocking PDF..."):
                            output_filename = f"unlocked_{uploaded_file.name}"
                            output_path = get_unique_filename(output_filename, "outputs")
                            
                            success = unlock_pdf(temp_path, output_path, password)
                            
                            if success:
                                st.success("✅ PDF unlocked successfully!")
                                
                                # Display output info
                                output_size = get_file_size_mb(output_path)
                                unlocked_page_count = get_pdf_page_count(output_path)
                                st.write(f"**Output:** {unlocked_page_count} pages, {output_size:.2f} MB")
                                
                                # Show preview
                                st.write("### 🔍 Preview")
                                try:
                                    with open(output_path, "rb") as f:
                                        preview_data = f.read()
                                    
                                    # Display PDF preview in browser
                                    st.success(f"✅ Preview - {unlocked_page_count} pages unlocked")
                                    show_pdf_preview(preview_data, height=1000)
                                except Exception as e:
                                    st.warning(f"Preview unavailable: {str(e)}")
                                
                                # Download button
                                with open(output_path, "rb") as file:
                                    st.download_button(
                                        label="⬇️ Download Unlocked PDF",
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
    render_protect_tool()
