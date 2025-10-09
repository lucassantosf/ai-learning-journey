import pytest
from fastapi.testclient import TestClient
from api.main import api  # Import your FastAPI application
import os
from io import BytesIO

# Import necessary components
from agent.vector_store import VectorStore
from agent.embedder import Embedder
from agent.document_agent import DocumentAgent
from agent.prompt_engine import PromptEngine

# Function to populate vector store with real document embeddings
def populate_vector_store_with_real_docs(vector_store, embedder):
    # Directories for different document types
    doc_dirs = {
        'resumes': '../dataset/resumes',
        'invoices': '../dataset/invoices', 
        'contracts': '../dataset/contracts'
    }

    # Populate vector store with real document embeddings
    for class_name, dir_path in doc_dirs.items():
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        
        # Process each document in the directory
        for filename in os.listdir(full_path):
            file_path = os.path.join(full_path, filename)
            
            # Skip non-PDF/DOCX files
            if not filename.lower().endswith(('.pdf', '.docx')):
                continue
            
            try:
                # Extract text from the document
                text = parse_file(file_path)
                
                # Generate embedding
                embedding = embedder.generate_embeddings(text)
                
                # Add to vector store
                vector_store.add(embedding, {"class_label": class_name})
            
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Initialize components before creating the test client
api.state.embedder = Embedder()
api.state.vector_store = VectorStore()
api.state.prompt_engine = PromptEngine()
api.state.document_agent = DocumentAgent()

# Populate with real document embeddings
populate_vector_store_with_real_docs(api.state.vector_store, api.state.embedder)

# Create the TestClient
client = TestClient(api)

# Utility function to create test files
def create_test_file(filename, content):
    file = BytesIO(content.encode())
    # Directly return the tuple as it would be used in files parameter
    return ("test.txt", file, "text/plain")

def test_upload_pdf():
    # Path to a test PDF file
    test_pdf_path = os.path.join(os.path.dirname(__file__), '../dataset/resumes/resume1.pdf')
    
    with open(test_pdf_path, 'rb') as pdf_file:
        response = client.post(
            "/upload", 
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            data={"name": "Test PDF Upload"}
        )
    
    assert response.status_code == 200
    response_json = response.json()
    
    # Check for expected keys in the response
    assert "status" in response_json
    assert response_json["status"] == "success"
    assert "predicted_class" in response_json
    assert "confidence" in response_json

def test_upload_docx():
    # Path to a test DOCX file
    test_docx_path = os.path.join(os.path.dirname(__file__), '../dataset/contracts/contract2.docx')
    
    with open(test_docx_path, 'rb') as docx_file:
        response = client.post(
            "/upload", 
            files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"name": "Test DOCX Upload"}
        )
    
    assert response.status_code == 200
    response_json = response.json()
    
    # Check for expected keys in the response
    assert "status" in response_json
    assert response_json["status"] == "success"
    assert "predicted_class" in response_json
    assert "confidence" in response_json

def test_upload_unsupported_format():
    unsupported_file = create_test_file("test.txt", "This is a text file")
    
    response = client.post(
        "/upload", 
        files={"file": unsupported_file},
        data={"name": "Unsupported File"}
    )
    
    assert response.status_code == 200
    response_json = response.json()
    
    # Check for expected keys in the response
    assert "status" in response_json
    assert response_json["status"] == "error"
    assert "content" in response_json  # Changed from "message"
    assert response_json["content"] == "Not supported format"