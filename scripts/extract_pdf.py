import os
import json
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    print(f"Processing PDF: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def process_insurance_pdfs(pdf_dir="data/pdfs"):
    """Process all insurance PDF files in the directory"""
    # Create output directory if it doesn't exist
    os.makedirs("data/raw_text", exist_ok=True)
    
    # Check if PDF directory exists
    if not os.path.exists(pdf_dir):
        print(f"PDF directory {pdf_dir} not found. Creating it...")
        os.makedirs(pdf_dir, exist_ok=True)
        print(f"Please place insurance PDFs in the {pdf_dir} directory and run again.")
        return []
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}. Please add some PDFs and run again.")
        return []
    
    extracted_docs = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        
        if text:
            doc = {
                "source": pdf_file,
                "content": text,
                "type": "pdf"
            }
            extracted_docs.append(doc)
    
    # Save extracted text
    if extracted_docs:
        with open("data/raw_text/insurance_docs.json", "w", encoding="utf-8") as f:
            json.dump(extracted_docs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Extracted text from {len(extracted_docs)} PDF documents.")
    
    return extracted_docs

if __name__ == "__main__":
    process_insurance_pdfs() 