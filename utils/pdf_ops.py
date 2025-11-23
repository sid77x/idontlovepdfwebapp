"""PDF operations utility functions."""
import PyPDF2
from typing import List, Tuple


def get_pdf_info(filepath: str) -> dict:
    """Get basic PDF information."""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            info = {
                'num_pages': len(reader.pages),
                'is_encrypted': reader.is_encrypted,
                'metadata': reader.metadata if reader.metadata else {},
            }
            
            return info
    except Exception as e:
        return {'error': str(e)}


def get_pdf_page_count(filepath: str) -> int:
    """Get the number of pages in a PDF."""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    except Exception:
        return 0


def is_pdf_encrypted(filepath: str) -> bool:
    """Check if PDF is password protected."""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return reader.is_encrypted
    except Exception:
        return False


def validate_pdf(filepath: str) -> Tuple[bool, str]:
    """Validate if file is a readable PDF."""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            _ = len(reader.pages)  # Try to access pages
        return True, "Valid PDF"
    except PyPDF2.errors.PdfReadError as e:
        return False, f"Invalid PDF: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_pdf_size_info(filepath: str) -> dict:
    """Get PDF size information using PyPDF2."""
    try:
        import os
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            info = {
                'page_count': len(reader.pages),
                'file_size_mb': os.path.getsize(filepath) / (1024 * 1024),
                'pages': []
            }
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                mediabox = page.mediabox
                
                info['pages'].append({
                    'page_num': page_num + 1,
                    'width': float(mediabox.width),
                    'height': float(mediabox.height),
                    'rotation': page.get('/Rotate', 0)
                })
            
            return info
        
    except Exception as e:
        return {'error': str(e)}


def parse_page_range(page_range: str, total_pages: int) -> List[int]:
    """
    Parse page range string into list of page numbers.
    Examples: "1,3,5", "1-5", "1-3,7,9-11"
    Returns 0-indexed page numbers.
    """
    pages = []
    
    try:
        parts = page_range.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                start = int(start)
                end = int(end)
                
                if start < 1 or end > total_pages or start > end:
                    continue
                
                pages.extend(range(start - 1, end))  # Convert to 0-indexed
            else:
                page_num = int(part)
                
                if 1 <= page_num <= total_pages:
                    pages.append(page_num - 1)  # Convert to 0-indexed
        
        return sorted(list(set(pages)))  # Remove duplicates and sort
        
    except Exception:
        return []
