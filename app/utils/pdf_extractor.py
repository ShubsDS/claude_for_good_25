"""
PDF text extraction utilities using PyMuPDF.
Converts PDF files to formatted text files for LLM processing.
"""

from pathlib import Path
import re
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
    
    # Extract text from all pages (avoid preserving raw whitespace which can cause line breaks mid-paragraph)
    text_parts = []
    for page in doc:
        # Use the default "text" extraction which normalizes spacing better than preserving raw layout
        text = page.get_text("text")
        if text:
            text_parts.append(text.strip())
    
    doc.close()
    
    # Join pages with double newline separator
    full_text = "\n\n".join(text_parts)
    
    # Normalize whitespace: collapse single newlines inside paragraphs into spaces,
    # but preserve paragraph breaks (two or more newlines).
    paragraphs = re.split(r'\n{2,}', full_text)
    cleaned_paragraphs = [re.sub(r'\s+', ' ', p).strip() for p in paragraphs if p.strip()]
    normalized = "\n\n".join(cleaned_paragraphs)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Write to text file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(normalized)
    
    return output_path