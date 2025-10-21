import re
from typing import List
from src.core.logger import log_info

class TextCleaner:
    def clean(self, texts: List[str]) -> List[str]:
        log_info("Limpando texto...")
        cleaned = []
        for text in texts:
            text = re.sub(r'\s+', ' ', text).strip()
            text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove caracteres especiais
            cleaned.append(text)
        return cleaned