from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from fastapi import Request

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ai_ocr_db")


async def init_db(db) -> None:
    """Initialize database: create indexes and any startup migrations.

    Expects a Motor `Database` instance (e.g. AsyncIOMotorClient().dbname).
    """
    try:
        # Users: unique email
        await db.users.create_index("email", unique=True)
        # Documents: index by user and created time
        await db.documents.create_index("user_id")
        await db.documents.create_index("created_at")
    except Exception:
        # If indexes already exist or an index creation fails, continue.
        pass


async def get_db(request: Request):
    """FastAPI dependency that returns the Motor database instance.

    Usage: db = Depends(get_db)  -> db.documents, db.users, etc.
    """
    return request.app.mongodb