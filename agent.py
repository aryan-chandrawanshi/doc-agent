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
    Choose the best format: 'docx' (reports), 'xlsx' (spreadsheets), 'pptx' (presentations) or 'pdf' (reports/articles).

    CRITICAL IMAGE RULE: You must provide THREE keys for every image:
    1. "search_term": A highly specific phrase.
    2. "fallback_search_term": A broader generic term.
    3. "image_type": Must be exactly "factual" (for specific historical or current figures, locations, or encyclopedic subjects) OR "stock" (for abstract concepts, generic items, or corporate metaphors).

    If 'pptx', output EXACTLY this structure:
    {   "filename": "[short relevant filename with numbers and without file extensions]"
        "format": "pptx",
        "title": "Presentation Title",
        "slides": [
            {
                "type": "content_slide",
                "title": "Slide Heading",
                "bullets": ["Key point 1", "Key point 2"],
                "search_term": "Roberto Carlos Brazil 2002",
                "fallback_search_term": "Football player kicking",
                "image_type": "factual"
            }
        ]
    }
    
    If 'docx' OR 'pdf' , output EXACTLY this structure:
    {   "filename": "[short relevant filename with numbers and without file extensions]"
        "format": "docx", # OR "pdf" depending on choice,
        "title": "Document Title",
        "content": [
            {"type": "heading", "text": "Section Heading"},
            {"type": "paragraph", "text": "Detailed paragraph text..."},
            {"type": "image", "search_term": "Specific Phrase", "fallback_search_term": "Broader Category", "image_type": "stock"}
        ]
    }


    If 'xlsx', you must dynamically adapt the 'headers' array and 'rows' arrays to construct EXACTLY what the user asks for. Whether the user wants a financial data summary, an inventory tracker, or a complex weekly timetable (e.g., Days in Column A, Periods in headers), map it directly to this 2D grid structure.
    Output EXACTLY this structure:
    {   "filename": "[short relevant filename with numbers and without file extensions]"
        "format": "xlsx",
        "title": "Workbook Title",
        "sheets": [
            {
                "sheet_name": "Sheet 1 Name",
                "headers": ["Top Left Blank or Header", "Column 2 Header", "Column 3 Header"],
                "rows": [
                    ["Row 1 Identifier (e.g., Monday)", "Data B", "Data C"],
                    ["Row 2 Identifier (e.g., Tuesday)", "Data E", "Data F"]
                ]
            }
        ]
    }
    """
    

    print("Agent is thinking and structuring the document...")
    
    try:
        # 4. Call the new API structure
        response = client.models.generate_content(
            model='gemini-3-flash-preview', # Upgraded to the modern flash model
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