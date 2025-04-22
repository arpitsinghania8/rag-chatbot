#!/bin/bash
set -e

# Terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==== PDF-Based RAG Chatbot ====${NC}"

# Check if PDFs exist
if [ ! "$(ls -A data/pdfs 2>/dev/null)" ]; then
    echo -e "${YELLOW}No PDF files found in data/pdfs directory!${NC}"
    echo -e "Please place your PDF documents in the data/pdfs directory."
    mkdir -p data/pdfs
    exit 1
fi

# Check if embeddings exist
if [ ! -f "data/embeddings/docs.index" ] || [ ! -f "data/embeddings/chunks_metadata.json" ]; then
    echo -e "${YELLOW}Embeddings not found. Running data processing pipeline...${NC}"
    python scripts/prepare_data.py
fi

# Start the API server in the background
echo -e "${YELLOW}Starting API server...${NC}"
uvicorn src.api.main:app --port 8000 &
API_PID=$!

# Wait for the API to start
echo -e "${YELLOW}Waiting for API server to start...${NC}"
sleep 5

# Start the UI
echo -e "${YELLOW}Starting UI server...${NC}"
python ui/app.py &
UI_PID=$!

echo -e "${GREEN}Both servers are running!${NC}"
echo -e "API server (PID: $API_PID) is running on http://localhost:8000"
echo -e "UI server (PID: $UI_PID) is running on http://localhost:7860"
echo -e "Open your browser and navigate to http://localhost:7860 to use the chatbot."
echo -e "Press Ctrl+C to stop the servers."

# Trap Ctrl+C to stop both servers
trap "echo -e '${YELLOW}Stopping servers...${NC}'; kill $API_PID $UI_PID 2>/dev/null" INT

# Wait for any process to exit
wait 