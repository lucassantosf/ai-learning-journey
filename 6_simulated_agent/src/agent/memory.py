
import tiktoken

class Memory:
    def __init__(self, max_messages=10, max_tokens=4000):
        self.history = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

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
        # First, remove messages beyond max_messages
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

        # Then, reduce tokens if needed
        while self._get_total_tokens() > self.max_tokens:
            # Remove the oldest non-system message
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
