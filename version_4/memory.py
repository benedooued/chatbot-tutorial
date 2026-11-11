import json
import os
from datetime import datetime

class StructuredMemory:
    def __init__(self, storage_dir: str, session_id: str, system_prompt: str, max_history: int):
        self.storage_dir = storage_dir
        self.session_id = session_id
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.file_path = os.path.join(self.storage_dir, f"session_{self.session_id}.json")
        
        os.makedirs(self.storage_dir, exist_ok=True)
        self.history = self._load()

    def add_message(self, role: str, content: str, name: str = None):
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if name:
            msg["name"] = name
        self.history.append(msg)
        self._save()

    def get_context(self) -> list:
        # Prepare context payload stripped of local extra metadata for API compatibility
        recent = self.history[-self.max_history:]
        clean_context = [{"role": "system", "content": self.system_prompt}]
        for item in recent:
            ctx_item = {"role": item["role"], "content": item["content"]}
            if "name" in item:
                ctx_item["name"] = item["name"]
            clean_context.append(ctx_item)
        return clean_context

    def clear(self):
        self.history = []
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def _save(self):
        data = {
            "session_id": self.session_id,
            "updated_at": datetime.now().isoformat(),
            "messages": self.history
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> list:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("messages", [])
            except Exception:
                return []
        return []