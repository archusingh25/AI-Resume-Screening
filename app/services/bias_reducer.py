import re
from typing import Dict, Optional


class BiasReducer:
    """Bias reduction mechanisms for fair resume screening"""
    
    def __init__(self):
        # Patterns that might indicate bias
        self.personal_info_patterns = {
            "name": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Full names
            "age": r'\b\d{1,2}\s*(?:years?\s*old|y\.?o\.?)\b',
            "gender": r'\b(he|she|him|her|his|hers|male|female|man|woman)\b',
            "location": r'\b(?:lives?|resides?|located|from)\s+[A-Z][a-z]+',
            "nationality": r'\b(?:american|indian|chinese|british|canadian|australian)\b',
            "religion": r'\b(?:christian|muslim|hindu|jewish|buddhist|sikh)\b',
            "marital_status": r'\b(?:married|single|divorced|widowed)\b',
        }
    
    def anonymize_resume(self, text: str) -> str:
        """Remove personal information that could lead to bias"""
        anonymized = text
        
        # Remove names (but keep technical terms)
        anonymized = re.sub(
            r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            '[Name]',
            anonymized
        )
        
        # Remove age references
        anonymized = re.sub(
            self.personal_info_patterns["age"],
            '[Age]',
            anonymized,
            flags=re.IGNORECASE
        )
        
        # Remove gender pronouns (context-dependent, be careful)
        # This is a simple approach - more sophisticated methods needed for production
        
        # Remove location mentions (but keep work locations in experience)
        # This is complex and might need more context
        
        return anonymized
    
    def calculate_bias_score(self, resume_data: Dict) -> float:
        """Calculate a bias score (0-1, lower is better)"""
        bias_indicators = 0
        total_checks = 0
        
        text = resume_data.get("original_text", "").lower()
        
        # Check for various bias indicators
        for category, pattern in self.personal_info_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                bias_indicators += 1
            total_checks += 1
        
        # Check for photos (if text mentions photo)
        if "photo" in text or "picture" in text or "image" in text:
            bias_indicators += 1
        total_checks += 1
        
        # Normalize to 0-1 scale
        bias_score = bias_indicators / total_checks if total_checks > 0 else 0.0
        
        return round(bias_score, 3)
    
    def get_anonymized_score(
        self,
        original_score: float,
        bias_score: float
    ) -> float:
        """Calculate score adjusted for bias reduction"""
        # Penalize resumes with high bias indicators
        # Lower bias_score is better, so we subtract it
        adjusted_score = original_score * (1 - bias_score * 0.1)
        
        return round(max(0.0, adjusted_score), 2)
    
    def filter_bias_indicators(self, resume_data: Dict) -> Dict:
        """Filter out bias-inducing information from resume data"""
        filtered_data = resume_data.copy()
        
        # Remove personal identifiers
        fields_to_remove = ["name", "email", "phone"]
        for field in fields_to_remove:
            if field in filtered_data:
                filtered_data[field] = None
        
        return filtered_data

