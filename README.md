# Happiness Notes Generator

Automatically generates comprehensive, exam-focused lecture notes from lecture outlines and readings using OpenAI's GPT-5.1 model.

## Quick Start

### Setup (One-time)

1. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

2. **Configure API key:**
   Create `.env` file with:
   ```
   OPENAI_API_KEY=your_key_here
   ```

3. **Install Quarto for PDF generation (optional):**
   ```bash
   brew install --cask quarto
   ```

### Generate Everything

```bash
uv run python src/main.py --pdf
```

This single command will:
- ✅ Convert all .docx outlines to .txt
- ✅ Convert all .pdf readings to .txt  
- ✅ Generate exam-focused lecture notes (20 markdown files)
- ✅ Create individual PDFs for each lecture
- ✅ Create master combined PDF with all lectures

### Other Commands

**Generate notes only:**
```bash
uv run python src/main.py
```

**Generate PDFs only:**
```bash
uv run python src/generate_pdfs.py
```

## Project Structure

```
happiness-notes/
├── data/
│   ├── lecture-outlines-docx/     # INPUT: Original .docx outlines
│   ├── lecture-outlines-txt/      # Generated: Converted outlines
│   ├── readings-pdf/              # INPUT: Original .pdf readings
│   ├── readings-txt/              # Generated: Converted readings
│   └── lecture-transcripts/       # INPUT (optional): Audio transcripts
├── lecture-notes/                 # OUTPUT: Markdown notes
├── lecture-notes-pdf/             # OUTPUT: PDF notes
├── mapping/                       # Configuration files
│   ├── lecture-naming.json        # Output filename mappings
│   └── exam-study-guide.json      # Exam topics for focused notes
├── src/                           # Source code
│   ├── main.py                    # Main pipeline
│   ├── generate_pdfs.py           # PDF generation
│   ├── convert_outlines.py        # DOCX → TXT
│   ├── convert_readings.py        # PDF → TXT
│   └── generate_notes.py          # Notes with OpenAI
└── .env                           # API key (not in git)
```

## How It Works

### Lecture-to-Reading Mapping

All outlines use **number prefix matching**:
- Example: "1 Plato Lecture Outline.docx" → matches "1 Plato - The Republic (selection).pdf"
- The system automatically finds all readings that start with the same number prefix

### Output Naming

Generated notes use a **number-author** format defined in `mapping/lecture-naming.json`:
- "1 Plato Lecture Outline.docx" → `1-plato.md`
- "2 Aristotle Lecture Outline.docx" → `2-aristotle.md`
- "11 Sartre Outline.docx" → `11-sartre.md`

### Note Generation

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

### Parallel Processing

The system processes up to 10 lectures simultaneously for faster generation.

### Optional Lecture Transcripts

If you add lecture transcripts to `data/lecture-transcripts/`, they will be automatically included in note generation. The transcript filename should match the outline filename (e.g., "1 Plato Lecture Outline.txt").

## Customization

### Change Output Filenames

Edit `mapping/lecture-naming.json`:
```json
{
  "1 Plato Lecture Outline.docx": "1-plato.md",
  "7 Buddhism Lecture Outline.docx": "7-buddha.md"
}
```

### Change Exam Focus Topics

Edit `mapping/exam-study-guide.json`:
```json
{
  "1": {
    "philosopher": "Plato",
    "exam": "Exam 1",
    "full_description": "Topics to focus on..."
  }
}
```

## What Gets Generated

### Intermediate Files
- `data/lecture-outlines-txt/` - Converted text outlines
- `data/readings-txt/` - Converted text readings

### Final Output
- `lecture-notes/` - Markdown lecture notes
  - `1-plato.md`, `2-aristotle.md`, etc.
  
- `lecture-notes-pdf/` - PDF lecture notes
  - `1-plato.pdf`, `2-aristotle.pdf`, etc.
  - `00-all-lectures-combined.pdf` (master PDF with all lectures)

After running the pipeline, you'll have:
- 20 converted outlines in `data/lecture-outlines-txt/`
- 25 converted readings in `data/readings-txt/`
- 20 lecture notes in `lecture-notes/`
- 20 PDFs + 1 master PDF in `lecture-notes-pdf/`

All conversions and notes are regenerated on each run to ensure they're up-to-date.

## Individual Steps

**Convert outlines only:**
```bash
uv run python src/convert_outlines.py
```

**Convert readings only:**
```bash
uv run python src/convert_readings.py
```

## Adding New Lectures

1. Add `.docx` outline to `data/lecture-outlines-docx/` with a number prefix (e.g., "21 New Topic Outline.docx")
2. Add corresponding `.pdf` readings to `data/readings-pdf/` with matching number prefix
3. Add entry to `mapping/lecture-naming.json` for custom output filename
4. Add entry to `mapping/exam-study-guide.json` for exam topics
5. Run `uv run python src/main.py --pdf`

## Troubleshooting

**Issue**: "Model not found" error
- **Solution**: Ensure your OpenAI API key has access to GPT-5.1

**Issue**: Missing readings
- **Solution**: Verify your outline files have number prefixes that match reading files

**Issue**: Slow processing
- **Solution**: The system already uses parallel processing (10 simultaneous requests). For faster processing, ensure good internet connection.

**Issue**: PDF generation fails
- **Solution**: Ensure Quarto is installed (`brew install --cask quarto`)

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
