
import tiktoken
from src.utils.logger import setup_logger

class Memory:
    def __init__(self, max_messages=50, max_tokens=10000):
        self.history = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.logger = setup_logger()  # Adicionando o logger aqui

    def add_message(self, role: str, content: str, name: str = None):
        message = {"role": role, "content": content}
        if name:
            message["name"] = name
        self.history.append(message)
        self._truncate()

    def get_context(self) -> list:
        return self.history.copy()

    def clear(self):
        self.history = []

    def _truncate(self):
        # Primeiro, remove mensagens que excedem o limite de mensagens
        if len(self.history) > self.max_messages:
            self.logger.warning(f"⚠️ Memória: Limite de mensagens excedido ({len(self.history)} > {self.max_messages}). Removendo as mensagens mais antigas.")
            self.history = self.history[-self.max_messages:]

        # Depois, reduz os tokens, se necessário
        current_tokens = self._get_total_tokens()
        if current_tokens > self.max_tokens:
            self.logger.warning(f"⚠️ Memória: Limite de tokens excedido ({current_tokens} > {self.max_tokens}). Removendo mensagens até o limite ser alcançado.")
        
        while self._get_total_tokens() > self.max_tokens:
            # Remove a mensagem mais antiga que não seja do tipo 'system'
            for i, msg in enumerate(self.history):
                if msg['role'] != 'system':
                    del self.history[i]
                    break

    def _get_total_tokens(self) -> int:
        return sum(len(self.tokenizer.encode(msg['content'])) for msg in self.history)

    def summarize_context(self, system_prompt: str) -> list:
        """
        Summarize context while preserving key information
        
        :param system_prompt: Original system prompt to preserve
        :return: Summarized context
        """
        # Keep system prompt and most recent messages
        summary = [msg for msg in self.history if msg['role'] == 'system']
        recent_messages = [msg for msg in self.history if msg['role'] != 'system'][-5:]
        
        summary.extend(recent_messages)
        return summary
