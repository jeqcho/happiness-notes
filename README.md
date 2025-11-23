# Get lecture transcripts
Given lecture-recordings/, which has audio files, transcribe each to .txt files in lecture-transcripts/

# Get lecture outlines
Given lecture-outlines-docx/, which has .docx files, transcribe each to .txt files in lecture-outlines-txt/. Depending on your strategy, you could try converting it to .pdf first.

# Get readings
Given readings-pdf/, which has .pdf files, transcribe each to .txt files in readings-txt/

# Get notes
This is the whole point of the repo. We will combine the following three inputs:
- lecture outline (.txt) in lecture-outlines-txt/
- readings (.txt) in readings-txt/
- lecture transcripts (.txt) in lecture-transcripts/
to generate the notes
- notes (.md) in lecture-notes/

Notes should be concise and comprehensive. Tailor it to a student with limited time but needs to know everything that is relevant to that lecture.

All code should be written in src/. You can use OpenAI models to do the audio transcription and the note generation. For note generation, use `gpt-5.1` with reasoning effort `medium`. Read https://platform.openai.com/docs for docs and use the Responses API. API key is in .env.

Use uv.

# Generate PDFs
After generating notes, you can create PDFs using Quarto:
```bash
uv run python src/generate_pdfs.py
```

Or generate notes and PDFs in one command:
```bash
uv run python src/main.py --pdf
```

**Requires:** Quarto (`brew install --cask quarto`)