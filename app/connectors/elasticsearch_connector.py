from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class ElasticsearchManager:
    def __init__(self, elasticsearch_url):
        self._client = None
        self.es_url = elasticsearch_url

    async def connect(self):
        """Установка подключения к Elasticsearch"""
        try:
            self._client = AsyncElasticsearch(
                hosts=[self.es_url],
                verify_certs=False,
                sniff_on_start=True
            )
            if await self._client.ping():
                logger.info("Connected to Elasticsearch")
            else:
                raise ConnectionError("Failed to ping Elasticsearch")
        except Exception as e:
            logger.error(f"Elasticsearch connection error: {e}")
            raise

    async def close(self):
        """Закрытие подключения"""
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