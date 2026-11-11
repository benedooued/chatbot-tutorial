import asyncpg
from typing import Dict, List, Optional

class PostgresDatabaseManager:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initializes an asynchronous connection pool."""
        self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=2, max_size=10)

    async def disconnect(self):
        """Closes the connection pool gracefully."""
        if self.pool:
            await self.pool.close()

    async def save_message(self, session_id: str, role: str, content: str, name: Optional[str] = None):
        query = """
            INSERT INTO messages (session_id, role, content, name)
            VALUES ($1, $2, $3, $4)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, session_id, role, content, name)

    async def save_user_fact(self, user_id: str, fact_key: str, fact_value: str):
        query = """
            INSERT INTO user_facts (user_id, fact_key, fact_value, updated_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (user_id, fact_key) DO UPDATE SET
                fact_value = EXCLUDED.fact_value,
                updated_at = NOW()
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, fact_key.strip().lower(), fact_value.strip())

    async def get_user_facts(self, user_id: str) -> Dict[str, str]:
        query = "SELECT fact_key, fact_value FROM user_facts WHERE user_id = $1"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return {r["fact_key"]: r["fact_value"] for r in rows}

    async def get_recent_messages(self, session_id: str, limit: int) -> List[dict]:
        query = """
            SELECT role, content, name FROM (
                SELECT role, content, name, id FROM messages
                WHERE session_id = $1
                ORDER BY id DESC
                LIMIT $2
            ) sub ORDER BY id ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, session_id, limit)
            messages = []
            for r in rows:
                msg = {"role": r["role"], "content": r["content"]}
                if r["name"]:
                    msg["name"] = r["name"]
                messages.append(msg)
            return messages