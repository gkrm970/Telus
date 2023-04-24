from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SchemaType(str, Enum):
    AVRO: str = 'AVRO'
    JSON: str = 'JSON'
    XML: str = 'XML'
    EMPTY: None = ''


class SchemaInfo(BaseModel):
    #bus_id: Optional[int] = Field(description=' bus id', example='1')
    name: Optional[str] = Field(title='SchemaName', description='Name of the schema', example='test')
    type: Optional[SchemaType] = Field(description='The type of the schema definition.', example='AVRO')

    definition: Optional[str] = Field(
        description='The definition of the schema. This should contain a string representing the full definition of '
                    'the schema that is a valid schema definition of the type specified in type.',
        example='{\"type\":\"record\",\"name\":\"Record\",\"fields\":[{\"name\":\"color\",\"type\":\"string\"},'
                '{\"name\":\"value\",\"type\":\"string\"}]} '
        )
    class Config:  
        use_enum_values = True  # <--


class SchemaInfoResponse(BaseModel):
    #bus_id: Optional[int] = Field(
    #    description=' bus id', example='1'
    #)
    name: Optional[str] = Field(title='SchemaName', description='Name of the schema', example='test')
    type: Optional[SchemaType] = Field(description='The type of the schema definition.', example='AVRO')

    definition: Optional[str] = Field(

        description='The definition of the schema. This should contain a string representing the full definition of '
                    'the schema that is a valid schema definition of the type specified in type.',
        example='{\"type\":\"record\",\"name\":\"Record\",\"fields\":[{\"name\":\"color\",\"type\":\"string\"},'
                '{\"name\":\"value\",\"type\":\"string\"}]} '
    )
    revisionId: Optional[str] = Field(
        description='Output only. Immutable. The revision ID of the schema.Output only. Immutable. The revision ID of the schema.', example= '302daeb3', readOnly= 'true'
    )
    revisionCreateTime: Optional[str] = Field(
         description='Output only. The timestamp that the revision was created', example= '2023-01-27T17:28:13.759Z', readOnly= 'true'
    )


class SchemaList(BaseModel):
    schemas: Optional[List[SchemaInfoResponse]]
