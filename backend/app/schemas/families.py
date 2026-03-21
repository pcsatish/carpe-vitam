"""Family and family member schemas."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.family import FamilyMemberRole


class FamilyCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class FamilySchema(BaseModel):
    id: str
    name: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyMemberCreateSchema(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(None, max_length=20)
    role: FamilyMemberRole = FamilyMemberRole.MEMBER
    user_id: Optional[str] = None


class FamilyMemberSchema(BaseModel):
    id: str
    family_id: str
    user_id: Optional[str]
    display_name: str
    date_of_birth: Optional[date]
    sex: Optional[str]
    role: FamilyMemberRole
    joined_at: datetime

    class Config:
        from_attributes = True
