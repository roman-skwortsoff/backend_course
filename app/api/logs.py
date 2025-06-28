import uuid
from datetime import datetime
from typing import Dict, List, Optional
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel
from fastapi import HTTPException, Query, APIRouter, Body, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.setup import mongo_manager, elasticsearch_manager

router = APIRouter(prefix="/logs", tags=["Логи"])


@router.get(
    "/mongo", summary="Логи из MongoDB", response_model=List[Dict]
)
async def get_request_logs( limit: int = Query(default=100, description="Maximum number of items to return"), db: AsyncIOMotorDatabase = Depends(mongo_manager.get_mongodb) ):
    try:
        cursor = db.request_logs.find().limit(limit)
        data = await cursor.to_list(length=limit)
        
        for item in data:
            item["_id"] = str(item["_id"])
            
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )

@router.get("/elastic", summary="Логи из Elasticsearch")
async def get_logs_from_elasticsearch(
    method: Optional[str] = Query(None, description="Фильтрация по HTTP-методу"),
    limit: int = Query(10, ge=1, le=100, description="Максимум 100 логов"),
    es_client: AsyncElasticsearch = Depends(elasticsearch_manager.get_client_dependency)
):
    try:
        query_body = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        if method:
            query_body["query"]["bool"]["must"].append({
                "match": {"method": method}
            })

        response = await es_client.search(index="request_logs", body=query_body)

        hits = response["hits"]["hits"]
        logs = [hit["_source"] for hit in hits]

        return {
            "count": len(logs),
            "logs": logs
        }

    except Exception as e:
        return {"error": str(e)}


class TestData(BaseModel):
    test_field: str = "test_value"
    timestamp: datetime = datetime.now()

@router.post(
    "/test-connection",
    summary="Тест подключения и записи в MongoDB",
    status_code=status.HTTP_201_CREATED,
    response_model=dict
)
async def test_mongo_connection(
    db: AsyncIOMotorDatabase = Depends(mongo_manager.get_mongodb)
):
    """
    Проверяет подключение к MongoDB путем записи тестового документа.
    Возвращает результат операции и записанные данные.
    """
    try:
        # 1. Проверяем подключение
        await db.command("ping")
        
        # 2. Создаем тестовый документ
        test_doc = {
            "_id": str(uuid.uuid4()),
            **TestData().model_dump(),
            "description": "Тестовый документ для проверки MongoDB"
        }
        
        # 3. Пытаемся записать
        result = await db.test_connection.insert_one(test_doc)
        
        # 4. Проверяем результат
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Документ не был записан"
            )
            
        # 5. Возвращаем результат
        return {
            "status": "success",
            "message": "Тестовый документ успешно записан",
            "document_id": str(result.inserted_id),
            "document": test_doc
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка тестирования MongoDB: {str(e)}"
        )