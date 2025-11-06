import pdfplumber
from typing import List
import os

from src.ingestion.parser_base import DocumentParser
from src.core.logger import log_info
from src.core.logger import log_info, log_success

# OCR opcional
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class PDFParser(DocumentParser):
    """Parser de PDF com fallback OCR para documentos escaneados."""

    def parse(self, file_path: str) -> List[str]:
        log_info(f"📄 Parsing PDF: {file_path}")

        texts = []
        text_found = False

        # --- 1️⃣ Tentar extrair texto normalmente com pdfplumber ---
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                texts.append(text)
                if text.strip():
                    text_found = True

        # --- 2️⃣ Se não encontrou texto, aplicar OCR ---
        if not text_found:
            if not OCR_AVAILABLE:
                log_info("⚠️ Nenhum texto detectado e OCR não disponível. Instale pytesseract e pdf2image.")
                return texts

            log_info("🧠 Nenhum texto detectado — aplicando OCR em cada página...")

            try:
                # Converter páginas em imagens
                images = convert_from_path(file_path)
                texts = []

                for i, image in enumerate(images, start=1):
                    text = pytesseract.image_to_string(image, lang="por+eng")
                    texts.append(text)
                    log_info(f"🖼️ OCR extraído da página {i} ({len(text)} caracteres).")

                log_success(f"✅ OCR concluído com sucesso em {len(images)} páginas.")
            except Exception as e:
                log_info(f"❌ Erro ao aplicar OCR: {e}")

        return texts