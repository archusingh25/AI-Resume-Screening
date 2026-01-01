from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SkillMatcher:
    """Skill matching and ranking system"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=1000
        )
    
    def match_skills(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None
    ) -> Dict:
        """Match resume skills against job requirements"""
        if preferred_skills is None:
            preferred_skills = []
        
        # Normalize skills to lowercase for comparison
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        preferred_skills_lower = [skill.lower() for skill in preferred_skills]
        
        # Find exact matches
        matched_required = [
            skill for skill in required_skills
            if skill.lower() in resume_skills_lower
        ]
        
        matched_preferred = [
            skill for skill in preferred_skills
            if skill.lower() in resume_skills_lower
        ]
        
        # Find missing required skills
        missing_required = [
            skill for skill in required_skills
            if skill.lower() not in resume_skills_lower
        ]
        
        # Calculate similarity scores using TF-IDF
        similarity_score = self._calculate_similarity(
            resume_skills,
            required_skills + preferred_skills
        )
        
        # Calculate skill match percentage
        required_match_ratio = len(matched_required) / len(required_skills) if required_skills else 0
        preferred_match_ratio = len(matched_preferred) / len(preferred_skills) if preferred_skills else 0
        
        # Combined score (weighted: 70% required, 30% preferred)
        skill_match_score = (
            required_match_ratio * 0.7 + 
            preferred_match_ratio * 0.3
        ) * 100
        
        return {
            "matched_required_skills": matched_required,
            "matched_preferred_skills": matched_preferred,
            "missing_required_skills": missing_required,
            "skill_match_score": round(skill_match_score, 2),
            "similarity_score": round(similarity_score, 2),
            "required_match_ratio": round(required_match_ratio, 2),
            "preferred_match_ratio": round(preferred_match_ratio, 2)
        }
    
    def _calculate_similarity(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> float:
        """Calculate semantic similarity between resume and job skills"""
        if not resume_skills or not job_skills:
            return 0.0
        
        # Combine skills into text
        resume_text = " ".join(resume_skills)
        job_text = " ".join(job_skills)
        
        try:
            # Vectorize and calculate cosine similarity
            vectors = self.vectorizer.fit_transform([resume_text, job_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            # Fallback to simple word overlap
            resume_words = set(resume_text.lower().split())
            job_words = set(job_text.lower().split())
            
            if not job_words:
                return 0.0
            
            intersection = resume_words.intersection(job_words)
            return len(intersection) / len(job_words)
    
    def rank_resumes(
        self,
        screening_results: List[Dict]
    ) -> List[Dict]:
        """Rank resumes based on multiple criteria"""
        # Sort by overall score (descending)
        ranked = sorted(
            screening_results,
            key=lambda x: x.get("overall_score", 0),
            reverse=True
        )
        
        # Assign ranks
        for i, result in enumerate(ranked, start=1):
            result["rank"] = i
        
        return ranked

