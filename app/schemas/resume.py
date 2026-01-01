from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ResumeBase(BaseModel):
    filename: str
    original_text: str


class ResumeCreate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    id: int
    parsed_data: Optional[Dict] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

