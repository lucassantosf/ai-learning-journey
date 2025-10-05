import pytest
import os
from backend.services.ocr_extractor import OCRExtractor

class TestOCRExtractor:
    def setup_method(self):
        self.ocr = OCRExtractor()
        self.test_files_dir = os.path.join(os.path.dirname(__file__), '../dataset/ocr_tests')  # Removed the trailing comma

    def test_extract_text_from_resume_pdf(self):
        resume_path = os.path.join(self.test_files_dir, 'resume.pdf')
        extracted_text = self.ocr.extract_text_from_pdf(resume_path)
        
        assert extracted_text is not None, "Extracted text should not be None"
        assert len(extracted_text.strip()) > 0, "Extracted text should not be empty"

        # Remove page headers and normalize the text
        normalized_text = ' '.join(line.strip() for line in extracted_text.split('\n') if line.strip() and not line.startswith('---'))
        assert "gabriel fernandes" in normalized_text.lower(), "Extracted text should contain the author's name"

    def test_extract_text_from_invoice_pdf(self):
        invoice_path = os.path.join(self.test_files_dir, 'invoice.pdf')
        extracted_text = self.ocr.extract_text_from_pdf(invoice_path)
        
        assert extracted_text is not None, "Extracted text should not be None"
        assert len(extracted_text.strip()) > 0, "Extracted text should not be empty"

        # Remove page headers and normalize the text
        normalized_text = ' '.join(line.strip() for line in extracted_text.split('\n') if line.strip() and not line.startswith('---'))
        assert "nota fiscal" in normalized_text.lower(), "Extracted text should contain 'NOTA FISCAL'"

    def test_extract_text_from_contract_pdf(self):
        contract_path = os.path.join(self.test_files_dir, 'contract.pdf')
        extracted_text = self.ocr.extract_text_from_pdf(contract_path)
        
        assert extracted_text is not None, "Extracted text should not be None"
        assert len(extracted_text.strip()) > 0, "Extracted text should not be empty"
        
        # Remove page headers and normalize the text
        normalized_text = ' '.join(line.strip() for line in extracted_text.split('\n') if line.strip() and not line.startswith('---'))
        assert "contrato de prestação" in normalized_text.lower(), "Extracted text should contain 'CONTRATO DE PRESTA..'"

    def test_extract_text_from_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            self.ocr.extract_text_from_pdf('nonexistent_file.pdf')