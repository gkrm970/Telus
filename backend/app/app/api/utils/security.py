import base64
from app.core.config import settings
import logging
logger = logging.getLogger(settings.LOGGER_APP_NAME)

from typing import Optional

import jwt
from fastapi.param_functions import Security
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowClientCredentials
from fastapi.param_functions import Form
from fastapi.security.oauth2 import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jwt import PyJWTError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings
from app.schemas.token import TokenPayload

ALGORITHM = "RS256"


class OAuth2ClientBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = "",
        scopes: dict = {},
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials=OAuthFlowClientCredentials(**{"tokenUrl": tokenUrl, "scopes": scopes})
        )

        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


class OAuth2CustomRequestForm:
    def __init__(
        self,
        grant_type: str = Form("client_credentials"),
        scope: str = Form(""),
        client_id: str = Form(None),
        client_secret: str = Form(None),
    ):
        self.grant_type = grant_type
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


oauth2_scheme = OAuth2ClientBearer(tokenUrl=settings.AUTH_TOKEN_URL)


def validate_token(token: str = Security(oauth2_scheme),):
    try:
        payload = jwt.decode(
            token,
            str(base64.b64decode(settings.SECRET_KEY), "utf-8"),
            algorithms=[ALGORITHM],
            audience="account",
            verify=True,
        )
        # logger.debug("decrypted token info:" + repr(payload))
        TokenPayload(**payload)
    except PyJWTError as e:
        logger.debug("PyJWTError: " + str(e))
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=str(e))

    return payload
