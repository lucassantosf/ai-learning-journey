
import tiktoken
from src.utils.logger import setup_logger

class Memory:
    def __init__(self, max_messages=50, max_tokens=100000):
        self.history = []
        self.session_state = {}         # Estado da sessão para armazenar variáveis
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.logger = setup_logger()    # Adicionando o logger aqui

    # ---------------------------
    # Short-term memory 
    # ---------------------------
    def add_message(self, role: str, content: str, name: str = None):
        message = {"role": role, "content": content}
        if name:
            message["name"] = name
        self.history.append(message)
        self._truncate()

    def get_context(self) -> list:
        """
        Retorna o histórico + estado atual como contexto
        """
        context = self.history.copy()
        if self.session_state:
            state_str = "\n".join(f"{k}: {v}" for k, v in self.session_state.items())
            context.append({"role": "system", "content": f"[Session State]\n{state_str}"})
        return context

    def clear(self):
        self.history = []
        self.session_state = {}

    def _truncate(self):
        # Primeiro, remove mensagens que excedem o limite de mensagens
        if len(self.history) > self.max_messages:
            self.logger.warning(f"⚠️ Memória: Limite de mensagens excedido ({len(self.history)} > {self.max_messages}). Removendo as mensagens mais antigas.")
            self.history = self.history[-self.max_messages:]

        # Depois, reduz os tokens, se necessário
        #current_tokens = self._get_total_tokens()
        #if current_tokens > self.max_tokens:
        #    self.logger.warning(f"⚠️ Memória: Limite de tokens excedido ({current_tokens} > {self.max_tokens}). Removendo mensagens até o limite ser alcançado.")
        
        while self._get_total_tokens() > self.max_tokens:
            # Remove a mensagem mais antiga que não seja do tipo 'system'
            for i, msg in enumerate(self.history):
                if msg['role'] != 'system':
                    del self.history[i]
                    break

    def _get_total_tokens(self) -> int:
        return sum(len(self.tokenizer.encode(msg['content'])) for msg in self.history)

    # ---------------------------
    # Stateful memory (novo)
    # ---------------------------
    def set_state(self, key: str, value):
        self.logger.info(f"🧠 Atualizando state: {key} = {value}")
        self.session_state[key] = value

    def get_state(self, key: str, default=None):
        return self.session_state.get(key, default)

    def remove_state(self, key: str):
        if key in self.session_state:
            del self.session_state[key]
