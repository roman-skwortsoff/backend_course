from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from app.config import settings


class MongoManager:
    def __init__(
        self,
        mongo_url: str,
        db_name: str,
        max_pool_size: int = 100
    ):
        self._mongo_url = mongo_url
        self._db_name = db_name
        self._max_pool_size = max_pool_size
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(
                self._mongo_url,
                maxPoolSize=self._max_pool_size,
                serverSelectionTimeoutMS=5000  # Таймаут подключения 5 сек
            )
            self._db = self._client[self._db_name]
            try:
                await self._db.command("ping")
                print(f"✅ MongoDB connected to {self._db_name}")
            except Exception as e:
                await self.close()
                raise ConnectionError(f"MongoDB connection failed: {e}")

    async def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("🚪 MongoDB connection closed")

    async def get_mongodb(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            await self.connect()
        try:
            return self._db
        except Exception as e:
            print(f"⚠️ MongoDB error: {e}")
            raise