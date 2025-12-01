"""
Generate lecture notes using OpenAI's API.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_exam_guide(guide_file: str = "mapping/exam-study-guide.json") -> dict:
    """
    Load the exam study guide mapping.
    
    Args:
        guide_file: Path to the exam guide JSON file
        
    Returns:
        Dictionary mapping lecture numbers to exam topics
    """
    guide_path = Path(guide_file)
    
    if not guide_path.exists():
        print(f"Warning: Exam guide not found at {guide_file}")
        return {}
    
    try:
        with open(guide_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading exam guide: {e}")
        return {}


def generate_lecture_notes(
    outline_text: str,
    readings_texts: list[str],
    transcript_text: Optional[str] = None,
    exam_topics: Optional[str] = None
) -> str:
    """
    Generate comprehensive lecture notes using OpenAI's API.
    
    Args:
        outline_text: Text content of the lecture outline
        readings_texts: List of text contents from all relevant readings
        transcript_text: Optional text content of the lecture transcript
        exam_topics: Optional specific topics from exam study guide to focus on
        
    Returns:
        Generated lecture notes in markdown format
    """
    # Construct the prompt
    if exam_topics:
        system_prompt = """You are an expert educational assistant helping students prepare for exams on philosophical concepts about happiness. 
Your task is to generate CONCISE, SELF-CONTAINED, exam-oriented lecture notes that cover ONLY the specific topics the student needs to know for the exam.

CRITICAL REQUIREMENTS:
- Keep notes BRIEF and TO THE POINT. Students need concise study materials, not lengthy explanations.
- These notes are SELF-CONTAINED. Students will NOT have access to the original readings.
- Focus on IDEAS, CONCEPTS, ARGUMENTS, and TASK DESCRIPTIONS - these are most important.
- DO NOT cite page numbers (e.g., "439d", "442c") - students won't have the texts.
- DO NOT reference specific passages by location - instead, explain the ideas directly.
- Present the philosophical content in your own clear explanations.

The notes should:
- Focus exclusively on the exam topics provided
- Be well-structured with clear headings matching the exam topics
- Provide explanations, examples, and arguments for each topic - but keep them CONCISE
- Be tailored for students with limited study time who need to master these specific concepts
- Use markdown formatting
- Cover required topics thoroughly but BRIEFLY - no unnecessary elaboration
- Make connections between related concepts when relevant
- Be fully understandable without access to any original readings"""
    else:
        system_prompt = """You are an expert educational assistant helping students understand philosophical concepts about happiness. 
Your task is to generate CONCISE, SELF-CONTAINED lecture notes that help students with limited time grasp essential content.

CRITICAL REQUIREMENTS:
- Keep notes BRIEF and TO THE POINT. Aim for approximately HALF the length you would normally write.
- These notes are SELF-CONTAINED. Students will NOT have access to the original readings.
- Focus on IDEAS, CONCEPTS, and ARGUMENTS - these are most important.
- DO NOT cite page numbers - students won't have the texts.
- DO NOT reference specific passages by location - instead, explain the ideas directly.
- Present the philosophical content in your own clear explanations.

The notes should:
- Be well-structured with clear headings and subheadings
- Cover key concepts, arguments, and ideas from the materials
- Be tailored for busy students who need efficient, focused study materials
- Use markdown formatting
- Be comprehensive but CONCISE - avoid verbose explanations
- Highlight connections between different ideas when relevant
- Be fully understandable without access to any original readings"""

    # Build user message
    user_message_parts = []
    
    if exam_topics:
        user_message_parts.append("Generate focused exam preparation notes that cover ONLY these specific topics:\n\n")
        user_message_parts.append("## EXAM TOPICS TO COVER\n")
        user_message_parts.append(exam_topics)
        user_message_parts.append("\n\nUse the following materials to create comprehensive notes on these topics:\n")
    else:
        user_message_parts.append("Please generate comprehensive lecture notes based on the following materials:\n")
    
    user_message_parts.append("\n## LECTURE OUTLINE\n")
    user_message_parts.append(outline_text)
    
    if readings_texts:
        user_message_parts.append("\n## COURSE READINGS\n")
        for i, reading in enumerate(readings_texts, 1):
            user_message_parts.append(f"\n### Reading {i}\n")
            user_message_parts.append(reading)
    
    if transcript_text:
        user_message_parts.append("\n## LECTURE TRANSCRIPT\n")
        user_message_parts.append(transcript_text)
    
    if exam_topics:
        user_message_parts.append("\n\nGenerate detailed lecture notes in markdown format that focus ONLY on the exam topics listed above. Do not include material not relevant to those topics.")
    else:
        user_message_parts.append("\n\nGenerate concise, comprehensive lecture notes in markdown format.")
    
    user_message = "".join(user_message_parts)
    
    try:
        # Call OpenAI API with GPT-5.1 and medium reasoning effort
        # Note: gpt-5.1 only supports default temperature value
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            reasoning_effort="medium",
        )
        
        notes = response.choices[0].message.content
        return notes
        
    except Exception as e:
        print(f"Error generating notes with OpenAI API: {e}")
        raise


def load_lecture_naming(naming_file: str = "mapping/lecture-naming.json") -> dict[str, str]:
    """
    Load the lecture naming mapping.
    
    Args:
        naming_file: Path to the naming JSON file
        
    Returns:
        Dictionary mapping outline filenames (.docx) to output filenames (.md)
    """
    naming_path = Path(naming_file)
    
    if not naming_path.exists():
        print(f"Warning: Naming file not found at {naming_file}, using default naming")
        return {}
    
    try:
        with open(naming_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading naming file: {e}")
        return {}


def parse_output_filename(outline_filename: str, naming_mapping: dict[str, str] = None) -> str:
    """
    Parse outline filename to generate output filename using naming mapping.
    
    Args:
        outline_filename: Name of the outline file (.txt or .docx)
        naming_mapping: Optional naming mapping dictionary
        
    Returns:
        Output filename in format from mapping, or default format
    """
    if naming_mapping is None:
        naming_mapping = {}
    
    # Normalize to .docx for lookup
    docx_filename = outline_filename.replace(".txt", ".docx")
    
    # Check if we have a mapping
    if docx_filename in naming_mapping:
        return naming_mapping[docx_filename]
    
    # Fallback to old behavior if no mapping found
    name = outline_filename.replace(".txt", "").replace(".docx", "")
    parts = name.split()
    
    if parts and parts[0].isdigit():
        number = parts[0]
        topic_parts = []
        for part in parts[1:]:
            if part.lower() in ["lecture", "outline"]:
                break
            topic_parts.append(part.lower())
        topic = "-".join(topic_parts) if topic_parts else "lecture"
        return f"{number}-{topic}.md"
    else:
        topic_parts = []
        for part in parts:
            if part.lower() in ["lecture", "outline"]:
                break
            topic_parts.append(part.lower())
        topic = "-".join(topic_parts) if topic_parts else "lecture"
        return f"{topic}.md"


def load_text_file(file_path: Path) -> Optional[str]:
    """
    Load text content from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Text content or None if file doesn't exist
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def get_matching_readings(
    outline_filename: str,
    readings_dir: Path
) -> list[str]:
    """
    Get matching reading texts for a given outline using number prefix matching.
    
    Args:
        outline_filename: Name of the outline file (with .txt or .docx extension)
        readings_dir: Directory containing reading .txt files
        
    Returns:
        List of reading text contents
    """
    readings = []
    
    # Extract number prefix (e.g., "1" from "1 Plato Lecture Outline.txt")
    parts = outline_filename.split()
    if parts and parts[0].isdigit():
        number_prefix = parts[0]
        
        # Find all readings starting with this number
        pattern = f"{number_prefix} *.txt"
        for reading_file in readings_dir.glob(pattern):
            text = load_text_file(reading_file)
            if text:
                readings.append(text)
    
    return readings


if __name__ == "__main__":
    # Test with a simple example
    test_outline = "This is a test outline about happiness."
    test_readings = ["Reading 1: Definition of happiness.", "Reading 2: Theories of well-being."]
    
    try:
        notes = generate_lecture_notes(test_outline, test_readings)
        print("Generated notes:")
        print(notes)
    except Exception as e:
        print(f"Test failed: {e}")

