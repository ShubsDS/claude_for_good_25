#!/usr/bin/env python3
"""
Test script for PDF text extraction.
Tests the pdf_to_text function with sample PDFs.
python -m app.api.tests.test_pdf_extractor
"""

import sys
from pathlib import Path

from ...utils.pdf_extractor import pdf_to_text


def test_pdf_extraction():
    """
    Test PDF extraction with sample files.
    Place test PDF files in data/test_pdfs/ directory.
    """
    test_pdfs_dir = Path("data/test_pdfs")
    output_dir = Path("data/submissions/test_output")
    
    # Check if test directory exists
    if not test_pdfs_dir.exists():
        print(f"Creating test directory: {test_pdfs_dir}")
        test_pdfs_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n⚠️  Please add test PDF files to {test_pdfs_dir}")
        print("Then run this test again.")
        return
    
    # Find all PDF files in test directory
    pdf_files = list(test_pdfs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {test_pdfs_dir}")
        print(f"\n⚠️  Please add test PDF files to {test_pdfs_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to test:\n")
    
    # Process each PDF
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        
        try:
            # Generate output filename
            output_filename = pdf_path.stem + ".txt"
            output_path = output_dir / output_filename
            
            # Extract text
            result_path = pdf_to_text(str(pdf_path), str(output_path))
            
            # Read and display first 500 characters
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
                preview = content[:500]
                
            print(f"✅ SUCCESS")
            print(f"   Output: {result_path}")
            print(f"   Size: {len(content)} characters")
            print(f"   Preview:\n")
            print("-" * 60)
            print(preview)
            if len(content) > 500:
                print(f"\n... ({len(content) - 500} more characters)")
            print("-" * 60)
            print()
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()


def test_with_sample_pdf():
    """
    Test with any PDF files found in data/submissions directory.
    """
    submissions_dir = Path("data/submissions")
    
    if not submissions_dir.exists():
        print(f"❌ Submissions directory not found: {submissions_dir}")
        return
    
    # Find PDFs in any subdirectory
    pdf_files = list(submissions_dir.rglob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {submissions_dir}")
        return
    
    print(f"\nTesting with PDFs from submissions directory:")
    print(f"Found {len(pdf_files)} PDF file(s)\n")
    
    for pdf_path in pdf_files[:3]:  # Test first 3 PDFs only
        print(f"Testing: {pdf_path.relative_to(submissions_dir)}")
        
        try:
            # Create output path (same location, .txt extension)
            output_path = pdf_path.with_suffix('.txt')
            
            # Extract text
            result_path = pdf_to_text(str(pdf_path), str(output_path))
            
            # Show stats
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ Extracted {len(content)} characters")
            print(f"   Saved to: {output_path.relative_to(submissions_dir)}\n")
            
        except Exception as e:
            print(f"❌ ERROR: {e}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("PDF Text Extractor Test")
    print("=" * 60)
    print()
    
    # Run test with test PDFs
    print("Test 1: Sample PDFs from data/test_pdfs/")
    print("-" * 60)
    test_pdf_extraction()
    
    # Run test with actual submission PDFs if available
    print("\nTest 2: PDFs from data/submissions/")
    print("-" * 60)
    test_with_sample_pdf()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)