"""
Generate PDFs from markdown lecture notes.
"""

import subprocess
import shutil
from pathlib import Path
from typing import List, Optional


def check_quarto() -> bool:
    """
    Check if quarto is installed.
    
    Returns:
        True if quarto is available, False otherwise
    """
    return shutil.which("quarto") is not None


def markdown_to_pdf_quarto(
    md_file: Path,
    pdf_file: Path,
    title: Optional[str] = None
) -> bool:
    """
    Convert markdown to PDF using Quarto with clean, modern formatting.
    
    Args:
        md_file: Path to markdown file
        pdf_file: Path to output PDF file
        title: Optional title for the PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Quarto uses YAML frontmatter for configuration
        # Create a temporary file in the output directory
        pdf_file.parent.mkdir(parents=True, exist_ok=True)
        temp_md = pdf_file.parent / f"temp_{md_file.name}"
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create YAML frontmatter
        frontmatter = f"""---
title: "{title if title else md_file.stem}"
format:
  pdf:
    documentclass: article
    papersize: letter
    margin-top: 1in
    margin-bottom: 1in
    margin-left: 1in
    margin-right: 1in
    fontsize: 11pt
    mainfont: "Helvetica"
    monofont: "Courier"
    colorlinks: true
    linkcolor: blue
    urlcolor: blue
---

"""
        
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)
        
        # Quarto output must be just a filename, run in the output directory
        cmd = [
            "quarto",
            "render",
            str(temp_md.absolute()),
            "--to", "pdf",
            "--output", pdf_file.name
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(pdf_file.parent.absolute())
        )
        
        # Clean up temp file
        if temp_md.exists():
            temp_md.unlink()
        
        if result.returncode == 0:
            print(f"  ✓ Generated PDF: {pdf_file.name}")
            return True
        else:
            print(f"  ✗ Failed to generate {pdf_file.name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout generating {pdf_file.name}")
        return False
    except Exception as e:
        print(f"  ✗ Error generating {pdf_file.name}: {e}")
        return False


def combine_pdfs_pandoc(pdf_files: List[Path], output_file: Path) -> bool:
    """
    Combine multiple PDFs into one master PDF using pandoc.
    
    Args:
        pdf_files: List of PDF file paths to combine
        output_file: Path to output master PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # We'll combine by converting markdown files together
        # This gives better formatting than merging PDFs
        print("\nNote: For better results, combine markdown files first, then convert to PDF")
        return False
            
    except Exception as e:
        print(f"Error combining PDFs: {e}")
        return False


def combine_markdown_to_pdf(
    md_files: List[Path],
    output_file: Path,
    title: str = "Happiness Lecture Notes - Complete Collection"
) -> bool:
    """
    Combine multiple markdown files and convert to single PDF.
    
    Args:
        md_files: List of markdown file paths to combine
        output_file: Path to output master PDF
        title: Title for the master PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Sort files numerically by extracting the leading number
        def get_sort_key(path: Path) -> tuple:
            """Extract numeric prefix for sorting, or use filename if no number."""
            stem = path.stem
            parts = stem.split("-", 1)
            if parts[0].isdigit():
                return (int(parts[0]), stem)
            else:
                # Put non-numbered files at the end
                return (999, stem)
        
        md_files = sorted(md_files, key=get_sort_key)
        
        # Create a temporary combined markdown file
        temp_md = Path("temp_combined.md")
        
        with open(temp_md, 'w', encoding='utf-8') as out_f:
            # Write Quarto YAML frontmatter
            out_f.write(f"""---
title: "{title}"
format:
  pdf:
    documentclass: article
    papersize: letter
    margin-top: 1in
    margin-bottom: 1in
    margin-left: 1in
    margin-right: 1in
    fontsize: 11pt
    mainfont: "Helvetica"
    monofont: "Courier"
    colorlinks: true
    linkcolor: blue
    urlcolor: blue
    toc: true
    toc-depth: 1
---

""")
            
            # Combine all markdown files
            for i, md_file in enumerate(md_files):
                if i > 0:
                    out_f.write("\n\\newpage\n\n")
                
                # Add lecture header with simple number: title format
                # Extract number and clean up the name
                stem = md_file.stem  # e.g., "1-plato"
                parts = stem.split("-", 1)
                if len(parts) == 2:
                    number = parts[0]
                    name = parts[1].replace("-", " ").title()
                    out_f.write(f"# {number}: {name}\n\n")
                else:
                    lecture_name = stem.replace("-", " ").title()
                    out_f.write(f"# {lecture_name}\n\n")
                
                # Read and write content
                with open(md_file, 'r', encoding='utf-8') as in_f:
                    content = in_f.read()
                    # Adjust heading levels (shift down by 1) to make them subsections
                    lines = content.split('\n')
                    adjusted_lines = []
                    for line in lines:
                        if line.startswith('#'):
                            adjusted_lines.append('#' + line)
                        else:
                            adjusted_lines.append(line)
                    out_f.write('\n'.join(adjusted_lines))
        
        # Convert combined markdown to PDF using Quarto
        print(f"\nGenerating master PDF: {output_file.name}")
        cmd = [
            "quarto",
            "render",
            str(temp_md.absolute()),
            "--to", "pdf",
            "--output", output_file.name
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(output_file.parent.absolute())
        )
        
        # Clean up temp file
        temp_md.unlink()
        
        if result.returncode == 0:
            print(f"  ✓ Generated master PDF: {output_file.name}")
            return True
        else:
            print(f"  ✗ Failed to generate master PDF: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating master PDF: {e}")
        if temp_md.exists():
            temp_md.unlink()
        return False


def generate_all_pdfs(
    notes_dir: str = "lecture-notes",
    pdfs_dir: str = "lecture-notes-pdf"
) -> None:
    """
    Generate PDFs for all markdown lecture notes.
    
    Args:
        notes_dir: Directory containing markdown notes
        pdfs_dir: Directory where PDFs will be saved
    """
    notes_path = Path(notes_dir)
    pdfs_path = Path(pdfs_dir)
    
    # Check if quarto is installed
    if not check_quarto():
        print("Error: Quarto is not installed!")
        print("\nTo install Quarto:")
        print("  macOS: brew install --cask quarto")
        print("  Linux: Download from https://quarto.org/docs/get-started/")
        print("  Or visit: https://quarto.org/docs/download/")
        return
    
    print("=" * 70)
    print("GENERATING PDF LECTURE NOTES")
    print("=" * 70)
    
    # Create output directory
    pdfs_path.mkdir(parents=True, exist_ok=True)
    
    # Get all markdown files and sort them numerically
    def get_sort_key(path: Path) -> tuple:
        """Extract numeric prefix for sorting, or use filename if no number."""
        stem = path.stem
        parts = stem.split("-", 1)
        if parts[0].isdigit():
            return (int(parts[0]), stem)
        else:
            # Put non-numbered files at the end
            return (999, stem)
    
    md_files = sorted(notes_path.glob("*.md"), key=get_sort_key)
    
    if not md_files:
        print(f"\nNo markdown files found in {notes_dir}")
        return
    
    print(f"\nFound {len(md_files)} lecture note(s)")
    print("\nGenerating individual PDFs...")
    
    # Generate individual PDFs
    results = []
    for md_file in md_files:
        # Create corresponding PDF filename
        pdf_file = pdfs_path / (md_file.stem + ".pdf")
        
        # Extract lecture name for title
        lecture_name = md_file.stem.replace("-", " ").title()
        
        success = markdown_to_pdf_quarto(md_file, pdf_file, title=lecture_name)
        results.append((md_file.name, success))
    
    # Summary of individual PDFs
    successful = sum(1 for _, success in results if success)
    print(f"\nGenerated {successful}/{len(results)} individual PDFs")
    
    if successful == 0:
        print("\nNo PDFs were generated successfully. Skipping master PDF.")
        return
    
    # Generate master PDF
    print("\n" + "=" * 70)
    print("GENERATING MASTER PDF")
    print("=" * 70)
    
    master_pdf = pdfs_path / "00-all-lectures-combined.pdf"
    success = combine_markdown_to_pdf(md_files, master_pdf)
    
    if success:
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\nIndividual PDFs: {successful}/{len(results)}")
        print(f"Master PDF: ✓")
        print(f"\nAll PDFs saved in: {pdfs_path}/")
        
        # List failed conversions if any
        if successful < len(results):
            print("\nFailed conversions:")
            for name, success in results:
                if not success:
                    print(f"  - {name}")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == "__main__":
    generate_all_pdfs()

