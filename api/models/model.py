from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


# Base models
class ModelBase(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., min_length=1, max_length=255)


class ModelCreate(ModelBase):
    pass


class ModelRead(ModelBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ModelDelete(BaseModel):
    id: uuid.UUID


class Model(ModelBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Response models
class ModelResponse(BaseModel):
    model: Model
