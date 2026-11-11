from dataclasses import dataclass, field
import uuid

@dataclass
class Config:
    model_name: str = "qwen3.5:4b"
    system_prompt: str = "You are an expert AI assistant equipped with file tools and semantic memory."
    max_history_messages: int = 6  # Keep last 6 exact messages
    summary_threshold: int = 8      # Summarize when total messages reach this count
    storage_dir: str = "version_5/sessions"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    temperature: float = 0.7
    num_ctx: int = 4096
    num_predict: int = 1024  # Cap maximum output tokens
    keep_alive: str = "15m"  # Keep model loaded in VRAM for 15 minutes