import gradio as gr
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# API configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000")

def chat(message, history):
    """Process user message and get chatbot response"""
    try:
        # Call the API
        response = requests.post(
            f"{API_URL}/chat",
            json={"text": message},
            timeout=30
        )
        
        # Handle API errors
        if response.status_code != 200:
            response_text = f"Error: API returned status code {response.status_code}"
            history.append((message, response_text))
            return "", history
        
        # Parse response
        result = response.json()
        
        # Format response with sources if available
        chatbot_response = result.get("response", "Sorry, I couldn't process your request.")
        
        # Handle "I don't know" responses consistently
        if "I don't know" in chatbot_response or "don't have information" in chatbot_response:
            chatbot_response = "I don't have information about that in my knowledge base. Please ask a question related to the content in the provided PDF documents."
        
        # Add the conversation to history
        history.append((message, chatbot_response))
        
        # Return empty message (to clear the input) and updated history
        return "", history
        
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        history.append((message, error_message))
        return "", history

def main():
    # Create the Gradio interface with Gradio 3.x compatibility
    with gr.Blocks(theme=gr.themes.Default()) as demo:
        gr.Markdown("""
        # PDF-Based Support Assistant
        
        Welcome to the PDF-Based Support Assistant! I can help you with questions about the content in the provided PDF documents.
        
        I'll search through the PDF documents to find information that answers your questions.
        
        Ask me anything about the content in the uploaded PDFs!
        """)
        
        chatbot = gr.Chatbot(label="Conversation")
        msg = gr.Textbox(label="Your question", placeholder="Ask a question about the PDF content...")
        clear = gr.Button("Clear conversation")
        
        msg.submit(chat, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
        
        gr.Examples(
            examples=[
                "What information is contained in the PDFs?",
                "Tell me about the key points in the documents.",
                "Explain the main concepts from the PDFs.",
                "What are the important details in the documents?",
                "Summarize the content of the PDFs."
            ],
            inputs=msg
        )
    
    # Launch the app
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    main()