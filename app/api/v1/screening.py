from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.resume import Resume
from app.models.job_posting import JobPosting
from app.models.screening_result import ScreeningResult
from app.services.scorer import ResumeScorer
from app.services.bias_reducer import BiasReducer
from app.services.skill_matcher import SkillMatcher
from app.schemas.screening import ScreeningResultResponse, ScreeningRequest, BatchScreeningRequest

router = APIRouter()
scorer = ResumeScorer()
bias_reducer = BiasReducer()
skill_matcher = SkillMatcher()


@router.post("/screen", response_model=ScreeningResultResponse)
async def screen_resume(
    request: ScreeningRequest,
    db: Session = Depends(get_db)
):
    """Screen a single resume against a job posting"""
    # Get resume and job posting
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    job_posting = db.query(JobPosting).filter(JobPosting.id == request.job_posting_id).first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Calculate scores
    score_result = scorer.calculate_score(resume, job_posting)
    
    # Calculate bias score
    resume_data = {
        "original_text": resume.original_text,
        "parsed_data": resume.parsed_data
    }
    bias_score = bias_reducer.calculate_bias_score(resume_data)
    anonymized_score = bias_reducer.get_anonymized_score(
        score_result["overall_score"],
        bias_score
    )
    
    # Create or update screening result
    existing_result = db.query(ScreeningResult).filter(
        ScreeningResult.resume_id == request.resume_id,
        ScreeningResult.job_posting_id == request.job_posting_id
    ).first()
    
    if existing_result:
        # Update existing result
        existing_result.overall_score = score_result["overall_score"]
        existing_result.skill_match_score = score_result["skill_match_score"]
        existing_result.experience_score = score_result["experience_score"]
        existing_result.education_score = score_result["education_score"]
        existing_result.matched_skills = score_result["matched_skills"]
        existing_result.missing_skills = score_result["missing_skills"]
        existing_result.preferred_skills_matched = score_result["preferred_skills_matched"]
        existing_result.bias_score = bias_score
        existing_result.anonymized_score = anonymized_score
        
        db.commit()
        db.refresh(existing_result)
        return existing_result
    else:
        # Create new result
        screening_result = ScreeningResult(
            resume_id=request.resume_id,
            job_posting_id=request.job_posting_id,
            overall_score=score_result["overall_score"],
            skill_match_score=score_result["skill_match_score"],
            experience_score=score_result["experience_score"],
            education_score=score_result["education_score"],
            matched_skills=score_result["matched_skills"],
            missing_skills=score_result["missing_skills"],
            preferred_skills_matched=score_result["preferred_skills_matched"],
            bias_score=bias_score,
            anonymized_score=anonymized_score
        )
        
        db.add(screening_result)
        db.commit()
        db.refresh(screening_result)
        return screening_result


@router.post("/screen-batch")
async def screen_multiple_resumes(
    request: BatchScreeningRequest,
    db: Session = Depends(get_db)
):
    """Screen multiple resumes against a job posting and return ranked results"""
    job_posting = db.query(JobPosting).filter(JobPosting.id == request.job_posting_id).first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Get all resumes or filter by IDs
    if request.resume_ids:
        resumes = db.query(Resume).filter(Resume.id.in_(request.resume_ids)).all()
    else:
        resumes = db.query(Resume).all()
    
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")
    
    # Screen all resumes
    results = []
    for resume in resumes:
        score_result = scorer.calculate_score(resume, job_posting)
        
        resume_data = {
            "original_text": resume.original_text,
            "parsed_data": resume.parsed_data
        }
        bias_score = bias_reducer.calculate_bias_score(resume_data)
        anonymized_score = bias_reducer.get_anonymized_score(
            score_result["overall_score"],
            bias_score
        )
        
        results.append({
            "resume_id": resume.id,
            "resume_filename": resume.filename,
            "overall_score": score_result["overall_score"],
            "skill_match_score": score_result["skill_match_score"],
            "experience_score": score_result["experience_score"],
            "education_score": score_result["education_score"],
            "matched_skills": score_result["matched_skills"],
            "missing_skills": score_result["missing_skills"],
            "preferred_skills_matched": score_result["preferred_skills_matched"],
            "bias_score": bias_score,
            "anonymized_score": anonymized_score
        })
    
    # Rank results
    ranked_results = skill_matcher.rank_resumes(results)
    
    return {
        "job_posting_id": request.job_posting_id,
        "total_resumes": len(ranked_results),
        "ranked_results": ranked_results
    }


@router.get("/results/{job_posting_id}", response_model=List[ScreeningResultResponse])
async def get_screening_results(
    job_posting_id: int,
    db: Session = Depends(get_db)
):
    """Get all screening results for a job posting, ranked by score"""
    results = db.query(ScreeningResult).filter(
        ScreeningResult.job_posting_id == job_posting_id
    ).order_by(ScreeningResult.overall_score.desc()).all()
    
    # Update ranks
    for i, result in enumerate(results, start=1):
        result.rank = i
        db.commit()
    
    return results


@router.get("/result/{result_id}", response_model=ScreeningResultResponse)
async def get_screening_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific screening result"""
    result = db.query(ScreeningResult).filter(ScreeningResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Screening result not found")
    return result

