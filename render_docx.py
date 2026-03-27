import docx
import urllib.request
import os
from docx.shared import Inches

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
                
        # --- NEW IMAGE LOGIC ---
        elif item["type"] == "image":
            image_url = item.get("url")
            if image_url:
                print(f" -> Downloading image: {image_url}")
                try:
                    # Download the image temporarily
                    urllib.request.urlretrieve(image_url, "temp_img.jpg")
                    # Insert into Word doc (making it 5 inches wide to fit nicely)
                    doc.add_picture("temp_img.jpg", width=Inches(5))
                    # Delete the temporary file from your PC
                    os.remove("temp_img.jpg")
                except Exception as e:
                    print(f" -> Could not add image: {e}")
                    doc.add_paragraph(f"[Image Placeholder: {item.get('alt')}]")
                
    doc.save(filename)
    print("Word document complete!")