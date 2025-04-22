import json
import os
from typing import List, Dict

def load_raw_docs() -> List[Dict]:
    """Load the raw text extracted from PDFs"""
    docs = []
    
    # Load PDF docs if they exist
    pdf_docs_path = "data/raw_text/insurance_docs.json"
    if os.path.exists(pdf_docs_path):
        try:
            with open(pdf_docs_path, "r", encoding="utf-8") as f:
                pdf_docs = json.load(f)
                docs.extend(pdf_docs)
            print(f"Loaded {len(pdf_docs)} PDF documents")
        except Exception as e:
            print(f"Error loading PDF documents: {e}")
    
    if not docs:
        print("No documents found. Please run PDF extraction first.")
        
    return docs

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks

def process_documents():
    """Process raw documents into chunks with metadata"""
    os.makedirs("data/processed", exist_ok=True)
    docs = load_raw_docs()
    processed_chunks = []

    for doc in docs:
        source = f"pdf:{doc['source']}"
        content = doc["content"]
            
        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "chunk_id": f"{i}_{source}",
                "text": chunk,
                "source": source,
                "doc_type": "pdf",
                "chunk_index": i
            })

    if processed_chunks:
        with open("data/processed/chunks.json", "w", encoding="utf-8") as f:
            json.dump(processed_chunks, f, indent=2, ensure_ascii=False)

        print(f"✅ Processed {len(processed_chunks)} chunks from {len(docs)} documents")
    else:
        print("No chunks were created. Please check the input documents.")

if __name__ == "__main__":
    process_documents()