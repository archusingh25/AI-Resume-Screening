from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobPostingBase(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = None
    required_education: Optional[str] = None


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingResponse(JobPostingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

