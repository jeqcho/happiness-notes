"""
Generate only the master combined PDF from all markdown lecture notes.
"""

from pathlib import Path
from generate_pdfs import combine_markdown_to_pdf, check_quarto


def generate_master_pdf_only(
    notes_dir: str = "lecture-notes",
    pdfs_dir: str = "lecture-notes-pdf"
) -> None:
    """
    Generate only the master combined PDF from all markdown notes.
    
    Args:
        notes_dir: Directory containing markdown notes
        pdfs_dir: Directory where PDF will be saved
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
    print("GENERATING MASTER PDF")
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
    
    # Generate master PDF
    master_pdf = pdfs_path / "00-all-lectures-combined.pdf"
    success = combine_markdown_to_pdf(md_files, master_pdf)
    
    if success:
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Master PDF: ✓")
        print(f"Saved to: {master_pdf}")
    else:
        print("\n" + "=" * 70)
        print("FAILED")
        print("=" * 70)
        print("Could not generate master PDF. Check error messages above.")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == "__main__":
    generate_master_pdf_only()

