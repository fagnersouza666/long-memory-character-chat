from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class Conversation(BaseModel):
    id: str
    user_id: int
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class ConversationCreate(BaseModel):
    title: str
    metadata: Optional[Dict[str, Any]] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MemorySummary(BaseModel):
    id: str
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    relevance_score: float

class MemorySummaryCreate(BaseModel):
    content: str
    relevance_score: float = 1.0

class Context(BaseModel):
    conversation_id: str
    user_id: int
    relevant_documents: List[str]
    relevant_evaluations: List[str]
    memory_summaries: List[MemorySummary]
    created_at: datetime