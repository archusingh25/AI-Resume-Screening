from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScreeningRequest(BaseModel):
    resume_id: int
    job_posting_id: int


class BatchScreeningRequest(BaseModel):
    job_posting_id: int
    resume_ids: Optional[List[int]] = None


class ScreeningResultResponse(BaseModel):
    id: int
    resume_id: int
    job_posting_id: int
    overall_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    preferred_skills_matched: Optional[List[str]] = None
    bias_score: Optional[float] = None
    anonymized_score: Optional[float] = None
    rank: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

