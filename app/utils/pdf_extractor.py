"""
PDF text extraction utilities using PyMuPDF.
Converts PDF files to formatted text files for LLM processing.
"""

from pathlib import Path
import pymupdf


def pdf_to_text(pdf_path: str, output_path: str) -> str:
    """
    Extract text from PDF and save to text file.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path where the text file should be saved
        
    Returns:
        Path to the saved text file
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF cannot be processed
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Open PDF
    doc = pymupdf.open(pdf_path)
    
    # Extract text from all pages without page separators
    text_parts = []
    for page in doc:
        # Get text preserving whitespace and layout
        text = page.get_text("text", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
        if text:
            text_parts.append(text.rstrip())
    
    doc.close()
    
    # Join pages with double newline separator
    full_text = "\n\n".join(text_parts)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Write to text file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    return output_path