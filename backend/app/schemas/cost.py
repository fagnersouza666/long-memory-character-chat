from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UsageRecordBase(BaseModel):
    userId: int
    organizationId: Optional[int] = None
    feature: str  # "document_processing", "search", "evaluation_creation", etc.
    tokens_used: Optional[int] = None
    cost: float

class UsageRecordCreate(UsageRecordBase):
    pass

class UsageRecord(UsageRecordBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class CostDashboard(BaseModel):
    total_cost: float
    daily_cost: float
    weekly_cost: float
    monthly_cost: float
    top_features: list
    usage_by_feature: dict

class CostHistory(BaseModel):
    records: list[UsageRecord]
    total_records: int
    total_cost: float