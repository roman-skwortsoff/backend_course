import logging
import asyncio

import redis.asyncio as redis
from redis.exceptions import RedisError


class RedisManager:
    def __init__(self, host: str, port: int, max_retries: int = 7, retry_delay: int = 2):
        self.host = host
        self.port = port
        self.redis = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def connect(self):
        for attempt in range(1, self.max_retries + 1):
            logging.info(f"[Redis] Попытка {attempt}/{self.max_retries} подключения к {self.host}:{self.port}")
            self.redis = redis.Redis(host=self.host, port=self.port)
            try:
                pong = await self.redis.ping()
                if pong:
                    logging.info(f"[Redis] Успешное подключение к {self.host}:{self.port}")
                    return
            except RedisError as e:
                logging.warning(f"[Redis] Ошибка подключения: {e}")
            await asyncio.sleep(self.retry_delay)

        logging.error(f"[Redis] Не удалось подключиться после {self.max_retries} попыток.")
        raise ConnectionError("Подключение к Redis не удалось.")

    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
