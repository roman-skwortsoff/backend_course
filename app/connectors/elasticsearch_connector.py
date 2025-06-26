from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class ElasticsearchManager:
    def __init__(self, url: str):
        self.es_url = url
        self._client: AsyncElasticsearch | None = None

    async def connect(self):
        self._client = AsyncElasticsearch(
            hosts=[self.es_url],
            verify_certs=False,
            sniff_on_start=False,
        )

        try:
            print(f"🔍 Trying to connect to {self.es_url}")
            is_alive = await self._client.ping()
        except Exception as e:
            raise ConnectionError(f"Ping failed: {e}")

        if not is_alive:
            raise ConnectionError("Failed to ping Elasticsearch")

        print("✅ Connected to Elasticsearch")

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("Elasticsearch connection closed")

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[AsyncElasticsearch, None]:
        if self._client is None:
            await self.connect()
    
        try:
            yield self._client
        except Exception as e:
            logger.error(f"Elasticsearch operation failed: {e}")
            raise
