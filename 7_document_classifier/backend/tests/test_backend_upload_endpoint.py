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
    return ('file', (filename, file, 'application/octet-stream'))

def test_upload_pdf():
    # Path to a test PDF file
    test_pdf_path = os.path.join(os.path.dirname(__file__), '../../lorem-ipsum.pdf')
    
    with open(test_pdf_path, 'rb') as pdf_file:
        response = client.post(
            "/upload", 
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            data={"name": "Test PDF Upload"}
        )
    
    assert response.status_code == 200
    assert response.json()["file_extension"] == ".pdf"
    assert len(response.json()["content"]) > 0

def test_upload_docx():
    # Path to a test DOCX file
    test_docx_path = os.path.join(os.path.dirname(__file__), '../../lorem_ipsum.docx')
    
    with open(test_docx_path, 'rb') as docx_file:
        response = client.post(
            "/upload", 
            files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"name": "Test DOCX Upload"}
        )
    
    assert response.status_code == 200
    assert response.json()["file_extension"] == ".docx"
    assert len(response.json()["content"]) > 0

def test_upload_unsupported_format():
    # Test uploading an unsupported file type
    unsupported_file = create_test_file("test.txt", "This is a text file")
    
    response = client.post(
        "/upload", 
        files={"file": unsupported_file},
        data={"name": "Unsupported File"}
    )
    
    # assert response.status_code == 200
    assert response.json()["content"] == "Not supported format"
