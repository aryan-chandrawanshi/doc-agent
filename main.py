import agent
import render_docx
import render_xlsx
import render_pptx
import json

def main():
    print("========================================")
    print("  Gemini AI Document Generator (MVP) ")
    print("========================================")
    print("Type 'quit' or 'exit' at any time to stop.\n")

    # 1. Get the initial request
    brief = input("Enter your document brief: ")

    while True:
        if brief.lower() in ['quit', 'exit']:
            break

        # 2. Get the structured plan from Gemini
        plan = agent.generate_document_plan(brief)

        if not plan:
            print("Failed to generate a plan. Please try again.")
            brief = input("\nEnter your document brief: ")
            continue

        # Show the user a quick summary of what the AI decided to build
        print("\n--- AI Document Plan ---")
        print(f"Format chosen: {plan.get('format', 'unknown').upper()}")
        print(f"Title: {plan.get('title', 'Untitled')}")
        print(f"File name saved as: {plan.get('filename', 'output')}.{plan.get('format','unknown')}")
        print("------------------------")

        # 3. Route to the correct renderer based on the AI's format choice
        # 3. Route to the correct renderer
        doc_format = plan.get("format", "").lower()
        file_name = plan.get("filename", '').lower()
        
        if doc_format == "docx":
            render_docx.create_word_doc(plan, f"{file_name}.docx")
        elif doc_format == "xlsx":
            render_xlsx.create_excel_file(plan, f"{file_name}.xlsx")
        elif doc_format == "pptx":
            render_pptx.create_ppt_file(plan, f"{file_name}.pptx")
        elif doc_format == "pdf":
            print("PDF rendering requested! (Code coming soon)")
            # render_pdf.create_pdf_file(plan, "output.pdf")
        else:
            print(f"Error: Unknown format requested by AI: {doc_format}")

        # 4. The Revision Loop
        print("\nDone! Check your project folder for the output file.")
        feedback = input("\nDoes this look right, or do you need revisions? \n(Type 'looks good' to finish, or enter your revision instructions): ")
        
        if feedback.lower() in ['looks good', 'good', 'done', 'yes', 'y', 'quit', 'exit']:
            print("Great! Enjoy your document.")
            break
        else:
            print("\nSending revision instructions to Gemini...")
            # We bundle the original context, the current JSON, and the new instructions together
            brief = f"Original brief: {brief}\n\nCurrent Draft JSON:\n{json.dumps(plan)}\n\nUser Revision Request: {feedback}\n\nPlease output the completely UPDATED JSON."

if __name__ == "__main__":
    main()