import asyncio
import json
from db import PostgresDatabaseManager
from ollama import AsyncClient

class PreferenceAwarePostgresMemory:
    def __init__(self, db: PostgresDatabaseManager, user_id: str, session_id: str, system_prompt: str, max_history: int, model_name: str):
        self.db = db
        self.user_id = user_id
        self.session_id = session_id
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.model_name = model_name
        self.async_ollama = AsyncClient()

    async def add_message(self, role: str, content: str, name: str = None):
        await self.db.save_message(self.session_id, role, content, name)

    def extract_facts_in_background(self, user_message: str):
        """Dispatches extraction directly to asyncio event loop without blocking response."""
        asyncio.create_task(self._extract_facts_task(user_message))

    async def _extract_facts_task(self, text: str):
        prompt = (
            "Analyze the following message. If the user states explicit personal information, preferences, "
            "or facts about themselves (e.g., name, job, tech stack, interests), extract them as a JSON object "
            "of key-value pairs. If no explicit user facts/preferences exist, output `{}`.\n\n"
            f"Message: \"{text}\"\n\nOutput JSON ONLY:"
        )
        try:
            response = await self.async_ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )
            raw_content = response["message"]["content"].strip()
            extracted = json.loads(raw_content)
            
            if isinstance(extracted, dict):
                for key, val in extracted.items():
                    if val:
                        await self.db.save_user_fact(self.user_id, str(key), str(val))
        except Exception:
            pass  # Silent failure recovery

    async def get_context(self) -> list:
        user_facts = await self.db.get_user_facts(self.user_id)
        
        enriched_system = self.system_prompt
        if user_facts:
            enriched_system += "\n\n[Persistent User Profile & Known Preferences]:\n"
            for k, v in user_facts.items():
                enriched_system += f"- {k}: {v}\n"

        context = [{"role": "system", "content": enriched_system}]
        recent_messages = await self.db.get_recent_messages(self.session_id, limit=self.max_history)
        context.extend(recent_messages)
        
        return context