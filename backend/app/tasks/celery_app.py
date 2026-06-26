from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "tamor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.rating_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Samarkand",
    enable_utc=True,
    beat_schedule={
        "daily-rating-recompute": {
            "task": "app.tasks.rating_tasks.compute_ratings_daily",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)
