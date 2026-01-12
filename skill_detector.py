from typing import Dict, List, Tuple
import re
from config import SKILL_CATEGORIES

class SkillDetector:
    @staticmethod
    def detect_primary_skill(text: str) -> str:
        """Detect primary skill from text using config.py categories"""
        text_lower = text.lower()
        skill_scores: Dict[str, int] = {}  # ADDED TYPE ANNOTATION
        
        for skill_category, category_data in SKILL_CATEGORIES.items():
            # ADDED: Handle case where category_data is a list (your config format)
            if isinstance(category_data, list):
                keywords = [str(item).lower() for item in category_data]
            else:
                # Original code assumes dict with "keywords" key
                keywords = category_data.get("keywords", [])
            
            score = 0
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(str(keyword).lower()) + r'\b'
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            skill_scores[skill_category] = score
        
        # Find skill with highest score
        if skill_scores:
            max_skill = max(skill_scores.items(), key=lambda x: x[1])[0]
            return max_skill if skill_scores[max_skill] > 0 else "frontend"
        
        return "backend"  # Default
    
    @staticmethod
    def get_skill_keywords(skill_category: str) -> List[str]:
        """Get keywords for a specific skill category"""
        category_data = SKILL_CATEGORIES.get(skill_category, {})
        
        # ADDED: Handle case where category_data is a list
        if isinstance(category_data, list):
            return [str(item).lower() for item in category_data]
        
        return category_data.get("keywords", [])
    
    @staticmethod
    def get_all_skills() -> List[str]:
        """Get all available skill categories"""
        return list(SKILL_CATEGORIES.keys())   