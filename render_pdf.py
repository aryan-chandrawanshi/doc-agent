from fpdf import FPDF
import requests
import os
import time
from dotenv import load_dotenv


# 1. Load the keys
load_dotenv()

PEXELS_HEADERS = {
    "Authorization": os.getenv("PEXELS_API_KEY"),
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

WIKI_HEADERS = {
    "User-Agent": "GeminiDocAgent/4.0 (LearningProject; waterfall-engine)"
}

# --- THE 3-TIER WATERFALL IMAGE ENGINE ---

def get_wiki_image_url(search_term, used_urls):
    """Tier 1: Highly factual, encyclopedic images."""
    print(f" -> [Tier 1] Searching Wikipedia for: '{search_term}'")
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_term,
        "gsrlimit": 1, "prop": "pageimages", "piprop": "thumbnail",
        "pithumbsize": 800, "format": "json"
    }
    try:
        response = requests.get(url, params=params, headers=WIKI_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        for page_id in data.get("query", {}).get("pages", {}):
            if "thumbnail" in data["query"]["pages"][page_id]:
                img_url = data["query"]["pages"][page_id]["thumbnail"]["source"]
                if img_url not in used_urls:
                    used_urls.add(img_url)
                    return img_url
    except Exception as e:
        print(f"    Wiki missed: {e}")
    return None


def get_pexels_image_url(search_term, used_urls):
    """Tier 3: The Safety Net. 100% reliable, high-quality stock photography."""
    if not os.getenv("PEXELS_API_KEY"): return None
    print(f" -> [Tier 3] Searching Pexels for: '{search_term}'")
    url = "https://api.pexels.com/v1/search"
    params = {"query": search_term, "per_page": 5} 
    time.sleep(2) 
    try:
        response = requests.get(url, headers=PEXELS_HEADERS, params=params, timeout=10)
        response.raise_for_status() 
        data = response.json()
        if data.get('photos'):
            for photo in data['photos']:
                img_url = photo['src']['large']
                if img_url not in used_urls:
                    used_urls.add(img_url)
                    return img_url
    except Exception as e:
        print(f"    Pexels missed: {e}")
    return None

# --- PDF GENERATOR ---

class PDF(FPDF):
    def footer(self):
        # Position 15mm from bottom
        self.set_y(-15)
        # Using the custom font for the footer as well
        self.set_font("Nunito", "", 8)
        self.set_text_color(128, 128, 128)
        # Add page number
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def create_pdf_file(data, filename="output.pdf"):
    print(f"Drafting PDF document: {filename}...")
    
    # Initialize PDF: Portrait, Millimeters, A4 size
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 2. LOAD YOUR CUSTOM FONT
    # Make sure this exact file is in the same folder as this Python script!
    try:
        pdf.add_font("Nunito", style="", fname="NunitoSans-VariableFont_YTLC,opsz,wdth,wght.ttf")
    except Exception as e:
        print(f" -> Font Error: Could not load Nunito. Is the .ttf file in the folder? Error: {e}")
        return
    
    # Write Title (Using Size and Color instead of bold to differentiate)
    title = data.get("title", "AI Generated Report")
    pdf.set_font("Nunito", "", 24) 
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 15, title, align="C")
    pdf.ln(10)
    
    used_images = set()
    
    for item in data.get("content", []):
        if item["type"] == "heading":
            pdf.set_font("Nunito", "", 16)
            pdf.set_text_color(0, 51, 102) # Dark Blue to make it stand out
            pdf.ln(5)
            pdf.multi_cell(0, 10, item["text"])
            pdf.ln(2)
            
        elif item["type"] == "paragraph":
            pdf.set_font("Nunito", "", 12)
            pdf.set_text_color(0, 0, 0) # Back to Black
            pdf.multi_cell(0, 7, item["text"])
            pdf.ln(2)
            
        elif item["type"] == "bullet_list":
            pdf.set_font("Nunito", "", 12)
            pdf.set_text_color(0, 0, 0)
            for point in item["items"]:
                # The custom font can now safely render real bullet points (•) if the AI generates them!
                # We'll use a standard format just in case.
                bullet_text = point if point.startswith("•") else f"• {point}"
                pdf.multi_cell(0, 7, f"  {bullet_text}")
            pdf.ln(2)
            
        elif item["type"] == "image":
            search_term = item.get("search_term")
            fallback_term = item.get("fallback_search_term")
            image_type = item.get("image_type", "stock") 
            
            if search_term:
                img_url = None
                
                # THE HYBRID ROUTING LOGIC
                if image_type == "factual":
                    img_url = get_wiki_image_url(search_term, used_images)
                
                if not img_url:
                    img_url = get_pexels_image_url(search_term, used_images)
                
                if not img_url and fallback_term:
                    print(f" -> No exact matches. Trying fallback: '{fallback_term}'")
                    img_url = get_pexels_image_url(fallback_term, used_images)
                
                if img_url:
                    try:
                        response = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, stream=True)
                        response.raise_for_status() 

                        with open("temp_pdf_img.jpg", 'wb') as out_file:
                            out_file.write(response.content)
            
                        # Insert into PDF (Width of 170mm centers it nicely on A4)
                        pdf.image("temp_pdf_img.jpg", x=20, w=170)
                        pdf.ln(5)
                        os.remove("temp_pdf_img.jpg")
                        
                    except Exception as e:
                        print(f" -> Could not download image: {e}")
                else:
                    print(f" -> Complete Waterfall Failure. Leaving text space.")
                    
    pdf.output(filename)
    print("PDF document complete!")