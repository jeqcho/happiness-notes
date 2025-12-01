"""
Generate notes for a single lecture by number.
"""

import sys
from pathlib import Path
from typing import Optional
from convert_outlines import convert_all_outlines
from generate_notes import (
    load_text_file,
    get_matching_readings,
    load_lecture_naming,
    load_exam_guide,
    parse_output_filename,
    generate_lecture_notes
)


def extract_lecture_number(outline_filename: str, naming_mapping: dict[str, str] = None) -> Optional[str]:
    """
    Extract lecture number from outline filename or naming mapping.
    
    Args:
        outline_filename: Name of the outline file
        naming_mapping: Optional naming mapping to check for assigned numbers
        
    Returns:
        Lecture number as string, or None if not found
    """
    # First try to get from filename
    parts = outline_filename.split()
    if parts and parts[0].isdigit():
        return parts[0]
    
    # If not in filename, try to extract from naming mapping
    if naming_mapping:
        docx_filename = outline_filename.replace(".txt", ".docx")
        if docx_filename in naming_mapping:
            output_filename = naming_mapping[docx_filename]
            # Extract number from output filename (e.g., "9-laozi.md" -> "9")
            if output_filename and output_filename[0].isdigit():
                num_parts = output_filename.split("-")
                if num_parts and num_parts[0].isdigit():
                    return num_parts[0]
    
    return None


def generate_single_lecture(lecture_number: str, generate_pdf: bool = False):
    """
    Generate notes for a single lecture by number.
    
    Args:
        lecture_number: Lecture number as string (e.g., "21")
        generate_pdf: If True, also generate PDF for this lecture
    """
    # Define paths
    outlines_docx_dir = Path("data/lecture-outlines-docx")
    outlines_txt_dir = Path("data/lecture-outlines-txt")
    readings_txt_dir = Path("data/readings-txt")
    transcripts_dir = Path("data/lecture-transcripts")
    notes_dir = Path("lecture-notes")
    
    # Step 1: Convert outline if needed
    print(f"Converting outline for lecture {lecture_number}...")
    convert_all_outlines(
        input_dir=str(outlines_docx_dir),
        output_dir=str(outlines_txt_dir)
    )
    
    # Step 2: Find the outline file
    outline_files = list(outlines_txt_dir.glob(f"{lecture_number} *.txt"))
    if not outline_files:
        print(f"Error: No outline file found for lecture {lecture_number}")
        print(f"Looking for files matching: {lecture_number} *.txt")
        sys.exit(1)
    
    outline_file = outline_files[0]
    print(f"Found outline: {outline_file.name}")
    
    # Step 3: Load mappings
    print("Loading configuration...")
    naming_mapping = load_lecture_naming()
    exam_guide = load_exam_guide()
    
    # Step 4: Process the lecture
    print(f"\nProcessing lecture {lecture_number}...")
    
    # Load outline
    outline_text = load_text_file(outline_file)
    if not outline_text:
        print(f"  ✗ Could not load outline")
        sys.exit(1)
    
    # Get matching readings
    readings_texts = get_matching_readings(
        outline_file.name,
        readings_txt_dir
    )
    
    if not readings_texts:
        print(f"  ⚠ No matching readings found")
    else:
        print(f"  ✓ Found {len(readings_texts)} matching reading(s)")
    
    # Check for lecture transcript
    transcript_file = transcripts_dir / outline_file.name
    transcript_text = load_text_file(transcript_file)
    
    if transcript_text:
        print(f"  ✓ Found lecture transcript")
    else:
        print(f"  ⚠ No lecture transcript found (will proceed without it)")
    
    # Get exam topics if available
    lecture_num = extract_lecture_number(outline_file.name, naming_mapping)
    exam_topics = None
    exam_key = lecture_num or lecture_number
    
    if exam_key and exam_key in exam_guide:
        exam_topics = exam_guide[exam_key].get("full_description")
        if exam_topics:
            philosopher = exam_guide[exam_key].get("philosopher", "")
            print(f"  ✓ Using focused exam topics ({philosopher})")
    
    # Generate notes using OpenAI
    print(f"  🤖 Generating notes with OpenAI...")
    notes = generate_lecture_notes(outline_text, readings_texts, transcript_text, exam_topics)
    
    # Save notes
    output_filename = parse_output_filename(outline_file.name, naming_mapping)
    output_path = notes_dir / output_filename
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(notes)
    
    print(f"  ✓ Notes saved to: {output_path}")
    
    # Generate PDF if requested
    if generate_pdf:
        print(f"\nGenerating PDF...")
        from generate_pdfs import markdown_to_pdf_quarto
        pdf_file = Path("lecture-notes-pdf") / (output_path.stem + ".pdf")
        pdf_file.parent.mkdir(parents=True, exist_ok=True)
        lecture_name = output_path.stem.replace("-", " ").title()
        success = markdown_to_pdf_quarto(output_path, pdf_file, title=lecture_name)
        if success:
            print(f"  ✓ PDF saved to: {pdf_file}")
        else:
            print(f"  ✗ Failed to generate PDF")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate notes for a single lecture")
    parser.add_argument(
        "lecture_number",
        type=str,
        help="Lecture number (e.g., '21')"
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also generate PDF"
    )
    
    args = parser.parse_args()
    generate_single_lecture(args.lecture_number, generate_pdf=args.pdf)

