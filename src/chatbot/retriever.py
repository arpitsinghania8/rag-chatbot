import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, index_path="data/embeddings/docs.index", metadata_path="data/embeddings/chunks_metadata.json"):
        # Check if index exists before loading
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(
                "Index or metadata files not found. Please run the embedding creation step first."
            )
            
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.read_index(index_path)
        
        with open(metadata_path, "r") as f:
            self.chunks = json.load(f)
            
        logger.info(f"Loaded {len(self.chunks)} chunks from metadata")
    
    def get_relevant_chunks(self, query: str, k: int = 5, threshold: float = 0.2):
        """
        Get the most relevant chunks for a query
        
        Args:
            query: The user question
            k: Number of chunks to retrieve
            threshold: Similarity threshold (0-1) for relevance filtering
            
        Returns:
            List of relevant chunk dictionaries
        """
        logger.info(f"Searching for query: '{query}'")
        
        # Encode the query
        query_vector = self.model.encode([query])[0].astype('float32')
        query_vector = np.array([query_vector])
        
        # Get more candidates initially
        k_init = min(k * 3, len(self.chunks))
        distances, indices = self.index.search(query_vector, k_init)
        
        logger.info(f"Retrieved {len(indices[0])} initial chunks")
        
        # Filter results by threshold and prepare results
        relevant_chunks = []
        for i, idx in enumerate(indices[0]):
            # Convert distance to similarity score (0-1)
            # FAISS uses L2 distance, so we need to convert to similarity
            # Lower distance = higher similarity
            distance = distances[0][i]
            # Normalize distance to similarity score between 0-1
            # This is a simple conversion for L2 distance
            similarity = 1 / (1 + distance)
            
            logger.info(f"Chunk {idx} similarity: {similarity:.4f}")
            
            if similarity >= threshold and idx < len(self.chunks):
                chunk = self.chunks[idx]
                chunk["similarity"] = float(similarity)
                relevant_chunks.append(chunk)
                
                # Break if we have enough chunks
                if len(relevant_chunks) >= k:
                    break
        
        # Sort by similarity (highest first)
        relevant_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        
        logger.info(f"Found {len(relevant_chunks)} relevant chunks after filtering")
        
        # Log the first few relevant chunks
        for i, chunk in enumerate(relevant_chunks[:2]):
            logger.info(f"Top chunk {i+1}: similarity={chunk['similarity']:.4f}, source={chunk['source']}")
            logger.info(f"Content preview: {chunk['text'][:100]}...")
        
        # If we don't have enough chunks after filtering, return what we have
        return relevant_chunks[:k] if relevant_chunks else []