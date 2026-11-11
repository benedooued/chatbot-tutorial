from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from config import Config
from db import PostgresDatabaseManager
from memory import PreferenceAwarePostgresMemory
from client import PreferenceAgent

cfg = Config()
db = PostgresDatabaseManager(dsn=cfg.postgres_dsn)
agent = PreferenceAgent(
    model_name=cfg.model_name,
    temperature=cfg.temperature,
    num_ctx=cfg.num_ctx,
    num_predict=cfg.num_predict,
    keep_alive=cfg.keep_alive
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifecycle: Startup pool initialization
    await db.connect()
    yield
    # Lifecycle: Shutdown pool cleanup
    await db.disconnect()

app = FastAPI(title="Enterprise Postgres Ollama Engine", version="6.0", lifespan=lifespan)

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    memory = PreferenceAwarePostgresMemory(
        db=db,
        user_id=req.user_id,
        session_id=req.session_id,
        system_prompt=cfg.system_prompt,
        max_history=cfg.max_history_messages,
        model_name=cfg.model_name
    )

    # 1. Retrieve prior conversation context FIRST
    context = await memory.get_context()

    # 2. Append current user message to payload
    context.append({"role": "user", "content": req.message})

    # 3. Save user message to PostgreSQL database
    await memory.add_message("user", req.message)

    # 4. Extract facts asynchronously in the background
    memory.extract_facts_in_background(req.message)

    try:
        # 5. Generate completion
        response_text = await agent.generate_response(context)

        # 6. Save assistant response to DB
        await memory.add_message("assistant", response_text)

        known_facts = await db.get_user_facts(req.user_id)

        return {
            "user_id": req.user_id,
            "session_id": req.session_id,
            "response": response_text,
            "active_user_facts": known_facts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/facts")
async def get_user_facts_endpoint(user_id: str):
    facts = await db.get_user_facts(user_id)
    return {"user_id": user_id, "facts": facts}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)