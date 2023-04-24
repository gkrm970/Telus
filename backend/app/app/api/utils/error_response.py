from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from app.schemas.response import ErrorMessage, UnauthorizedMessage

"""
Usage: https://fastapi.tiangolo.com/advanced/additional-responses/
"""
default_error_responses = {
    HTTP_400_BAD_REQUEST: {"description": "Validation Error"},
    HTTP_401_UNAUTHORIZED: {
        "model": UnauthorizedMessage,
        "description": "Unauthorized.",
    },
    HTTP_403_FORBIDDEN: {"model": ErrorMessage, "description": "Permission Denied."},
    HTTP_404_NOT_FOUND: {
        "model": ErrorMessage,
        "description": "Provided resource not found.",
    },
}
create_error_responses = dict(default_error_responses)
create_error_responses[HTTP_409_CONFLICT] = {
    "model": ErrorMessage,
    "description": "Resource already exist.",
}
