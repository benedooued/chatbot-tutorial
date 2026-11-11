from dataclasses import dataclass, field
import uuid

@dataclass
class Config:
    model_name: str = "qwen3.5:4b"
    system_prompt: str = "You are an intelligent AI assistant equipped with tools."
    max_history_messages: int = 12
    storage_dir: str = "version_4/sessions"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    temperature: float = 0.7
    num_ctx: int = 4096