from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    fileType: str
    workspaceId: int
    tags: Optional[List[str]] = []

class DocumentCreate(DocumentBase):
    filePath: str
    size: Optional[int] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None

class Document(DocumentBase):
    id: int
    filePath: str
    size: Optional[int] = None
    authorId: int
    uploadDate: datetime
    status: str
    updatedAt: datetime

    class Config:
        orm_mode = True

class DocumentChunkBase(BaseModel):
    documentId: int
    content: str

class DocumentChunkCreate(DocumentChunkBase):
    embedding: Optional[List[float]] = None

class DocumentChunk(DocumentChunkBase):
    id: int
    createdAt: datetime

    class Config:
        orm_mode = True