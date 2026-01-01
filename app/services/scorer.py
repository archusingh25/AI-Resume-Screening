from typing import Dict, List, Optional
from app.models.resume import Resume
from app.models.job_posting import JobPosting
from app.services.skill_matcher import SkillMatcher


class ResumeScorer:
    """Calculate comprehensive scores for resume screening"""
    
    def __init__(self):
        self.skill_matcher = SkillMatcher()
    
    def calculate_score(
        self,
        resume: Resume,
        job_posting: JobPosting
    ) -> Dict:
        """Calculate overall screening score"""
        resume_skills = resume.skills or []
        required_skills = job_posting.required_skills or []
        preferred_skills = job_posting.preferred_skills or []
        
        # Skill matching
        skill_match_result = self.skill_matcher.match_skills(
            resume_skills,
            required_skills,
            preferred_skills
        )
        
        # Experience score
        experience_score = self._calculate_experience_score(
            resume.experience_years,
            job_posting.min_experience_years
        )
        
        # Education score
        education_score = self._calculate_education_score(
            resume.education_level,
            job_posting.required_education
        )
        
        # Overall weighted score
        overall_score = (
            skill_match_result["skill_match_score"] * 0.5 +  # 50% weight
            experience_score * 0.3 +  # 30% weight
            education_score * 0.2  # 20% weight
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "skill_match_score": skill_match_result["skill_match_score"],
            "experience_score": experience_score,
            "education_score": education_score,
            "matched_skills": skill_match_result["matched_required_skills"],
            "missing_skills": skill_match_result["missing_required_skills"],
            "preferred_skills_matched": skill_match_result["matched_preferred_skills"],
            "skill_match_details": skill_match_result
        }
    
    def _calculate_experience_score(
        self,
        resume_experience: Optional[int],
        required_experience: Optional[int]
    ) -> float:
        """Calculate experience match score (0-100)"""
        if required_experience is None:
            return 100.0  # No requirement means any experience is fine
        
        if resume_experience is None:
            return 0.0  # No experience mentioned
        
        if resume_experience >= required_experience:
            # Bonus for exceeding requirements
            excess = resume_experience - required_experience
            if excess <= 2:
                return 100.0
            elif excess <= 5:
                return 95.0
            else:
                return 90.0  # Overqualified might be penalized slightly
        else:
            # Penalty for not meeting requirements
            ratio = resume_experience / required_experience
            return max(0.0, ratio * 100)
    
    def _calculate_education_score(
        self,
        resume_education: Optional[str],
        required_education: Optional[str]
    ) -> float:
        """Calculate education match score (0-100)"""
        if required_education is None:
            return 100.0  # No requirement
        
        if resume_education is None:
            return 50.0  # Unknown education
        
        # Education hierarchy
        education_hierarchy = {
            "Diploma": 1,
            "Bachelor's": 2,
            "Master's": 3,
            "PhD": 4
        }
        
        resume_level = education_hierarchy.get(resume_education, 0)
        required_level = education_hierarchy.get(required_education, 0)
        
        if resume_level >= required_level:
            return 100.0
        elif resume_level == required_level - 1:
            return 70.0
        else:
            return 40.0

