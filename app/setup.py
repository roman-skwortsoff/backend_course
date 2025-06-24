from app.connectors.mongo_connector import MongoManager
from app.connectors.redis_connector import RedisManager
from app.connectors.elasticsearch_connector import ElasticsearchManager
from app.config import settings

redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_POST,
)

mongo_manager = MongoManager(
    mongo_url = settings.MONGO_URL,
    db_name = settings.MONGODB_NAME)

elasticsearch_manager = ElasticsearchManager(settings.ELASTICSEARCH_URL)