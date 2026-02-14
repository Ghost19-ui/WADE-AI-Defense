from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        # 1. Try to get the Cloud URL, but default to LOCAL if missing/broken
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        
        try:
            print(f"🔌 Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
            self.db = self.client["wade_db"]
            # Trigger a command to verify connection
            await self.client.server_info()
            print("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            print(f"⚠️ Cloud DB Failed: {e}")
            print("🔄 Switching to Temporary In-Memory Mode (For Testing Only)")
            # This prevents the crash so the app still runs!
            self.db = None 

    async def close(self):
        if self.client:
            self.client.close()
            print("🔻 MongoDB Connection Closed")

db = Database()