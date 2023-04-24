from fastapi.routing import APIRouter
from app.core.config import settings

from app.api.api_v1.endpoints import schema_info_service
from app.api.api_v1.endpoints import kafka_topics_service
from app.api.api_v1.endpoints import subscription_service

user_api_router = APIRouter()
user_api_router.include_router(schema_info_service.api_router, prefix=settings.API_VERSION_STR, tags=["Schema APIs"])
user_api_router.include_router(kafka_topics_service.api_router, prefix=settings.API_VERSION_STR, tags=['Topic APIs'])
user_api_router.include_router(subscription_service.api_router, prefix=settings.API_VERSION_STR, tags=['Subscription APIs'])
