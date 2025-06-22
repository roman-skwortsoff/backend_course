from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]

    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    REDIS_HOST: str
    REDIS_POST: int

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_POST}"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    KAFKA_BOOTSTRAP_SERVERS: str

    MONGODB_NAME: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str

    @property
    def MONGO_URL(self):
        return f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@mongo:27017/{self.MONGODB_NAME}?authSource={self.MONGODB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
