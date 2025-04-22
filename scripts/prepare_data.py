#!/usr/bin/env python3
import os
import subprocess
import sys
import time

def run_step(step_name, command):
    """Run a step in the pipeline and check for success"""
    print(f"\n{'='*80}\n{step_name}\n{'='*80}")
    
    try:
        # Run the command and capture output
        start_time = time.time()
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        elapsed_time = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        print(f"\n✅ {step_name} completed successfully in {elapsed_time:.1f} seconds.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {step_name} failed with error code {e.returncode}.")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Run the complete data processing pipeline for PDFs only"""
    
    print("\nRAG-Chatbot: PDF Processing Pipeline")
    print(f"Working directory: {os.getcwd()}\n")
    
    # Make sure data directories exist
    os.makedirs("data/raw_text", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)
    os.makedirs("data/pdfs", exist_ok=True)
    
    # Verify PDF directory and give instructions
    if not any(f.lower().endswith('.pdf') for f in os.listdir("data/pdfs")):
        print("\n⚠️ No PDF files found in data/pdfs directory!")
        print("Please place your PDF files in the data/pdfs directory.")
        print("Exiting. Please add PDF files and run again.")
        return
    
    # Run each step in sequence
    steps = [
        ("PDF extraction", "python scripts/extract_pdf.py"),
        ("Data processing", "python scripts/process_data.py"),
        ("Embedding creation", "python scripts/create_embeddings.py")
    ]
    
    for step_name, command in steps:
        success = run_step(step_name, command)
        if not success:
            print(f"\n❌ Pipeline failed at step: {step_name}")
            print("Aborting remaining steps.")
            return
    
    print("\n🎉 All data processing steps completed successfully!")
    print("\nNext steps:")
    print("1. Start the API server: uvicorn src.api.main:app --reload --port 8000")
    print("2. Start the UI: python ui/app.py")
    print("3. Open your browser at http://localhost:7860 to use the chatbot")

if __name__ == "__main__":
    main() 