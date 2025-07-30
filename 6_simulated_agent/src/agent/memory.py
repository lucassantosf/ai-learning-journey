
class Memory:
    def __init__(self, max_messages=20):
        self.history = []
        self.max_messages = max_messages

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
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]