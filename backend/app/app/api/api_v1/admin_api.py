from fastapi.routing import APIRouter
from app.core.config import settings

from app.api.api_v1.endpoints import auth_type_service
from app.api.api_v1.endpoints import schema_registry_service
from app.api.api_v1.endpoints import schema_info_service
from app.api.api_v1.endpoints import scheduler_service
from app.api.api_v1.endpoints import kafka_topics_service
from app.api.api_v1.endpoints import kafka_buses_service

admin_api_router = APIRouter()
admin_api_router.include_router(auth_type_service.router, prefix=settings.API_VERSION_STR, tags=["Authentication APIs"])
admin_api_router.include_router(schema_registry_service.router, prefix=settings.API_VERSION_STR, tags=["Schema Registry APIs"])
admin_api_router.include_router(scheduler_service.router, prefix=settings.API_VERSION_STR, tags=['Scheduler APIs'])
admin_api_router.include_router(kafka_buses_service.router, prefix=settings.API_VERSION_STR, tags=['Bus APIs'])
