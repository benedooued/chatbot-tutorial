class ConversationMemory:
    def __init__(self, system_prompt: str, max_history: int):
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.history = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_context(self) -> list:
        # Keep system prompt at the top, plus the last N messages
        recent_history = self.history[-self.max_history:]
        return [{"role": "system", "content": self.system_prompt}] + recent_history

    def clear(self):
        self.history.clear()