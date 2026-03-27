import docx
from docx.shared import Inches
import urllib.request
import urllib.parse
import json
import os
import time

# A custom User-Agent badge so Wikipedia knows we are a friendly bot
CUSTOM_HEADERS = {'User-Agent': 'GeminiDocAgent/1.0 (LearningProject; friendly-bot)'}

def get_wiki_image_url(search_term):
    """Searches Wikipedia and returns the URL of the top image."""
    encoded_term = urllib.parse.quote(search_term)
    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrlimit=1&prop=pageimages&piprop=thumbnail&pithumbsize=800&format=json"
    
    try:
        req = urllib.request.Request(url, headers=CUSTOM_HEADERS)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for page_id in pages:
                if "thumbnail" in pages[page_id]:
                    return pages[page_id]["thumbnail"]["source"]
    except Exception as e:
        pass
    return None

def create_word_doc(data, filename="output.docx"):
    """Takes JSON data and builds a formatted Word document."""
    print(f"Drafting Word document: {filename}...")
    
    doc = docx.Document()
    
    title = data.get("title", "AI Generated Report")
    doc.add_heading(title, 0)
    
    for item in data.get("content", []):
        if item["type"] == "heading":
            doc.add_heading(item["text"], level=1)
            
        elif item["type"] == "paragraph":
            doc.add_paragraph(item["text"])
            
        elif item["type"] == "bullet_list":
            for point in item["items"]:
                doc.add_paragraph(point, style='List Bullet')
                
        # --- NEW: Wikipedia Image Sourcing ---
        elif item["type"] == "image":
            search_term = item.get("search_term")
            
            if search_term:
                print(f" -> Searching Wikipedia for: '{search_term}'")
                img_url = get_wiki_image_url(search_term)
                
                if img_url:
                    try:
                        # Polite pause to avoid rate limits
                        time.sleep(1.5)
                        
                        req = urllib.request.Request(img_url, headers=CUSTOM_HEADERS)
                        with urllib.request.urlopen(req) as response, open("temp_doc_img.jpg", 'wb') as out_file:
                            out_file.write(response.read())
                            
                        # Insert into Word doc (making it 5 inches wide to fit nicely)
                        doc.add_picture("temp_doc_img.jpg", width=Inches(5))
                        os.remove("temp_doc_img.jpg")
                    except Exception as e:
                        print(f" -> Could not add image: {e}")
                        doc.add_paragraph(f"[Image Placeholder: {search_term}]")
                else:
                    print(f" -> No image found on Wikipedia for '{search_term}'")
                    doc.add_paragraph(f"[Image intended: {search_term}]")
                    
    doc.save(filename)
    print("Word document complete!")