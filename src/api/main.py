from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import logging
from ..chatbot.retriever import Retriever
from ..chatbot.generator import Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app with CORS
app = FastAPI(title="PDF Knowledge Base API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot components
try:
    retriever = Retriever()
    generator = Generator()
    logger.info("Chatbot components initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing chatbot components: {e}")
    logger.error("Make sure you have run the data processing and embedding scripts.")
    retriever = None
    generator = None

class Query(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str
    sources: list = []
    error: str = None
    debug_info: dict = None

@app.get("/")
async def read_root():
    return {
        "status": "online",
        "message": "PDF Knowledge Base API is running. Send POST requests to /chat endpoint."
    }

@app.post("/chat")
async def chat(query: Query):
    if not query.text or query.text.strip() == "":
        raise HTTPException(status_code=400, detail="Query text cannot be empty")
    
    if not retriever or not generator:
        raise HTTPException(
            status_code=503,
            detail="Chatbot components not initialized. Please check server logs."
        )
    
    try:
        logger.info(f"Received query: '{query.text}'")
        
        # Get relevant context
        context_chunks = retriever.get_relevant_chunks(query.text, threshold=0.2)
        
        # Add debug info
        debug_info = {
            "num_chunks_retrieved": len(context_chunks),
            "similarity_scores": [chunk.get("similarity", 0) for chunk in context_chunks[:3]] if context_chunks else [],
            "sources": [chunk["source"] for chunk in context_chunks[:3]] if context_chunks else []
        }
        logger.info(f"Debug info: {debug_info}")
        
        # If no relevant chunks found
        if not context_chunks:
            logger.warning(f"No relevant chunks found for query: '{query.text}'")
            return ChatResponse(
                response="I don't know the answer to that question based on my available information. Try rephrasing your question or asking about topics in the PDFs.",
                sources=[],
                debug_info=debug_info
            )
        
        # Generate response
        response = generator.generate_response(query.text, context_chunks)
        
        # Extract sources from chunks
        sources = []
        for chunk in context_chunks:
            if chunk["source"] not in sources:
                sources.append(chunk["source"])
        
        logger.info(f"Returning response with {len(sources)} sources")
        return ChatResponse(
            response=response,
            sources=sources,
            debug_info=debug_info
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return ChatResponse(
            response="I'm sorry, but I encountered an error while processing your request.",
            error=str(e),
            debug_info={"error": str(e)}
        )