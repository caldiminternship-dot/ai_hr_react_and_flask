import openai
import random
from typing import List, Dict
from config import SKILL_CATEGORIES, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME

class QuestionGenerator:
    def __init__(self):
        openai.api_key = OPENROUTER_API_KEY
        openai.api_base = OPENROUTER_BASE_URL

    # 1️⃣ FIRST QUESTION (GENERIC)
    def generate_general_intro_question(self) -> str:
        return (
            "Please describe your professional background, key skills, tools you use, "
            "and the type of projects you have worked on."
        )

    # 2️⃣ TECHNICAL QUESTIONS (CATEGORY LOCKED)
    def generate_initial_skill_questions(
        self, skill_category: str, candidate_level: str = "mid"
    ) -> List[str]:

        skills = SKILL_CATEGORIES.get(skill_category, [])
        skills_text = ", ".join(skills[:6]) if skills else skill_category

        prompt = f"""
        You are an interviewer.

        Candidate level: {candidate_level}
        Domain: {skill_category}
        Key skills: {skills_text}

        Generate:
        - 2 fundamental questions
        - 2 practical questions
        - 1 scenario-based question

        Each must be strictly related to the domain.
        
        IMPORTANT: Vary the questions. Do not use the same standard questions every time.
        Focus on: {random.choice(['performance and optimization', 'security and best practices', 'architecture and design', 'debugging and troubleshooting', 'modern features and updates'])}
        """

        try:
            res = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9, # Increased for variance
                max_tokens=250
            )

            import re
            # Clean up leading numbers (1. Question -> Question)
            cleaned_questions = []
            for q in [x for x in res.choices[0].message.content.split("\n") if x.strip().endswith("?")]:
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', q.strip())
                cleaned_questions.append(cleaned)
            
            return cleaned_questions[:5] # Ensure max 5

        except Exception:
            return self._fallback(skill_category)

    def generate_behavioral_question_ai(
        self,
        candidate_background: dict,
        context: list | None = None
    ) -> str:
        """
        Generate a behavioral question based on candidate background.
        Context is optional and used for future adaptive behavior.
        """

        domain = candidate_background.get("primary_skill", "general")

        if domain == "bim":
            return (
                "Tell me about a time you identified a coordination or clash issue "
                "that was outside your assigned scope in a BIM project. "
                "How did you handle it and what was the outcome?"
            )

        return (
            "Tell me about a time when you faced an unexpected challenge at work. "
            "How did you take ownership of the situation and resolve it?"
        )


    def _fallback(self, category: str) -> List[str]:
        skills = SKILL_CATEGORIES.get(category, [])
        if not skills:
            return [
                "Explain a core concept in your domain?",
                "Describe a real-world problem you solved?",
                "How do you stay updated in your field?"
            ]

        return [
            f"Explain a core concept in {skills[0]}?",
            f"How do you use {skills[1] if len(skills) > 1 else skills[0]}?",
            f"What challenges do you face with {skills[-1]}?"
        ]
