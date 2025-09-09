
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
        - Nunca resume o prompt inicial (system base).
        - Resume apenas interações antigas (user/assistant/function).
        - Mantém as últimas N interações intactas.
        """
        KEEP_LAST = 6  # mantém as 6 últimas mensagens brutas

        if len(self.history) > self.max_messages:
            self.logger.info(f"Criando resumo da memória (total {len(self.history)} mensagens).")

            # Separa o system base (primeira mensagem)
            base_system = self.history[0] if self.history and self.history[0]["role"] == "system" else None

            # Pega as mensagens antigas que devem ser resumidas (exclui o system base e as últimas N)
            excess = self.history[1:-KEEP_LAST]

            # Concatena em texto
            text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in excess if m["role"] != "system"])

            if text_to_summarize.strip():
                summary_text = summarize_fn(text_to_summarize) if summarize_fn else text_to_summarize
                self.logger.debug(f"Resumo gerado:\n{summary_text}")

                # Cria a entrada de resumo
                summary_entry = {"role": "system", "content": f"[Conversation Summary]\n{summary_text}"}

                # Reconstrói a history: base_system + resumo + últimas mensagens
                self.history = ([base_system] if base_system else []) + [summary_entry] + self.history[-KEEP_LAST:]

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
        
    def _maybe_summarize_block(self, agent=None, summarize_every=5):
        """
        Se o número de mensagens do usuário desde o último resumo >= summarize_every,
        cria um resumo incremental e substitui essas interações pelo resumo.
        """
        # Conta só interações "usuário + assistente"
        user_msgs = [m for m in self.history if m["role"] == "user"]

        if len(user_msgs) >= summarize_every:
            # Pega só o bloco a resumir (tudo menos system/resumo)
            block = []
            for m in self.history:
                if m["role"] not in ("system", "summary"):
                    block.append(f"{m['role']}: {m['content']}")

            text_to_summarize = "\n".join(block)

            if agent:
                summary_text = self._summarize_with_model(text_to_summarize, agent)
            else:
                summary_text = text_to_summarize

            # Cria uma nova entrada de resumo
            self.history = [m for m in self.history if m["role"] == "system"] + [
                m for m in self.history if m["role"] == "summary"
            ] + [{"role": "summary", "content": summary_text}]

            self.logger.info("Resumo incremental adicionado ao histórico:")
            self.logger.info(summary_text)

