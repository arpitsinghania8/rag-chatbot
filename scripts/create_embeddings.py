import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

def create_embeddings():
    """Create and save embeddings using FAISS"""
    # Load processed chunks
    with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    # Initialize the embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # Save the index and metadata
    os.makedirs("data/embeddings", exist_ok=True)
    faiss.write_index(index, "data/embeddings/docs.index")
    
    with open("data/embeddings/chunks_metadata.json", "w") as f:
        json.dump(chunks, f, indent=2)
    
    print("✅ Created and saved embeddings")

if __name__ == "__main__":
    create_embeddings()