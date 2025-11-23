# Happiness Notes Generator - Usage Guide

## Overview

This project automatically generates comprehensive lecture notes from lecture outlines and readings using OpenAI's GPT-5.1 model with low reasoning effort.

## Project Structure

```
happiness-notes/
├── data/
│   ├── lecture-outlines-docx/     # Input: .docx lecture outlines
│   ├── lecture-outlines-txt/      # Generated: converted .txt outlines
│   ├── readings-pdf/              # Input: .pdf readings
│   ├── readings-txt/              # Generated: converted .txt readings
│   └── lecture-transcripts/       # Optional: .txt lecture transcripts
├── lecture-notes/                 # Output: generated .md lecture notes
├── src/                          # Source code
│   ├── convert_outlines.py       # Converts .docx to .txt
│   ├── convert_readings.py       # Converts .pdf to .txt
│   ├── generate_notes.py         # Generates notes with OpenAI
│   └── main.py                   # Main orchestration script
├── mapping.json                  # Custom mapping for unnumbered outlines
├── pyproject.toml               # Project dependencies
└── .env                         # API keys (not in git)
```

## Setup

1. **Install dependencies** (using uv):
   ```bash
   uv pip install -e .
   ```

2. **Configure OpenAI API key**:
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Run the Full Pipeline

**Generate all lecture notes:**

```bash
uv run python src/main.py
```

This will:
1. Convert all lecture outlines (.docx → .txt)
2. Convert all readings (.pdf → .txt)
3. Generate lecture notes for each outline (in parallel, up to 10 simultaneous requests)
4. Save notes as .md files in `lecture-notes/`

**Generate lecture notes AND PDFs in one command:**

```bash
uv run python src/main.py --pdf
```

This will run the full pipeline and then automatically generate PDFs.

**Generate PDFs only (after notes are already created):**

```bash
uv run python src/generate_pdfs.py
```

This will:
1. Generate individual PDF for each markdown note
2. Create a master PDF combining all lectures with table of contents
3. Save PDFs in `lecture-notes-pdf/`
   - Individual PDFs: `1-plato.pdf`, `2-aristotle.pdf`, etc.
   - Master PDF: `00-all-lectures-combined.pdf`

**Requirements for PDF generation:**
- `quarto` (install: `brew install --cask quarto`)
- Quarto includes all necessary dependencies for PDF generation

### Run Individual Steps

**Convert outlines only:**
```bash
uv run python src/convert_outlines.py
```

**Convert readings only:**
```bash
uv run python src/convert_readings.py
```

## How It Works

### Lecture-to-Reading Mapping

1. **Numbered outlines** (e.g., "1 Plato Lecture Outline.docx"):
   - Automatically matches all readings with the same number prefix
   - Example: "1 Plato Lecture Outline" → "1 Plato - The Republic (selection).pdf"

2. **Unnumbered outlines** (e.g., "Lyubomirsky Outline 2025.docx"):
   - Uses custom mapping defined in `mapping.json`

### Output Naming

Generated notes use a **number-author** format defined in `lecture-naming.json`:
- "1 Plato Lecture Outline.docx" → `1-plato.md`
- "2 Aristotle Lecture Outline.docx" → `2-aristotle.md`
- "3 Epictetus (Stoicism) Outline.docx" → `3-epictetus.md`
- "7 Buddhism Lecture Outline.docx" → `7-buddha.md`
- "Tao Te Ching Outline.docx" → `9-laozi.md`
- "Zhuangzi Outline.docx" → `10-zhuangzi.md`
- "Lyubomirsky Outline 2025.docx" → `11-lyubomirsky.md`

All lectures now have number prefixes. You can customize the output filenames by editing `lecture-naming.json`.

### Parallel Processing

The system processes up to 10 lectures simultaneously for faster generation. This significantly reduces total processing time when generating multiple lecture notes.

### Optional Lecture Transcripts

If you add lecture transcripts to `data/lecture-transcripts/`, they will be automatically included in note generation. The transcript filename should match the outline filename (e.g., "1 Plato Lecture Outline.txt").

## Customizing Mappings

### Reading Mappings

Edit `mapping.json` to add custom outline-to-reading mappings:

```json
{
  "Outline Filename.docx": [
    "Reading 1.pdf",
    "Reading 2.pdf"
  ]
}
```

### Output Filename Mappings

Edit `lecture-naming.json` to customize output filenames (number-author format):

```json
{
  "1 Plato Lecture Outline.docx": {
    "number": "1",
    "author": "Plato",
    "output_filename": "1-plato.md"
  }
}
```

This allows you to:
- Control the exact output filename for each lecture
- Use author names instead of text/tradition names
- Maintain consistent naming conventions

## Note Generation

Notes are generated using:
- **Model**: GPT-5.1
- **Reasoning effort**: Medium
- **Purpose**: Concise, exam-focused notes for busy students
- **Format**: Markdown (.md)

Each note includes:
- All key concepts from the outline
- Relevant passages from readings
- Clear structure with headings
- Connections between ideas
- Important quotes when relevant

## Troubleshooting

**Issue**: "Model not found" error
- **Solution**: Ensure your OpenAI API key has access to GPT-5.1

**Issue**: Missing readings
- **Solution**: Check `mapping.json` for unnumbered outlines, or verify number prefixes match

**Issue**: Slow processing
- **Solution**: The system already uses parallel processing (10 simultaneous requests). For faster processing, ensure good internet connection.

## Adding New Lectures

1. Add `.docx` outline to `data/lecture-outlines-docx/`
2. Add corresponding `.pdf` readings to `data/readings-pdf/`
3. If the outline is unnumbered, update `mapping.json`
4. Run `uv run python src/main.py`

## Files Generated

After running the pipeline, you'll have:
- 11 converted outlines in `data/lecture-outlines-txt/`
- 25 converted readings in `data/readings-txt/`
- 11 lecture notes in `lecture-notes/`

All conversions and notes are regenerated on each run to ensure they're up-to-date.

