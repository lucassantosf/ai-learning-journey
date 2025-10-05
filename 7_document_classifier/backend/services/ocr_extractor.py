import pytesseract
from pdf2image import convert_from_path
from pathlib import Path

class OCRExtractor:
    def __init__(self, tesseract_cmd: str = None):
        # Caso precise especificar o binário do Tesseract
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de um PDF escaneado usando OCR.
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_file}")

        # Converter páginas do PDF para imagens
        pages = convert_from_path(str(pdf_file))

        extracted_text = []
        for page_number, page in enumerate(pages, start=1):
            text = pytesseract.image_to_string(page, lang="por")  # 'por' para português
            extracted_text.append(f"--- Página {page_number} ---\n{text}")

        return "\n".join(extracted_text)

if __name__ == "__main__":
    ocr = OCRExtractor()
    texto = ocr.extract_text_from_pdf("dataset/ocr_tests/contract.pdf")
    print(texto)