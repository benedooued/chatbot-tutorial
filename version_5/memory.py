import json
import os
from datetime import datetime
import ollama

class SummarizedMemory:
    def __init__(self, storage_dir: str, session_id: str, system_prompt: str, max_history: int, threshold: int, model_name: str):
        self.storage_dir = storage_dir
        self.session_id = session_id
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.threshold = threshold
        self.model_name = model_name
        self.file_path = os.path.join(self.storage_dir, f"session_{self.session_id}.json")
        
        os.makedirs(self.storage_dir, exist_ok=True)
        data = self._load()
        self.history = data.get("messages", [])
        self.summary = data.get("summary", "")

    def add_message(self, role: str, content: str, name: str = None):
        msg = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        if name:
            msg["name"] = name
        self.history.append(msg)
        self._save()

    async def summarize_if_needed(self):
        """Compresses older history into an ongoing abstract summary."""
        if len(self.history) >= self.threshold:
            to_summarize = self.history[:-self.max_history]
            recent = self.history[-self.max_history:]
            
            prompt = f"Summarize the main points of this conversation concise bullet points:\n"
            for m in to_summarize:
                prompt += f"{m['role']}: {m['content']}\n"
            
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            new_summary_text = response["message"]["content"]
            if self.summary:
                self.summary += f"\n{new_summary_text}"
            else:
                self.summary = new_summary_text
                
            self.history = recent
            self._save()

    def get_context(self) -> list:
        clean_context = [{"role": "system", "content": self.system_prompt}]
        
        if self.summary:
            clean_context.append({
                "role": "system", 
                "content": f"Summary of earlier conversation:\n{self.summary}"
            })

        for item in self.history[-self.max_history:]:
            ctx_item = {"role": item["role"], "content": item["content"]}
            if "name" in item:
                ctx_item["name"] = item["name"]
            clean_context.append(ctx_item)
            
        return clean_context

    def clear(self):
        self.history = []
        self.summary = ""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def _save(self):
        data = {
            "session_id": self.session_id,
            "summary": self.summary,
            "updated_at": datetime.now().isoformat(),
            "messages": self.history
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> dict:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}