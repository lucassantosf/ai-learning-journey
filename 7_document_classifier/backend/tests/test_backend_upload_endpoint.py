import pytest
from fastapi.testclient import TestClient
from api.main import api  # Import your FastAPI application
import os
from io import BytesIO

# Create a TestClient instance
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