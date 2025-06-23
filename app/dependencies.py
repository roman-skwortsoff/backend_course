from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config import settings

class MongoLogger:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def save(self, log_data: dict):
        await self.db.request_logs.insert_one(log_data)

async def get_mongo_logger():
    from app.connectors.mongo_connector import get_mongodb  # Ленивый импорт
    db = await get_mongodb()
    return MongoLogger(db)