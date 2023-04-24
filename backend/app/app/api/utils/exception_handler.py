from fastapi.applications import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


async def http_exception_handler(
    _request: Request, exc: HTTPException,
) -> JSONResponse:

    payload = {"message": exc.detail}

    return JSONResponse(content=payload, status_code=exc.status_code)


async def request_validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:

    payload = {"message": "Validation Error", "detail": exc.errors()}

    return JSONResponse(content=payload, status_code=HTTP_400_BAD_REQUEST)


def register_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
    return app


class TopicNotFoundException(Exception):
    def __init__(self, topic_name):
        self.topic_name = topic_name

    def __str__(self):
        return f"Topic '{self.topic_name}' not found in the Kafka topic table list. Create new topic using this " \
               f"endpoint " \
               f"/pubsub/v1/topics/TopicName"
