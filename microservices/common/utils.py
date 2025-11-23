"""Common utilities for PDF microservices."""
import os
import shutil
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List


def ensure_directory_exists(directory: str) -> None:
    """Create directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_unique_filename(filename: str, directory: str = None) -> str:
    """
    Generate unique filename by appending timestamp if file exists.
    
    Args:
        filename: The base filename
        directory: Optional directory path. If provided, returns full path.
    
    Returns:
        str: Unique filename or full path
    """
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if directory:
        ensure_directory_exists(directory)
        base_path = os.path.join(directory, filename)
        
        if not os.path.exists(base_path):
            return base_path
        
        counter = 1
        while True:
            new_filename = f"{name}_{timestamp}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1
    else:
        if not os.path.exists(filename):
            return filename
        
        counter = 1
        while True:
            new_filename = f"{name}_{timestamp}_{counter}{ext}"
            if not os.path.exists(new_filename):
                return new_filename
            counter += 1


def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def copy_file(src: str, dst: str) -> bool:
    """Copy a file from source to destination."""
    try:
        ensure_directory_exists(os.path.dirname(dst))
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def move_file(src: str, dst: str) -> bool:
    """Move a file from source to destination."""
    try:
        ensure_directory_exists(os.path.dirname(dst))
        shutil.move(src, dst)
        return True
    except Exception:
        return False


def cleanup_files(*file_paths: str) -> None:
    """Clean up multiple files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0.0


def create_temp_file(suffix: str = "", prefix: str = "pdf_") -> str:
    """Create a temporary file and return its path."""
    with tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, delete=False) as f:
        return f.name


def parse_page_range(page_range: str, total_pages: int) -> Optional[List[int]]:
    """
    Parse page range string and return list of 0-indexed page numbers.
    
    Args:
        page_range: String like "1-3,5,7-9" (1-indexed)
        total_pages: Total number of pages in document
    
    Returns:
        List of 0-indexed page numbers, or None if invalid
    """
    try:
        pages = set()
        
        # Split by commas and process each part
        parts = [part.strip() for part in page_range.split(',')]
        
        for part in parts:
            if '-' in part:
                # Handle range like "1-3"
                start, end = part.split('-', 1)
                start_page = int(start.strip())
                end_page = int(end.strip())
                
                # Validate range
                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    return None
                
                # Add pages to set (convert to 0-indexed)
                for page_num in range(start_page - 1, end_page):
                    pages.add(page_num)
            else:
                # Handle single page like "5"
                page_num = int(part.strip())
                
                # Validate page number
                if page_num < 1 or page_num > total_pages:
                    return None
                
                # Add page to set (convert to 0-indexed)
                pages.add(page_num - 1)
        
        return sorted(list(pages))
    
    except (ValueError, AttributeError):
        return None


def validate_pdf_file(file_path: str) -> bool:
    """Basic validation to check if file is a PDF."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


def get_safe_filename(filename: str) -> str:
    """Get a safe filename by removing/replacing dangerous characters."""
    # Remove or replace dangerous characters
    safe_chars = []
    for char in filename:
        if char.isalnum() or char in '.-_':
            safe_chars.append(char)
        elif char in ' ':
            safe_chars.append('_')
    
    safe_filename = ''.join(safe_chars)
    
    # Ensure it doesn't start with a dot
    if safe_filename.startswith('.'):
        safe_filename = 'file' + safe_filename
    
    # Ensure it has an extension
    if '.' not in safe_filename:
        safe_filename += '.pdf'
    
    return safe_filename[:255]  # Limit length


class FileManager:
    """File management utility class."""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        ensure_directory_exists(base_dir)
    
    def save_upload(self, content: bytes, filename: str) -> str:
        """Save uploaded file content and return path."""
        safe_filename = get_safe_filename(filename)
        file_path = get_unique_filename(safe_filename, self.base_dir)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path
    
    def get_output_path(self, filename: str) -> str:
        """Get unique output file path."""
        safe_filename = get_safe_filename(filename)
        return get_unique_filename(safe_filename, self.base_dir)
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up files older than max_age_hours."""
        import time
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        for file_path in Path(self.base_dir).glob('*'):
            if file_path.is_file():
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors