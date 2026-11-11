from dataclasses import dataclass, field
import uuid

@dataclass
class Config:
    model_name: str = "qwen3.5:4b"
    system_prompt: str = "You are a personalized AI assistant. Always respect known user preferences and past facts."
    
    max_history_messages: int = 8
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # PostgreSQL Connection DSN
    postgres_dsn: str = "postgresql://postgres:postgres@localhost:5432/chatbot_db"
    
    temperature: float = 0.7
    num_ctx: int = 4096
    num_predict: int = 1024
    keep_alive: str = "30m"