
import tiktoken
from src.utils.logger import setup_logger

class Memory:
    def __init__(self, max_messages=10, max_tokens=100000):
        self.history = []
        self.session_state = {}         # Estado da sessão para armazenar variáveis
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.logger = setup_logger()    # Adicionando o logger aqui
        self.summary = ""

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
        Retorna o resumo acumulado + histórico recente + estado atual como contexto.
        """
        context = []

        # Se já existe um resumo consolidado, injeta como "system"
        if hasattr(self, "summary") and self.summary:
            context.append({
                "role": "system",
                "content": f"[Conversation Summary]\n{self.summary}"
            })

        # Inclui as mensagens recentes do histórico
        context.extend(self.history)

        # Inclui também o estado da sessão, se existir
        if self.session_state:
            state_str = "\n".join(f"{k}: {v}" for k, v in self.session_state.items())
            context.append({
                "role": "system",
                "content": f"[Session State]\n{state_str}"
            })

        return context

    def clear(self):
        self.history = []
        self.session_state = {}

    def _truncate(self, summarize_fn=None):
        """
        Trunca a memória quando o limite é atingido.
        Se houver summarize_fn, usa o modelo para resumir as mensagens antigas.
        Caso contrário, apenas concatena em texto bruto.
        """
        if len(self.history) > self.max_messages:
            self.logger.info(f"Criando resumo da memória (total {len(self.history)} mensagens).")

            # Pega as mensagens mais antigas além da metade que queremos manter
            excess = self.history[:-self.max_messages // 2]
            text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in excess])

            if summarize_fn:
                summary_text = summarize_fn(text_to_summarize)
            else:
                summary_text = text_to_summarize

            # loga o resumo gerado
            self.logger.debug(f"Resumo gerado:\n{summary_text}")

            # Acumula no resumo
            self.summary = (self.summary + "\n" if getattr(self, "summary", None) else "") + summary_text

            # Mantém só a metade mais recente
            self.history = self.history[-self.max_messages // 2:]

        # Truncamento por tokens (se ainda exceder)
        while self._get_total_tokens() > self.max_tokens and self.history:
            for i, msg in enumerate(self.history):
                if msg['role'] != 'system':
                    if summarize_fn:
                        self.summary += "\n" + summarize_fn(msg['content'])
                    else:
                        self.summary += f"\n{msg['role']}: {msg['content']}"
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

    # ---------------------------
    # Memory summarization with model
    # ---------------------------
    def _summarize_with_model(self, text: str, agent):
        """
        Usa o modelo do agente para gerar um resumo das mensagens antigas.
        """
        prompt = [
            {"role": "system", "content": "Summarize the following conversation objectively, keep only key facts and decisions."},
            {"role": "user", "content": text}
        ]
        try:
            summary = agent._send_to_model(prompt)
            self.logger.info(f"✅ Resumo criado com sucesso (tamanho={len(summary)} chars).")
            return summary
        except Exception as e:
            self.logger.error(f"Erro ao resumir: {e}")
            return text[:500]  # fallback em caso de erro
