from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentProcessingTaskBase(BaseModel):
    document_id: int
    user_id: int
    status: str = "pending"  # pending, processing, completed, failed
    priority: int = 1  # 1-10, where 10 is highest priority

class DocumentProcessingTaskCreate(DocumentProcessingTaskBase):
    pass

class DocumentProcessingTaskUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None  # 0-100
    error_message: Optional[str] = None
    result_document_id: Optional[int] = None

class DocumentProcessingTask(DocumentProcessingTaskBase):
    id: int
    progress: int = 0
    error_message: Optional[str] = None
    result_document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class DocumentProcessingResult(BaseModel):
    task_id: int
    document_id: int
    chunks_created: int
    embeddings_generated: int
    processing_time_seconds: float
    status: str  # success, partial_success, failed
    error_message: Optional[str] = None

class DocumentChunkWithEmbedding(BaseModel):
    document_id: int
    content: str
    embedding: List[float]
    position: int

class ProcessingQueueStatus(BaseModel):
    total_tasks: int
    pending_tasks: int
    processing_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_processing_time: float