import pdfplumber
from typing import List

class PDFParser:
    """
    Classe responsável por fazer o parsing de PDFs e extrair texto.
    Pode ser expandida futuramente para lidar com tabelas, metadados etc.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> List[str]:
        """
        Extrai o texto de todas as páginas do PDF.
        Retorna uma lista onde cada item é o texto de uma página.
        """
        textos = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                textos.append(texto if texto else "")
        return textos