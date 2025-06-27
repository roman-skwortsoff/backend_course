import asyncio
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

        last_error = None
        for attempt in range(10):
            print(f"🔁 Elasticsearch ping attempt {attempt + 1}")
            try:
                if await self._client.ping():
                    print("✅ Connected to Elasticsearch")
                    break
                else:
                    print("⚠️ Ping returned False")
            except Exception as e:
                last_error = e
                print(f"⛔ Ping raised exception: {e}")
        
            await asyncio.sleep(3)
        else:
            raise ConnectionError(f"❌ Could not connect to Elasticsearch: {last_error or 'ping returned False'}")
    
        last_info_error = None
        for attempt in range(10):
            print(f"🔁 Elasticsearch info attempt {attempt + 1}")
            try:
                info = await self._client.info()
                if info:
                    print("ℹ️ Elasticsearch info:", info)
                    break
                else:
                    print("⚠️ Info returned empty")
            except Exception as e:
                last_info_error = e
                print(f"⛔ Info raised exception: {e}")
        
            await asyncio.sleep(3)
        else:
            raise ConnectionError(f"❌ Failed to retrieve Elasticsearch info after 10 attempts: {last_info_error or 'info returned empty'}")


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
