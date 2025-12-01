"""
Convert .pdf readings to .txt files.
"""

import os
from pathlib import Path
from pypdf import PdfReader


def convert_pdf_to_txt(pdf_path: Path, output_path: Path) -> bool:
    """
    Convert a single .pdf file to .txt.
    
    Args:
        pdf_path: Path to the .pdf file
        output_path: Path where the .txt file will be saved
        
    Returns:
        True if successful, False otherwise
    """
    try:
        reader = PdfReader(pdf_path)
        
        # Extract text from all pages
        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
        
        # Write to output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(text_content))
        
        print(f"✓ Converted: {pdf_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to convert {pdf_path.name}: {e}")
        return False


def convert_all_readings(
    input_dir: str = "data/readings-pdf",
    output_dir: str = "data/readings-txt"
) -> dict[str, bool]:
    """
    Convert all .pdf files in input_dir to .txt files in output_dir.
    
    Args:
        input_dir: Directory containing .pdf files
        output_dir: Directory where .txt files will be saved
        
    Returns:
        Dictionary mapping filenames to conversion success status
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Check if input directory exists
    if not input_path.exists():
        print(f"Input directory does not exist: {input_dir}")
        return {}
    
    # Get all .pdf files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No .pdf files found in {input_dir}")
        return {}
    
    print(f"\nConverting {len(pdf_files)} readings...")
    
    results = {}
    for pdf_file in pdf_files:
        # Create output filename (replace .pdf with .txt)
        txt_filename = pdf_file.stem + ".txt"
        txt_path = output_path / txt_filename
        
        success = convert_pdf_to_txt(pdf_file, txt_path)
        results[pdf_file.name] = success
    
    successful = sum(1 for v in results.values() if v)
    print(f"\nCompleted: {successful}/{len(pdf_files)} readings converted successfully")
    
    return results


if __name__ == "__main__":
    convert_all_readings()



