models that be changed if daily limit runs out (in agent.py):
gemini-3.1-flash-lite-preview
gemini-2.5-flash
gemini-3-flash-preview


***VIBECODED USING GEMINI PRO 3.1***


This is a document generating model which was made during an AI hackathon.

It generates 3 types of documents - pptx, xslx and docx based on user prompt.

The agent.py module calls a Gemini model to generate:
i) JSON formatted text which is used for generating the corresponding document
ii) search keywords for images which are fetched using url request in corresponding document-renderers,
In the first draft, wikipedia was used for images. Using wikipedia has the advantage of authentic high quality images for specific nouns, but fails for specific phrases 
In second draft, pexels was used for image fetching, for generic images in case wikipedia fails. This ensures some relevent image is inserted in every slide.  

The formatted JSON is sent to either of three modules:
render_pptx.py: Uses pptx python library to convert the JSON into .pptx file, render_docx.py : Uses docx library for generating .docx and render_xlsx.py : Uses openpxyl for .xlsx 
in this advanced-engine branch, added render_pdf too, but as with docx generation since such article type documents generally require contexted and related images to the text, so image added to pdf or docx generated may not feel perfectly matching, 
The agent is run using main.py which provides a simple text interface and produces the file in the 
