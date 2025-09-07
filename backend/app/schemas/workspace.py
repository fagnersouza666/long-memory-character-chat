from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkspaceBase(BaseModel):
    name: str
    organizationId: int

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(WorkspaceBase):
    pass

class Workspace(WorkspaceBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class WorkspaceUserBase(BaseModel):
    userId: int
    workspaceId: int
    role: str = "member"

class WorkspaceUserCreate(WorkspaceUserBase):
    pass

class WorkspaceUser(WorkspaceUserBase):
    class Config:
        from_attributes = True