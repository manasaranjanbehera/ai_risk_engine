# scripts/test_db.py
import sys
from pathlib import Path
from sqlalchemy import text

# Ensure project root is on the path when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from app.infrastructure.database.session import engine

async def test_connection():
    async with engine.begin() as conn:
        #result = await conn.execute("SELECT 1")
        result = await conn.execute(text("SELECT 1"))
        print("DB Connected:", result.scalar())

asyncio.run(test_connection())
