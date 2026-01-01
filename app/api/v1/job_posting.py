from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.job_posting import JobPosting
from app.schemas.job_posting import JobPostingCreate, JobPostingResponse

router = APIRouter()


@router.post("/", response_model=JobPostingResponse)
async def create_job_posting(
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    db_job = JobPosting(
        title=job_posting.title,
        description=job_posting.description,
        required_skills=job_posting.required_skills,
        preferred_skills=job_posting.preferred_skills,
        min_experience_years=job_posting.min_experience_years,
        required_education=job_posting.required_education
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.get("/", response_model=List[JobPostingResponse])
async def list_job_postings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all job postings"""
    job_postings = db.query(JobPosting).offset(skip).limit(limit).all()
    return job_postings


@router.get("/{job_posting_id}", response_model=JobPostingResponse)
async def get_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific job posting"""
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job_posting


@router.put("/{job_posting_id}", response_model=JobPostingResponse)
async def update_job_posting(
    job_posting_id: int,
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db)
):
    """Update a job posting"""
    db_job = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    db_job.title = job_posting.title
    db_job.description = job_posting.description
    db_job.required_skills = job_posting.required_skills
    db_job.preferred_skills = job_posting.preferred_skills
    db_job.min_experience_years = job_posting.min_experience_years
    db_job.required_education = job_posting.required_education
    
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.delete("/{job_posting_id}")
async def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db)
):
    """Delete a job posting"""
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    db.delete(job_posting)
    db.commit()
    return {"message": "Job posting deleted successfully"}

