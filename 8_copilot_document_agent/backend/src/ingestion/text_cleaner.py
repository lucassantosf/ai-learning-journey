from src.core.logger import log_info

class TextCleaner:
    def clean(self, text: str) -> str:
        log_info("Limpando texto...")
        # TODO: Implementar limpeza real (remover espaços, quebras, etc.)
        return text.strip()