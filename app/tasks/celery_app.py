from celery import Celery

from app.config import settings

celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "app.tasks.tasks"
    ],
)

celery_instance.conf.beat_schedule = {
    "nazvanie": {
        "task": "booking_today_checkin",
        "schedule": 5, #лучше использовать crontab и задать время согласно crontab guru
    }
}