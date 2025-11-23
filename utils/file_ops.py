"""File operations utility functions."""
import os
import shutil
from pathlib import Path
from datetime import datetime


def ensure_directory_exists(directory: str) -> None:
    """Create directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_unique_filename(filename: str, directory: str = None) -> str:
    """
    Generate unique filename by appending timestamp if file exists.
    
    Args:
        filename: The base filename
        directory: Optional directory path. If provided, checks for existence and returns full path.
                   If not provided, just returns the unique filename without a path.
    
    Returns:
        Either just the unique filename (if directory is None) or the full path (if directory is provided).
    """
    if directory is None:
        # Just generate a unique filename without checking existence
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}{ext}"
    
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        return filepath
    
    # Split filename and extension
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{name}_{timestamp}{ext}"
    
    return os.path.join(directory, unique_filename)


def clean_temp_files(directory: str, max_age_hours: int = 24) -> None:
    """Remove temporary files older than specified hours."""
    if not os.path.exists(directory):
        return
    
    current_time = datetime.now().timestamp()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing {filepath}: {e}")


def get_file_size_mb(filepath) -> float:
    """
    Get file size in megabytes.
    Accepts either a file path (str) or a Streamlit UploadedFile object.
    """
    if hasattr(filepath, 'size'):
        # It's a Streamlit UploadedFile object
        return filepath.size / (1024 * 1024)
    elif hasattr(filepath, 'getvalue'):
        # It's a file-like object with getvalue method
        return len(filepath.getvalue()) / (1024 * 1024)
    else:
        # It's a file path string
        return os.path.getsize(filepath) / (1024 * 1024)


def save_uploaded_file(uploaded_file, directory: str) -> str:
    """Save uploaded file to directory and return the filepath."""
    ensure_directory_exists(directory)
    filepath = get_unique_filename(uploaded_file.name, directory)
    
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath


def cleanup_directory(directory: str) -> None:
    """Remove all files in a directory."""
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            except Exception as e:
                print(f"Error removing {filepath}: {e}")
