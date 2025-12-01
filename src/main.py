"""
Main orchestration script for generating happiness lecture notes.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import our modules
from convert_outlines import convert_all_outlines
from convert_readings import convert_all_readings
from generate_notes import (
    generate_lecture_notes,
    parse_output_filename,
    load_text_file,
    get_matching_readings,
    load_lecture_naming,
    load_exam_guide
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


def process_lecture(
    outline_file: Path,
    readings_dir: Path,
    transcripts_dir: Path,
    output_dir: Path,
    naming_mapping: dict[str, str],
    exam_guide: dict
) -> bool:
    """
    Process a single lecture: gather materials and generate notes.
    
    Args:
        outline_file: Path to the lecture outline .txt file
        readings_dir: Directory containing reading .txt files
        transcripts_dir: Directory containing lecture transcript .txt files
        output_dir: Directory where notes will be saved
        naming_mapping: Mapping from outline filenames to output filenames
        exam_guide: Exam study guide with topics for each lecture
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\nProcessing: {outline_file.name}")
        
        # Load outline
        outline_text = load_text_file(outline_file)
        if not outline_text:
            print(f"  ✗ Could not load outline")
            return False
        
        # Get matching readings
        readings_texts = get_matching_readings(
            outline_file.name,
            readings_dir
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
        exam_key = lecture_num
        
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
        output_path = output_dir / output_filename
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        print(f"  ✓ Notes saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {outline_file.name}: {e}")
        return False


def main(generate_pdfs: bool = False):
    """
    Main function to orchestrate the entire pipeline.
    
    Args:
        generate_pdfs: If True, generate PDFs after creating markdown notes
    """
    print("=" * 70)
    print("HAPPINESS LECTURE NOTES GENERATOR")
    print("=" * 70)
    
    # Define paths
    outlines_docx_dir = Path("data/lecture-outlines-docx")
    outlines_txt_dir = Path("data/lecture-outlines-txt")
    readings_pdf_dir = Path("data/readings-pdf")
    readings_txt_dir = Path("data/readings-txt")
    transcripts_dir = Path("data/lecture-transcripts")
    notes_dir = Path("lecture-notes")
    
    # Step 1: Convert outlines
    print("\n" + "=" * 70)
    print("STEP 1: Converting lecture outlines (.docx → .txt)")
    print("=" * 70)
    convert_all_outlines(
        input_dir=str(outlines_docx_dir),
        output_dir=str(outlines_txt_dir)
    )
    
    # Step 2: Convert readings
    print("\n" + "=" * 70)
    print("STEP 2: Converting readings (.pdf → .txt)")
    print("=" * 70)
    convert_all_readings(
        input_dir=str(readings_pdf_dir),
        output_dir=str(readings_txt_dir)
    )
    
    # Step 3: Load configuration
    print("\n" + "=" * 70)
    print("STEP 3: Loading configuration")
    print("=" * 70)
    print("Loading lecture naming mapping...")
    naming_mapping = load_lecture_naming()
    if naming_mapping:
        print(f"✓ Loaded {len(naming_mapping)} lecture name mapping(s)")
    else:
        print("⚠ No naming mapping found (will use default naming)")
    
    print("\nLoading exam study guide...")
    exam_guide = load_exam_guide()
    if exam_guide:
        print(f"✓ Loaded exam topics for {len(exam_guide)} lecture(s)")
        print("  Notes will focus on exam-relevant topics only")
    else:
        print("⚠ No exam guide found (will generate comprehensive notes)")
    
    # Step 4: Generate notes for each lecture
    print("\n" + "=" * 70)
    print("STEP 4: Generating lecture notes")
    print("=" * 70)
    
    # Check if outline directory exists
    if not outlines_txt_dir.exists():
        print(f"Error: Outline directory not found: {outlines_txt_dir}")
        sys.exit(1)
    
    # Get all outline files
    outline_files = sorted(outlines_txt_dir.glob("*.txt"))
    
    if not outline_files:
        print(f"No outline files found in {outlines_txt_dir}")
        sys.exit(1)
    
    print(f"\nFound {len(outline_files)} lecture outline(s) to process")
    print("Processing lectures in parallel (up to 10 simultaneous requests)...\n")
    
    # Process lectures in parallel with ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                process_lecture,
                outline_file,
                readings_txt_dir,
                transcripts_dir,
                notes_dir,
                naming_mapping,
                exam_guide
            ): outline_file
            for outline_file in outline_files
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            outline_file = future_to_file[future]
            try:
                success = future.result()
                results.append((outline_file.name, success))
            except Exception as e:
                print(f"  ✗ Unexpected error processing {outline_file.name}: {e}")
                results.append((outline_file.name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nCompleted: {successful}/{total} lecture notes generated successfully")
    
    if successful < total:
        print("\nFailed lectures:")
        for name, success in results:
            if not success:
                print(f"  - {name}")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)
    
    # Generate PDFs if requested
    if generate_pdfs:
        print("\n")
        try:
            from generate_pdfs import generate_all_pdfs
            generate_all_pdfs()
        except Exception as e:
            print(f"Error generating PDFs: {e}")
            print("You can generate PDFs manually with: uv run python src/generate_pdfs.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate happiness lecture notes")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also generate PDFs after creating markdown notes"
    )
    args = parser.parse_args()
    
    main(generate_pdfs=args.pdf)

