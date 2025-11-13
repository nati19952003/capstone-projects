import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from Backend.database.database import MONGODB_URL, DB_NAME, init_db

async def setup_database():
    """Initialize database with indexes"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    try:
        # Initialize database (creates indexes)
        await init_db(db)
        
        # Create additional indexes for better query performance
        await db.documents.create_index("filename")
        await db.documents.create_index("status")
        await db.documents.create_index("user_id")
        
        print("MongoDB indexes created successfully!")
        print(f"Connected to: {MONGODB_URL}")
        print(f"Database: {DB_NAME}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(setup_database())
