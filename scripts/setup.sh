#!/bin/bash
set -e

# Terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==== Angel One RAG Chatbot Setup ====${NC}"
echo -e "This script will set up the environment for the Angel One RAG Chatbot."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher and try again.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
echo -e "${GREEN}Using Python version: ${PYTHON_VERSION}${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/raw_html
mkdir -p data/raw_text
mkdir -p data/processed
mkdir -p data/embeddings
mkdir -p data/pdfs

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}OPENAI_API_KEY environment variable not set.${NC}"
    echo -e "Please set it by running: export OPENAI_API_KEY='your-api-key-here'"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating .env file. Please edit it to add your OpenAI API key.${NC}"
        echo "OPENAI_API_KEY=your-api-key-here" > .env
    fi
else
    echo -e "${GREEN}OPENAI_API_KEY is set.${NC}"
    
    # Update .env file
    if [ -f ".env" ]; then
        if ! grep -q "OPENAI_API_KEY" .env; then
            echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env
        fi
    else
        echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env
    fi
fi

echo -e "${GREEN}==== Setup completed successfully ====${NC}"
echo -e "To process data, run: python scripts/prepare_data.py"
echo -e "To start the API server, run: uvicorn src.api.main:app --reload --port 8000"
echo -e "To start the UI, run: python ui/app.py" 