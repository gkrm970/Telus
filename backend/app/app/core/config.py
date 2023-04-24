import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyUrl, AnyHttpUrl, BaseSettings, HttpUrl, PostgresDsn, validator
from starlette.middleware import Middleware
from starlette_context.middleware import ContextMiddleware
from starlette_context import plugins


class Settings(BaseSettings):

    DOMAIN: str = "localhost"
    VERSION: str = "1.0.0"
    API_VERSION:str = "v1"
    #API_NAME: str = "pubsub_discoverer"
    API_NAME: str = "pubsub"
    API_VERSION_STR: str = f"/{API_NAME}/" + API_VERSION

    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if v is None or len(v) == 0:
            return None
        return v



    MIDDLEWARES: list = [
        Middleware(
            ContextMiddleware,
            plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
        )
    ]

    SSL_VERIFY: Any = True
    AUTH_REDIRECT_URL: str = "/docs"
    JWK: str = ""
    AUTH_BASE_URL: AnyHttpUrl
    AUTH_AUTHORIZATION_URL: AnyHttpUrl = None
    AUTH_TOKEN_URL: AnyHttpUrl = None
    AUTH_CERTS_URL: AnyHttpUrl = None

    @validator("AUTH_AUTHORIZATION_URL", pre=True)
    def assemble_auth_authorization_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if values.get("AUTH_AUTHORIZATION_URL"):
            return values.get("AUTH_AUTHORIZATION_URL")
        else:
            return f"{values.get('AUTH_BASE_URL')}/auth"
    @validator("AUTH_TOKEN_URL", pre=True)
    def assemble_auth_token_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if values.get("AUTH_TOKEN_URL"):
            return values.get("AUTH_TOKEN_URL")
        else:
            return f"{values.get('AUTH_BASE_URL')}/token"
    @validator("AUTH_CERTS_URL", pre=True)
    def assemble_auth_certs_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if values.get("AUTH_CERTS_URL"):
            return values.get("AUTH_CERTS_URL")
        else:
            return f"{values.get('AUTH_BASE_URL')}/certs"


    LOGGER_APP_NAME: str = "COOKIECUTTER"
    LOGGER_APP_CODE: str = "0098"
    LOGGER_HANDLER_NAME = "console"
    TINAA_LOG_LEVEL: str
    LOGGER_FORMAT = "[%(asctime)s] [%(levelname)s] [{}] [{}] [%(filename)s -> %(funcName)s()] [%(lineno)s] %(message)s"
    LOGGER_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    class Config:
        case_sensitive = True


settings = Settings()       # type: ignore
