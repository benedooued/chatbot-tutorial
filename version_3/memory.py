import json
import os

class ConversationMemory:
    def __init__(self, system_prompt: str, max_history: int, storage_file: str):
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.storage_file = storage_file
        self.history = self._load()

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self._save()

    def get_context(self) -> list:
        recent_history = self.history[-self.max_history:]
        return [{"role": "system", "content": self.system_prompt}] + recent_history

    def clear(self):
        self.history.clear()
        self._save()

    def _save(self):
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def _load(self) -> list:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []