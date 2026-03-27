from pptx import Presentation
from pptx.util import Inches, Pt
import urllib.request
import urllib.parse
import json
import os
import time  # <-- NEW: We need this to pause between requests

# NEW: A custom User-Agent badge so Wikipedia knows we are a friendly bot
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

def create_ppt_file(data, filename="output.pptx"):
    print(f"Drafting PowerPoint: {filename}...")
    prs = Presentation()

    slides_data = data.get("slides", [])

    for slide_data in slides_data:
        if slide_data["type"] == "title_slide":
            slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(slide_layout)
            slide.shapes.title.text = slide_data.get("title", "")
            slide.placeholders[1].text = slide_data.get("subtitle", "")

        elif slide_data["type"] == "content_slide":
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)
            
            slide.shapes.title.text = slide_data.get("title", "")

            body_shape = slide.placeholders[1]
            tf = body_shape.text_frame
            tf.word_wrap = True 
            
            search_term = slide_data.get("search_term")
            
            if search_term:
                body_shape.left = Inches(0.5)
                body_shape.width = Inches(4.5)
                body_shape.top = Inches(1.8)
                body_shape.height = Inches(5.0)
                
                print(f" -> Searching Wikipedia for: '{search_term}'")
                img_url = get_wiki_image_url(search_term)
                
                if img_url:
                    try:
                        # --- NEW: The Polite Pause ---
                        # Wait 1.5 seconds before downloading the actual image
                        time.sleep(5.0) 
                        
                        req = urllib.request.Request(img_url, headers=CUSTOM_HEADERS)
                        with urllib.request.urlopen(req) as response, open("temp_ppt_img.jpg", 'wb') as out_file:
                            out_file.write(response.read())
                            
                        slide.shapes.add_picture(
                            "temp_ppt_img.jpg", 
                            left=Inches(5.2),   
                            top=Inches(1.8),    
                            height=Inches(4.5)  
                        )
                        os.remove("temp_ppt_img.jpg")
                    except Exception as e:
                        print(f" -> Could not download image: {e}")
            else:
                body_shape.width = Inches(9.0)

            bullets = slide_data.get("bullets", [])
            for i, bullet in enumerate(bullets):
                if i == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                p.text = bullet
                
                p.font.size = Pt(20)
                p.space_after = Pt(14) 

    prs.save(filename)
    print("PowerPoint complete!")