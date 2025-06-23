from fastapi import Request
from datetime import datetime, timezone
import time
import json
from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    start_time = datetime.now(timezone.utc)
    log_data: Dict[str, Any] = {
        "timestamp": start_time,
        "path": str(request.url.path),
        "method": request.method,
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }

    try:
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            try:
                body = await request.json()
                log_data["request_body"] = _sanitize_body(body)  # Очистка чувствительных данных
            except json.JSONDecodeError:
                body = await request.body()
                log_data["request_body"] = str(body)[:1000]  # Обрезаем большие бинарные данные

        response = await call_next(request)
        
        log_data.update({
            "status_code": response.status_code,
            "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
            "response_size": int(response.headers.get("content-length", 0))
        })

        db = request.app.state.mongo_db
        if db is not None:
            await db.request_logs.insert_one(log_data)
        else:
            logger.warning("MongoDB connection not available")

        return response

    except Exception as e:
        log_data.update({
            "status_code": 500,
            "error": str(e),
            "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        })
        logger.error(f"Request failed: {log_data}")
        raise

def _sanitize_body(body: dict) -> dict:
    SENSITIVE_KEYS = {"password", "token", "credit_card"}
    if not isinstance(body, dict):
        return body
        
    return {
        k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS else v
        for k, v in body.items()
    }