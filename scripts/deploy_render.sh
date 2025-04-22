#!/bin/bash
set -e

# Terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==== Angel One RAG Chatbot - Render.com Deployment ====${NC}"

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}Render CLI not installed. Installing...${NC}"
    curl -s https://render.com/download/cli | bash
fi

# Create deployment directories
echo -e "${YELLOW}Creating deployment directories...${NC}"
mkdir -p deploy/api
mkdir -p deploy/ui

# Copy API files
echo -e "${YELLOW}Copying API files...${NC}"
cp -r src deploy/api/
cp -r data/embeddings deploy/api/data/ 2>/dev/null || mkdir -p deploy/api/data/embeddings
cp requirements.txt deploy/api/
cat > deploy/api/main.py << 'EOF'
import uvicorn
from src.api.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# Create API render.yaml
cat > deploy/api/render.yaml << 'EOF'
services:
  - type: web
    name: angelone-chatbot-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: OPENAI_API_KEY
        sync: false
EOF

# Copy UI files
echo -e "${YELLOW}Copying UI files...${NC}"
cp -r ui deploy/ui/
cp requirements.txt deploy/ui/

# Create UI render.yaml
cat > deploy/ui/render.yaml << 'EOF'
services:
  - type: web
    name: angelone-chatbot-ui
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python ui/app.py
    envVars:
      - key: API_URL
        value: https://angelone-chatbot-api.onrender.com
EOF

echo -e "${GREEN}==== Deployment files created successfully ====${NC}"
echo -e "Files are ready in the deploy/ directory."
echo -e "\nTo deploy to Render.com:"
echo -e "1. Create a new Web Service in Render Dashboard"
echo -e "2. Connect your repository"
echo -e "3. Set the following settings:"
echo -e "   - Environment: Python"
echo -e "   - Build Command: pip install -r requirements.txt"
echo -e "   - Start Command: python main.py (for API) or python ui/app.py (for UI)"
echo -e "4. Add OPENAI_API_KEY environment variable"
echo -e "5. For the UI service, also add API_URL pointing to your API service URL"
echo -e "\nAlternatively, if you have render-cli configured:"
echo -e "cd deploy/api && render blueprint create"
echo -e "cd ../ui && render blueprint create" 