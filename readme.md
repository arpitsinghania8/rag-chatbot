# PDF-Based RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot trained on PDF documents. This chatbot uses simple information retrieval techniques to answer questions based only on the content of provided PDF files, without relying on external APIs.

## Features

- Extracts text from PDF documents
- Processes and chunks text content for semantic search
- Creates vector embeddings using sentence-transformers
- Performs similarity search using FAISS
- Provides direct answers from the most relevant text chunks
- Responds with "I don't know" for questions outside of its knowledge base
- Provides citations to information sources
- FastAPI backend for reliability and performance
- Gradio web UI for a user-friendly experience

## Setup Instructions

### Prerequisites

- Python 3.8 or later
- PDF documents (place in the `data/pdfs` directory)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd rag-chatbot
```

2. Run the setup script:

```bash
bash scripts/setup.sh
```

This script will:

- Create a virtual environment
- Install dependencies
- Set up data directories
- Configure environment variables

### Data Processing

1. Place your PDF documents in the `data/pdfs` directory.

2. Run the data preparation script:

```bash
python scripts/prepare_data.py
```

This script will:

- Extract text from your PDF documents
- Process and chunk the text
- Create vector embeddings for search

### Running the Chatbot

1. Start the API server:

```bash
uvicorn src.api.main:app --reload --port 8000
```

2. In a new terminal, start the UI:

```bash
python ui/app.py
```

3. Open your browser and navigate to `http://localhost:7860` to interact with the chatbot.

## Project Structure

```
rag-chatbot/
├── data/                  # Data storage
│   ├── raw_text/          # Extracted text from PDFs
│   ├── processed/         # Processed text chunks
│   ├── embeddings/        # Vector embeddings and index
│   └── pdfs/              # PDF documents
├── scripts/               # Data processing scripts
│   ├── extract_pdf.py     # PDF text extraction
│   ├── process_data.py    # Text processing
│   ├── create_embeddings.py # Vector embedding creation
│   ├── prepare_data.py    # Complete pipeline
│   └── setup.sh           # Environment setup
├── src/                   # Core chatbot logic
│   ├── chatbot/           # Chatbot components
│   │   ├── retriever.py   # Vector search
│   │   └── generator.py   # Response generation
│   └── api/               # FastAPI backend
│       └── main.py        # API endpoints
├── ui/                    # Gradio interface
│   └── app.py             # Web UI
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## How It Works

1. **Data Collection**: The system extracts text from your PDF documents.
2. **Text Processing**: Documents are split into manageable chunks with appropriate overlap.
3. **Embedding Creation**: Text chunks are converted to vector embeddings using sentence-transformers.
4. **Retrieval**: When a user asks a question, the system finds the most relevant chunks using semantic search.
5. **Generation**: The system returns the most relevant text chunk as the answer.
6. **Verification**: If no relevant information is found, the system responds with "I don't know."

## Customization

- Change the embedding model in `src/chatbot/retriever.py`
- Adjust chunk sizes in `scripts/process_data.py`
- Modify the retrieval parameters in `src/chatbot/retriever.py`
- Update the UI theme and examples in `ui/app.py`

## License

MIT
