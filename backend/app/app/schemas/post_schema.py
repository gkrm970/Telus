from pydantic import BaseModel, Field


class SubscriptionPull(BaseModel):
    maxMessages: int = Field(example='example: 1', title='maxMessages')
