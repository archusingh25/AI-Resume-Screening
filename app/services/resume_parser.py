import spacy
from typing import Dict, List, Optional
import re
from app.core.config import settings


class ResumeParser:
    """NLP-based CV parsing using spaCy"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            raise Exception(
                f"spaCy model '{settings.SPACY_MODEL}' not found. "
                f"Please install it using: python -m spacy download {settings.SPACY_MODEL}"
            )
    
    def parse(self, text: str) -> Dict:
        """Parse resume text and extract structured information"""
        doc = self.nlp(text)
        
        parsed_data = {
            "name": self._extract_name(doc),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(doc, text),
            "experience": self._extract_experience(doc, text),
            "education": self._extract_education(doc, text),
            "summary": self._extract_summary(doc),
            "experience_years": self._calculate_experience_years(doc, text),
            "education_level": self._extract_education_level(doc, text),
        }
        
        return parsed_data
    
    def _extract_name(self, doc) -> Optional[str]:
        """Extract candidate name (first person entity)"""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group() if match else None
    
    def _extract_skills(self, doc, text: str) -> List[str]:
        """Extract technical skills from resume"""
        skills = []
        
        # Common technical skills keywords
        skill_keywords = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "sql", "postgresql", "mysql", "mongodb", "redis",
            "docker", "kubernetes", "aws", "azure", "gcp",
            "git", "github", "gitlab", "ci/cd", "jenkins",
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "fastapi", "django", "flask", "express", "spring",
            "html", "css", "typescript", "rest api", "graphql",
            "agile", "scrum", "devops", "microservices"
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Extract noun phrases that might be skills
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:
                chunk_lower = chunk.text.lower()
                if any(keyword in chunk_lower for keyword in skill_keywords):
                    if chunk.text not in skills:
                        skills.append(chunk.text)
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_experience(self, doc, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        experience_pattern = r'(?i)(?:work|experience|employment|career)'
        
        # Simple extraction - can be enhanced with more sophisticated NLP
        lines = text.split('\n')
        current_exp = {}
        
        for i, line in enumerate(lines):
            if re.search(experience_pattern, line):
                # Look for dates and company names
                date_match = re.search(r'\d{4}|\d{1,2}[/-]\d{4}', line)
                if date_match:
                    current_exp['dates'] = date_match.group()
                
                # Look for company names (entities)
                for ent in doc.ents:
                    if ent.label_ == "ORG" and ent.text in line:
                        current_exp['company'] = ent.text
                        break
                
                if current_exp:
                    experience.append(current_exp)
                    current_exp = {}
        
        return experience
    
    def _extract_education(self, doc, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        education_keywords = ["university", "college", "degree", "bachelor", "master", "phd", "diploma"]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                edu_entry = {"institution": None, "degree": None, "year": None}
                
                # Extract degree
                degree_match = re.search(r'(?i)(bachelor|master|phd|doctorate|diploma|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)', line)
                if degree_match:
                    edu_entry["degree"] = degree_match.group()
                
                # Extract year
                year_match = re.search(r'\d{4}', line)
                if year_match:
                    edu_entry["year"] = year_match.group()
                
                # Extract institution (ORG entity)
                for ent in doc.ents:
                    if ent.label_ == "ORG" and ent.text in line:
                        edu_entry["institution"] = ent.text
                        break
                
                if edu_entry["degree"] or edu_entry["institution"]:
                    education.append(edu_entry)
        
        return education
    
    def _extract_summary(self, doc) -> Optional[str]:
        """Extract summary/objective section"""
        # Simple extraction - first few sentences
        sentences = [sent.text for sent in doc.sents]
        if sentences:
            return " ".join(sentences[:3])
        return None
    
    def _calculate_experience_years(self, doc, text: str) -> Optional[int]:
        """Calculate total years of experience"""
        # Look for patterns like "5 years", "3+ years", etc.
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        matches = re.findall(years_pattern, text.lower())
        
        if matches:
            # Return the highest mentioned years
            return max([int(match) for match in matches])
        
        # Try to extract from dates
        date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        date_matches = re.findall(date_pattern, text)
        
        if date_matches:
            total_years = 0
            for start, end in date_matches:
                if end.lower() in ['present', 'current']:
                    end = '2024'  # Current year
                try:
                    years = int(end) - int(start)
                    total_years += years
                except:
                    pass
            return total_years if total_years > 0 else None
        
        return None
    
    def _extract_education_level(self, doc, text: str) -> Optional[str]:
        """Extract highest education level"""
        text_lower = text.lower()
        
        if re.search(r'\b(phd|doctorate|d\.?phil\.?)\b', text_lower):
            return "PhD"
        elif re.search(r'\b(master|m\.?s\.?|m\.?a\.?|mba)\b', text_lower):
            return "Master's"
        elif re.search(r'\b(bachelor|b\.?s\.?|b\.?a\.?|b\.?e\.?)\b', text_lower):
            return "Bachelor's"
        elif re.search(r'\b(diploma|associate)\b', text_lower):
            return "Diploma"
        
        return None

