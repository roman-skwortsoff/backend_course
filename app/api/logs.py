import uuid
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
from fastapi import HTTPException, Query, APIRouter, Body, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.setup import mongo_manager

router = APIRouter(prefix="/logs", tags=["Логи"])


@router.get(
    "/", summary="Логи из MongoDB", response_model=List[Dict]
)
async def get_test_connection( limit: int = Query(default=100, description="Maximum number of items to return"), db: AsyncIOMotorDatabase = Depends(mongo_manager.get_mongodb) ):
    try:
        cursor = db.test_connection.find().limit(limit)
        data = await cursor.to_list(length=limit)
        
        for item in data:
            item["_id"] = str(item["_id"])
            
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )
    
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