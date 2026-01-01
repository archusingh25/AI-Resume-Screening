from fastapi import APIRouter
from app.api.v1 import resume, job_posting, screening

router = APIRouter()

router.include_router(resume.router, prefix="/resumes", tags=["resumes"])
router.include_router(job_posting.router, prefix="/job-postings", tags=["job-postings"])
router.include_router(screening.router, prefix="/screening", tags=["screening"])

