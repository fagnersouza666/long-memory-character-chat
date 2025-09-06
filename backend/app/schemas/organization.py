from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

class OrganizationUserBase(BaseModel):
    userId: int
    organizationId: int
    role: str = "member"

class OrganizationUserCreate(OrganizationUserBase):
    pass

class OrganizationUser(OrganizationUserBase):
    class Config:
        orm_mode = True