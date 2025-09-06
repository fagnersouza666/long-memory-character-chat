from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RateLimitBase(BaseModel):
    userId: Optional[int] = None
    organizationId: Optional[int] = None
    feature: str  # "document_upload", "search", "evaluations", etc.
    limit: int
    window_seconds: int  # Time window in seconds (e.g., 3600 for 1 hour)

class RateLimitCreate(RateLimitBase):
    pass

class RateLimit(RateLimitBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

class RateLimitStatus(BaseModel):
    feature: str
    limit: int
    remaining: int
    reset_time: datetime
    is_limited: bool