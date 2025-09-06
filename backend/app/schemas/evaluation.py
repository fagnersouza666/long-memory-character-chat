from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvaluationBase(BaseModel):
    employeeId: int
    period: str
    content: str
    score: Optional[float] = None

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationUpdate(BaseModel):
    content: Optional[str] = None
    score: Optional[float] = None

class Evaluation(EvaluationBase):
    id: int
    evaluatorId: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True