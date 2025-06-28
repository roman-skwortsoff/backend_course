from elasticsearch import AsyncElasticsearch
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Dict, Any
import logging
from elasticsearch.helpers import async_bulk


logger = logging.getLogger(__name__)


async def transfer_logs_to_elasticsearch(
    mongo_db: AsyncIOMotorDatabase,
    es_client: AsyncElasticsearch,
    index_name: str = "request_logs"
) -> None:
    try:
        logger.info("🔁 Начинаем перенос логов из MongoDB в Elasticsearch...")

        cursor = mongo_db.request_logs.find({
            "method": {"$ne": "GET"},
            "transferred_to_es": {"$ne": True}
        })

        logs = await cursor.to_list(length=None)

        logger.debug(f"🔍 Найдено логов для переноса: {len(logs)}")

        if not logs:
            logger.info("ℹ️ Нет новых логов для переноса")
            return

        actions = []
        ids = []

        for log in logs:
            log_id = log["_id"]
            ids.append(log_id)

            logger.debug(f"📄 Обрабатываем лог: {log}")

            source = dict(log)
            source.pop("_id", None)  # удаляем поле _id из содержимого

            actions.append({
                "_index": index_name,
                "_id": str(log_id),     # используем _id как метаданные
                "_source": source,      # без _id внутри документа
            })

        logger.info(f"📦 Подготовлено {len(actions)} документов для bulk-запроса")

        # Отправляем bulk
        success, errors = await async_bulk(es_client, actions, raise_on_error=False)

        logger.info(f"📤 Отправка завершена: success={success}, errors={len(errors)}")

        if errors:
            logger.warning(f"⚠ Ошибки при индексации {len(errors)} документов:")
            for err in errors[:5]:  # выводим первые 5 ошибок
                logger.warning(f"⛔ {err}")

        if success:
            update_result = await mongo_db.request_logs.update_many(
                {"_id": {"$in": ids}},
                {"$set": {"transferred_to_es": True}}
            )
            logger.info(f"📝 Обновлено {update_result.modified_count} документов в MongoDB")

        logger.info(f"✅ Успешно перенесли {success} логов в Elasticsearch")

    except Exception as e:
        logger.error(f"🔥 Ошибка при переносе логов: {e}", exc_info=True)
        raise