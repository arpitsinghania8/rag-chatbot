from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Generator:
    def __init__(self):
        """Initialize a simple generator that doesn't rely on external APIs"""
        pass

    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Generate a response based solely on the retrieved context chunks
        
        This implementation doesn't use any external API and simply returns
        the most relevant chunks formatted as a response.
        
        Args:
            query: The user's question
            context_chunks: List of relevant text chunks with metadata
            
        Returns:
            A response based on the retrieved chunks
        """
        if not context_chunks:
            logger.warning(f"No relevant chunks found for query: '{query}'")
            return "I don't know the answer to that question based on my available information. Please check that your PDFs were properly loaded and processed."
        
        logger.info(f"Generating response for query: '{query}' with {len(context_chunks)} chunks")
        
        # Sort chunks by similarity score (if available)
        if "similarity" in context_chunks[0]:
            context_chunks = sorted(context_chunks, key=lambda x: x.get("similarity", 0), reverse=True)
            logger.info(f"Top chunk similarity: {context_chunks[0].get('similarity', 0)}")
        
        # Format the response
        response = "Based on the available information:\n\n"
        
        # Add the most relevant chunk content
        most_relevant = context_chunks[0]
        response += most_relevant["text"].strip()
        
        # Add sources
        sources = []
        for chunk in context_chunks:
            source = chunk["source"]
            if source not in sources:
                sources.append(source)
        
        if sources:
            response += "\n\nSources:\n"
            for source in sources:
                response += f"- {source}\n"
        
        logger.info(f"Generated response with {len(sources)} sources")
                
        return response