import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load the API key from your .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: Could not find GEMINI_API_KEY. Check your .env file.")
    exit()

# 2. Initialize the new Client
client = genai.Client(api_key=api_key)

def generate_document_plan(brief):
    """Sends the brief to Gemini and gets a structured JSON document plan back."""
    
    # 3. The Master Prompt
    system_instruction = """
    You are an expert AI document creation agent. Analyze the user's brief and plan a document.
    You MUST output strict, valid JSON. 
    Choose the best format: 'docx' (reports), 'xlsx' (spreadsheets), 'pptx' (presentations).

    CRITICAL IMAGE RULE: We use Wikipedia to source real images. For any image, provide a "search_term" that is a highly specific, 1-3 word noun that perfectly matches the section (e.g., "Espresso machine", "Solar panel", "Mars rover").

    If 'docx', output EXACTLY this structure:
    {   "filename": "[short relevant filename with numbers and without file extensions]"
        "format": "docx",
        "title": "Document Title",
        "content": [
            {"type": "heading", "text": "Section Heading"},
            {"type": "paragraph", "text": "Detailed paragraph text..."},
            {"type": "image", "search_term": "Specific Noun"},
            {"type": "bullet_list", "items": ["point 1", "point 2"]}
        ]
    }

    If 'pptx', output EXACTLY this structure:
    {   "filename": "[short relevant filename with numbers and without file extensions]"
        "format": "pptx",
        "title": "Presentation Title",
        "slides": [
            {
                "type": "title_slide",
                "title": "Main Deck Title",
                "subtitle": "Presented by AI"
            },
            {
                "type": "content_slide",
                "title": "Slide Heading",
                "bullets": ["Key point 1", "Key point 2"],
                "search_term": "Specific Noun" 
            }
        ]
    }

    If 'xlsx', output EXACTLY this structure:
    {   "filename": "[short relevant filename with numbers and without file extensions]"
        "format": "xlsx",
        "title": "Spreadsheet",
        "headers": ["Col 1", "Col 2"],
        "rows": [["Data 1", "Data 2"]]
    }
    """

    print("Agent is thinking and structuring the document...")
    
    try:
        # 4. Call the new API structure
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Upgraded to the modern flash model
            contents=brief,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )
        # Parse the text response into a Python dictionary
        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred while talking to Gemini: {e}")
        return None

# --- Quick Test Block ---
if __name__ == "__main__":
    test_brief = "Create a 2-slide presentation about cats."
    plan = generate_document_plan(test_brief)
    
    print("\n--- Gemini Output ---")
    print(json.dumps(plan, indent=2))