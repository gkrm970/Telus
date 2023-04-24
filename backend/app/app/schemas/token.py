from typing import Optional
from pydantic import BaseModel, UUID4, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    email: EmailStr = EmailStr("test@test.com")
    preferred_username: str = ""
    name: str = ""
    given_name: str = ""
    family_name: str = ""
    sub: Optional[UUID4] = None
    aud: list = []
    resource_access: dict = {}