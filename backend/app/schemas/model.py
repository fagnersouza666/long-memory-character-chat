from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    displayName: str
    prompt: str
    isActive: Optional[bool] = True

class ModelCreate(ModelBase):
    pass

class ModelUpdate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True