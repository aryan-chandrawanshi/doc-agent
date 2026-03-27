import openpyxl

def create_excel_file(data, filename="output.xlsx"):
    """Takes JSON data and builds a formatted Excel spreadsheet."""
    print(f"Drafting Excel spreadsheet: {filename}...")
    
    # Create a blank workbook and select the active sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Set the sheet tab name (Excel limits this to 31 characters)
    title = data.get("title", "Data Tracker")
    ws.title = title[:31] 
    
    # 1. Insert the Headers into the first row
    headers = data.get("headers", [])
    ws.append(headers)
    
    # 2. Insert all the data rows beneath the headers
    rows = data.get("rows", [])
    for row in rows:
        ws.append(row)
        
    # Save the file to your hard drive
    wb.save(filename)
    print("Excel spreadsheet complete!")