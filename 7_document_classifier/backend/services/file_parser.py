from pathlib import Path
from services.pdf_parser import PDFParser
from services.docx_parser import DocxParser
from services.ocr_extractor import OCRExtractor

ocr_engine = OCRExtractor()

def parse_file(file_path: str) -> str:
    """
    Detecta o tipo do arquivo e extrai texto.
    Se PDF estiver vazio, aplica OCR.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        parser = PDFParser(file_path)
        text = parser.extract_text()
        text = " ".join(text) if isinstance(text, list) else text

        # fallback para OCR se vazio
        if not text.strip():
            print(f"[INFO] Nenhum texto detectado em {file_path}, aplicando OCR...")
            text = ocr_engine.extract_text_from_pdf(file_path)

        return text

    elif ext == ".docx":
        parser = DocxParser(file_path)
        return parser.get_text()

    else:
        raise ValueError(f"Formato não suportado: {ext}")