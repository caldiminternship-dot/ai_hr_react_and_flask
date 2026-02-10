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
        self, skill_category: str, candidate_level: str = "mid", specific_skills: List[str] = None
    ) -> List[str]:
        """
        Generate EXACTLY 20 questions based on the candidate's profile and locked skills.
        Structure:
        - 5 Basic Technical (Tekla/SDS priority for AEC_BIM)
        - 10 Mixed (Basic/Deep) based on level ratio
        - 5 Behavioral
        """
        
        # 1. Determine Skills Context
        skills = SKILL_CATEGORIES.get(skill_category, [])
        skills_text = ", ".join(specific_skills) if specific_skills else ", ".join(skills[:6])
        if not skills_text:
            skills_text = skill_category

        # AEC_BIM Special Priority
        # ONLY Prioritize Tekla/SDS/BIM if they are ACTUALLY present in specific_skills
        bim_priority_text = ""
        if skill_category == "aec_bim" and specific_skills:
            # STRICTLY FILTER OUT Software Dev skills that might have been falsely detected
            forbidden_skills = ["go", "golang", "python", "java", "node", "backend", "api"]
            specific_skills = [s for s in specific_skills if s.lower() not in forbidden_skills]
            
            lower_skills = [s.lower() for s in specific_skills]
            
            # Check for BIM Modeling exclusivity logic
            bim_related_count = sum(1 for s in lower_skills if "bim" in s)
            non_bim_count = len(lower_skills) - bim_related_count
            
            if non_bim_count == 0 and bim_related_count > 0:
                 skills_text = "BIM Modeling"
            else:
                 # Only prioritize Tekla/SDS if they are in the detected list
                 priorities = []
                 if any("tekla" in s for s in lower_skills):
                     priorities.append("Tekla Structures")
                 if any("sds" in s for s in lower_skills):
                     priorities.append("SDS/2")
                 
                 if priorities:
                     bim_priority_text = f"Prioritize questions on **{'** and **'.join(priorities)}** as they are listed in the resume."

        # 2. Determine Ratios for the "Next 10"
        # Beginner: 10 Basic (Strictly Basic for Junior as requested)
        # Average (Mid): 5 Basic + 5 Deep
        # Experienced: 2 Basic + 8 Deep
        
        c_level = candidate_level.lower()
        if "junior" in c_level or "beginner" in c_level or "fresher" in c_level:
            # Generate 10 Basic questions. We will dynamically insert 2 follow-ups in the App.
            mix_ratio_instruction = "Generate 10 BASIC/INTERMEDIATE technical questions."
        elif "senior" in c_level or "expert" in c_level or "experienced" in c_level:
             # Generate 10 High-level questions. We will dynamically insert 8 follow-ups in the App.
             mix_ratio_instruction = "Generate 10 ADVANCED/COMPLEX technical questions."
        else: # Mid/Average
             mix_ratio_instruction = "Generate 10 INTERMEDIATE/ADVANCED technical questions."

        if skill_category == "aec_bim":
             strict_exclusion = "CRITICAL: The domain is AEC/BIM. Do NOT ask about software development (Go, Python) OR Data Management (Databases, Data Analytics). Do NOT ask about User Interface (UI) locations, buttons, ribbons, or menu paths. Focus ONLY on Engineering concepts, Detailing rules, Modeling logic, and Construction workflows."
        else:
             strict_exclusion = ""

        # Call 1: Generate 15 Technical Questions
        # Structure: 5 Basic + 10 Mixed
        prompt_tech = f"""
        You are an expert technical interviewer. Generate exactly 15 technical interview questions.
        
        Candidate Domain: {skill_category}
        Candidate Level: {candidate_level}
        Key Skills: {skills_text}
        
        CRITICAL RULES:
        1. ASK ONLY ABOUT THE KEY SKILLS LISTED ABOVE ({skills_text}). 
        2. {strict_exclusion}
        3. If a skill is not in the list, ignore it completely.
        
        Strictly follow this structure:

        SECTION 1: 5 BASIC Technical Questions
        - Focus: Core concepts, definitions, tools.
        - {bim_priority_text}
        - Difficulty: STRICTLY BASIC / FUNDAMENTAL.

        SECTION 2: 10 SKILL-BASED MIXED Questions
        - {mix_ratio_instruction}
        - Topic: Strictly related to Key Skills ({skills_text}).

        OUTPUT FORMAT:
        Return ONLY the list of 15 questions, one per line.
        """

        tech_questions = []
        try:
            res_tech = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt_tech}],
                temperature=0.7, 
                max_tokens=600 
            )
            raw_lines = res_tech.choices[0].message.content.strip().split("\n")
            import re
            for line in raw_lines:
                line = re.sub(r'^[\d\-\.\)\s]+', '', line.strip())
                if line and "?" in line:
                    tech_questions.append(line)
        except Exception as e:
            print(f"Error generating technical questions: {e}")
            tech_questions = self._fallback(skill_category) * 3

        # Call 2: Generate 5 Behavioral Questions
        prompt_beh = f"""
        You are an HR interviewer. Generate exactly 5 behavioral interview questions.
        
        Focus: Teamwork, ownership, communications, adaptability, conflict resolution.
        Context: For a technical role in {skill_category} at {candidate_level} level.
        
        OUTPUT FORMAT:
        Return ONLY the list of 5 questions, one per line.
        """
        
        beh_questions = []
        try:
            res_beh = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt_beh}],
                temperature=0.8, 
                max_tokens=300
            )
            raw_lines = res_beh.choices[0].message.content.strip().split("\n")
            for line in raw_lines:
                line = re.sub(r'^[\d\-\.\)\s]+', '', line.strip())
                if line and "?" in line:
                    beh_questions.append(line)
        except Exception as e:
            print(f"Error generating behavioral questions: {e}")
            beh_questions = ["Describe a time you showed leadership.", "How do you handle conflict?", "Describe a challenge you overcame.", "How do you prioritize tasks?", "Why do you want this job?"]

        # Combine: First 15 Tech + Last 5 Behavioral
        # Ensure tech list is trimmed/padded to 15 if AI messed up
        final_tech = tech_questions[:15]
        if len(final_tech) < 15:
            # Pad if needed (unlikely)
            while len(final_tech) < 15:
                 final_tech.append(f"Explain a core concept in {skill_category}.")
        
        final_beh = beh_questions[:5]
        final_beh = beh_questions[:5]
        if len(final_beh) < 5:
             fallback_beh = [
                 "Describe a professional achievement you are proud of.",
                 "How do you handle tight deadlines?",
                 "Describe a time you had a conflict with a colleague and how you resolved it.",
                 "What is your preferred work style: independent or collaborative?",
                 "How do you stay updated with industry trends?"
             ]
             # Fill with unique fallbacks
             for q in fallback_beh:
                 if len(final_beh) >= 5:
                     break
                 if q not in final_beh:
                     final_beh.append(q)

        return final_tech + final_beh 

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

    def generate_followup_question(
        self,
        previous_question: str,
        previous_answer: str,
        skill_category: str | None = None
    ) -> str | None:
        """Generate a single concise follow-up question based on the candidate's previous answer.

        Returns a string follow-up question, or None if no useful follow-up can be generated.
        """

        # Quick heuristics to avoid asking followups for very short answers or flagged content
        if not previous_answer or len(previous_answer.strip()) < 30:
            return None

        if previous_answer.lower().strip().startswith("session terminated"):
            return None

        prompt = f"""
        You are an intelligent interviewer. Given the previous question and the candidate's answer, produce a single, concise follow-up question that probes deeper, asks for clarification, or requests a concrete example.

        Previous question: {previous_question}
        Candidate answer: {previous_answer}

        Requirements:
        - Single short question (one sentence, ending with a '?')
        - Strictly related to the domain and the candidate's answer
        - **Beginner level difficulty**: Ask for basic clarification or a simple example. Do not ask complex or deep technical questions.
        - Avoid repeating the same content
        - Do not ask meta-questions (e.g., 'Did that make sense?')
        - If the answer already fully addresses the question, return an empty string
        """

        try:
            res = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=80
            )

            followup = res.choices[0].message.content.strip()
            # Basic cleanup
            if not followup or len(followup) < 10 or "no follow" in followup.lower():
                return None

            # Ensure it ends with a '?'
            if not followup.endswith('?'):
                followup = followup.rstrip('.') + '?'

            return followup

        except Exception:
            # Fallback heuristic: ask for more detail about a noun in the answer
            words = [w.strip('.,') for w in previous_answer.split() if len(w) > 4]
            if not words:
                return None
            keyword = words[0]
            return f"Can you provide a concrete example that illustrates {keyword}?"


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
