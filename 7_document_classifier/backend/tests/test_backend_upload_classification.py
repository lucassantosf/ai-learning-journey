import os
import pytest
from fastapi.testclient import TestClient
from api.main import api

client = TestClient(api)

def test_upload_resume():
    # Path to test resume files
    resume_files = [
        os.path.join(os.path.dirname(__file__), '../dataset/resumes/resume1.pdf'),
        os.path.join(os.path.dirname(__file__), '../dataset/resumes/resume2.pdf')
    ]
    
    for resume_path in resume_files:
        with open(resume_path, 'rb') as resume_file:
            response = client.post(
                "/upload", 
                files={"file": ("test_resume.pdf", resume_file, "application/pdf")},
                data={"name": "Test Resume Upload"}
            )
        
        assert response.status_code == 200
        response_json = response.json()
        
        # Verify classification
        assert "status" in response_json
        assert response_json["status"] == "success"
        assert "predicted_class" in response_json
        assert response_json["predicted_class"].lower() == "resumes"
        assert "confidence" in response_json
        assert response_json["confidence"] > 0.5  # Reasonable confidence threshold

def test_upload_invoice():
    # Path to test invoice files
    invoice_files = [
        os.path.join(os.path.dirname(__file__), '../dataset/invoices/invoice1.pdf'),
        os.path.join(os.path.dirname(__file__), '../dataset/invoices/invoice2.docx')
    ]
    
    for invoice_path in invoice_files:
        with open(invoice_path, 'rb') as invoice_file:
            response = client.post(
                "/upload", 
                files={"file": (os.path.basename(invoice_path), invoice_file, "application/pdf" if invoice_path.endswith('.pdf') else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Test Invoice Upload"}
            )
        
        assert response.status_code == 200
        response_json = response.json()
        
        # Verify classification
        assert "status" in response_json
        assert response_json["status"] == "success"
        assert "predicted_class" in response_json
        assert response_json["predicted_class"].lower() == "invoices"
        assert "confidence" in response_json
        assert response_json["confidence"] > 0.5  # Reasonable confidence threshold

def test_upload_contract():
    # Path to test contract files
    contract_files = [
        os.path.join(os.path.dirname(__file__), '../dataset/contracts/contract1.pdf'),
        os.path.join(os.path.dirname(__file__), '../dataset/contracts/contract2.docx')
    ]
    
    for contract_path in contract_files:
        with open(contract_path, 'rb') as contract_file:
            response = client.post(
                "/upload", 
                files={"file": (os.path.basename(contract_path), contract_file, "application/pdf" if contract_path.endswith('.pdf') else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Test Contract Upload"}
            )
        
        assert response.status_code == 200
        response_json = response.json()
        
        # Verify classification
        assert "status" in response_json
        assert response_json["status"] == "success"
        assert "predicted_class" in response_json
        assert response_json["predicted_class"].lower() == "contracts"
        assert "confidence" in response_json
        assert response_json["confidence"] > 0.5  # Reasonable confidence threshold
