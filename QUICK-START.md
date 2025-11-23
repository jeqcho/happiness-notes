# Happiness Notes - Quick Start Guide

## Setup (One-time)

1. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

2. **Configure API key:**
   - Create `.env` file with: `OPENAI_API_KEY=your_key_here`

3. **Install Quarto for PDF generation (optional):**
   ```bash
   brew install --cask quarto
   ```

## Usage

### Generate Everything (Notes + PDFs)

```bash
uv run python src/main.py --pdf
```

This single command will:
- ✅ Convert all .docx outlines to .txt
- ✅ Convert all .pdf readings to .txt  
- ✅ Generate exam-focused lecture notes (11 markdown files)
- ✅ Create individual PDFs for each lecture (11 PDFs)
- ✅ Create master combined PDF with all lectures

### Generate Notes Only

```bash
uv run python src/main.py
```

### Generate PDFs Only

```bash
uv run python src/generate_pdfs.py
```

## What Gets Generated

### Intermediate Files
- `data/lecture-outlines-txt/` - Converted text outlines (11 files)
- `data/readings-txt/` - Converted text readings (25 files)

### Final Output
- `lecture-notes/` - Markdown lecture notes (11 files)
  - `1-plato.md`, `2-aristotle.md`, etc.
  
- `lecture-notes-pdf/` - PDF lecture notes (12 files)
  - `1-plato.pdf`, `2-aristotle.pdf`, etc. (11 individual PDFs)
  - `00-all-lectures-combined.pdf` (master PDF with all lectures)

## Customization

### Change Output Filenames
Edit `lecture-naming.json`:
```json
{
  "1 Plato Lecture Outline.docx": {
    "output_filename": "1-plato.md"
  }
}
```

### Change Exam Focus Topics
Edit `exam-study-guide-mapping.json`:
```json
{
  "1": {
    "philosopher": "Plato",
    "full_description": "Topics to focus on..."
  }
}
```

### Map Readings to Lectures
Edit `mapping.json` for unnumbered lectures:
```json
{
  "Lyubomirsky Outline 2025.docx": [
    "14 Lyubomirsky The How of Happiness (selection).pdf"
  ]
}
```

## File Structure

```
happiness-notes/
├── data/
│   ├── lecture-outlines-docx/    # INPUT: Original .docx outlines
│   ├── lecture-outlines-txt/     # Generated: Converted outlines
│   ├── readings-pdf/              # INPUT: Original .pdf readings
│   ├── readings-txt/              # Generated: Converted readings
│   └── lecture-transcripts/       # INPUT (optional): Audio transcripts
├── lecture-notes/                 # OUTPUT: Markdown notes
├── lecture-notes-pdf/             # OUTPUT: PDF notes
├── src/                          # Source code
│   ├── main.py                   # Main pipeline
│   ├── generate_pdfs.py          # PDF generation
│   ├── convert_outlines.py       # DOCX → TXT
│   ├── convert_readings.py       # PDF → TXT
│   └── generate_notes.py         # Notes with OpenAI
├── mapping.json                  # Reading mappings
├── lecture-naming.json           # Output filename mappings
└── exam-study-guide-mapping.json # Exam topics for focused notes
```

## Features

✨ **Parallel Processing**: Generates up to 10 notes simultaneously  
✨ **Exam-Focused**: Notes cover only exam-relevant topics from study guide  
✨ **Smart Naming**: Number-author format (e.g., `1-plato.md`)  
✨ **Master PDF**: Combined PDF with table of contents  
✨ **Robust**: Gracefully handles missing files and directories  

## Tips

- Run the full pipeline whenever you add new lectures or update mappings
- The master PDF (`00-all-lectures-combined.pdf`) is great for studying all lectures together
- Individual PDFs are perfect for focusing on specific topics
- Markdown files are searchable and easy to version control

