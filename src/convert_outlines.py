"""
Convert .docx lecture outlines to .txt files.
"""

import os
from pathlib import Path
from docx import Document


def convert_docx_to_txt(docx_path: Path, output_path: Path) -> bool:
    """
    Convert a single .docx file to .txt.
    
    Args:
        docx_path: Path to the .docx file
        output_path: Path where the .txt file will be saved
        
    Returns:
        True if successful, False otherwise
    """
    try:
        doc = Document(docx_path)
        
        # Extract all text from paragraphs
        text_content = []
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)
        
        # Write to output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))
        
        print(f"✓ Converted: {docx_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to convert {docx_path.name}: {e}")
        return False


def convert_all_outlines(
    input_dir: str = "data/lecture-outlines-docx",
    output_dir: str = "data/lecture-outlines-txt"
) -> dict[str, bool]:
    """
    Convert all .docx files in input_dir to .txt files in output_dir.
    
    Args:
        input_dir: Directory containing .docx files
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
    
    # Get all .docx files
    docx_files = list(input_path.glob("*.docx"))
    
    if not docx_files:
        print(f"No .docx files found in {input_dir}")
        return {}
    
    print(f"\nConverting {len(docx_files)} lecture outlines...")
    
    results = {}
    for docx_file in docx_files:
        # Create output filename (replace .docx with .txt)
        txt_filename = docx_file.stem + ".txt"
        txt_path = output_path / txt_filename
        
        success = convert_docx_to_txt(docx_file, txt_path)
        results[docx_file.name] = success
    
    successful = sum(1 for v in results.values() if v)
    print(f"\nCompleted: {successful}/{len(docx_files)} outlines converted successfully")
    
    return results


if __name__ == "__main__":
    convert_all_outlines()



