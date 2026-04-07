from pptx import Presentation
from pptx.util import Inches, Pt
import urllib.request
import json
import os
import time 
from ddgs import DDGS# <-- NEW: We need this to pause between requests

# NEW: A custom User-Agent badge so Wikipedia knows we are a friendly bot
CUSTOM_HEADERS = {'User-Agent': 'GeminiDocAgent/1.0 (LearningProject; friendly-bot)'}

def get_web_image_url(search_term):
    """Searches the web via DDGS with a mandatory pre-search pause."""
    print(" -> Pausing 10 seconds to avoid search engine bans...")
    time.sleep(10) 
    try:
        results = DDGS().images(search_term, max_results=1)
        if results and len(results) > 0:
            return results[0].get("image")
    except Exception as e:
        print(f" -> Search error: {e}")
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
                        # Wait 5 seconds before downloading the actual image
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
