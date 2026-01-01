from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import PyPDF2
import docx
from io import BytesIO

from app.core.database import get_db
from app.models.resume import Resume
from app.services.resume_parser import ResumeParser
from app.schemas.resume import ResumeCreate, ResumeResponse

router = APIRouter()
resume_parser = ResumeParser()


def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file (PDF or DOCX)"""
    content = file.file.read()
    
    if file.filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    
    elif file.filename.endswith('.docx'):
        try:
            doc = docx.Document(BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")
    
    elif file.filename.endswith('.txt'):
        return content.decode('utf-8')
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume"""
    # Extract text from file
    text = extract_text_from_file(file)
    
    if not text or len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short or empty")
    
    # Parse resume using NLP
    parsed_data = resume_parser.parse(text)
    
    # Create resume record
    resume = Resume(
        filename=file.filename,
        original_text=text,
        parsed_data=parsed_data,
        skills=parsed_data.get("skills", []),
        experience_years=parsed_data.get("experience_years"),
        education_level=parsed_data.get("education_level")
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all resumes"""
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}

