import openai
import random
from typing import List, Dict
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, QUESTION_DIFFICULTY_LEVELS, SKILL_CATEGORIES

class QuestionGenerator:
    def __init__(self):
        openai.api_key = OPENROUTER_API_KEY
        openai.api_base = OPENROUTER_BASE_URL
        self.asked_questions = []
        self.conversation_history = []
    
    def generate_initial_skill_questions(self, skill_category: str, candidate_level: str = "mid") -> List[str]:
        """Generate initial questions based on skill category """
        
        prompt = f"""
        Generate 3 technical interview questions for a {candidate_level}-level {skill_category} developer.
        The questions should cover:
        1. A fundamental concept question
        2. A practical implementation question
        3. A problem-solving scenario question
        
        Format each question on a new line starting with Q1:, Q2:, Q3:
        
        Skill Category: {skill_category}
        Level: {candidate_level}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "You are a technical interviewer creating relevant questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            questions_text = response.choices[0].message.content # type: ignore
            questions = []
            
            # Parse the response
            lines = questions_text.strip().split('\n')
            for line in lines:
                if line.strip() and (line.startswith('Q') or '?' in line):
                    # Clean up the question
                    question = line.strip()
                    if ':' in question:
                        question = question.split(':', 1)[1].strip()
                    questions.append(question)
            
            return questions[:3]  # Return up to 3 questions
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            # Fallback questions
            return self._get_fallback_questions(skill_category)
    
    def generate_adaptive_followup(self, previous_question: str, candidate_answer: str, 
                                  skill_category: str, difficulty_level: int) -> str:
        """Generate a follow-up question based on the candidate's previous answer"""
        
        # Add to conversation history
        self.conversation_history.append({
            "question": previous_question,
            "answer": candidate_answer
        })
        
        # Determine next question type based on previous answer quality
        answer_length = len(candidate_answer.split())
        if answer_length < 30:
            # Short answer - ask for more depth
            followup_type = "probing"
        elif difficulty_level < 3:
            # Medium difficulty - increase challenge
            followup_type = "deepening"
        else:
            # Already challenging - ask application question
            followup_type = "application"
        
        prompt = f"""
        You are conducting a technical interview for a {skill_category} role.
        
        Previous Question: {previous_question}
        Candidate's Answer: {candidate_answer}
        
        Generate a follow-up question that:
        1. Builds upon their answer
        2. Tests deeper understanding
        3. Is appropriate for difficulty level {difficulty_level}/5
        4. Type: {followup_type}
        
        If their answer was incomplete or shallow, ask a clarifying question.
        If their answer was good, ask a more challenging related question.
        
        Generate ONLY the follow-up question, nothing else.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "You are a technical interviewer creating intelligent follow-up questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=100
            )
            
            followup_question = response.choices[0].message.content.strip() # type: ignore

            # Clean up the question
            if followup_question.startswith('"') and followup_question.endswith('"'):
                followup_question = followup_question[1:-1]
            
            return followup_question
            
        except Exception as e:
            print(f"Error generating followup: {e}")
            return self._get_generic_followup(skill_category)
    
    def generate_behavioral_question_ai(self, candidate_background: Dict, context: List[Dict]) -> str:  # type: ignore
        """Generate a behavioral question using AI based on candidate's background"""
        
        skills = candidate_background.get("skills", [])
        experience = candidate_background.get("experience", "mid")
        
        prompt = f"""
        Generate a behavioral interview question for a software developer with:
        - Skills: {', '.join(skills[:5]) if skills else 'General development'}
        - Experience Level: {experience}
        - Recent technical questions asked: {len(context)} questions
        
        The question should assess:
        1. Problem-solving approach
        2. Team collaboration
        3. Learning adaptability
        4. Project management
        
        Make the question specific to their technical background.
        Generate ONLY the question, nothing else.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "You are an HR interviewer creating behavioral questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=80
            )
            
            question = response.choices[0].message.content.strip()  # type: ignore

        except Exception as e:
            print(f"Error generating behavioral question: {e}")
            return "Tell me about a challenging project you worked on and how you overcame obstacles."
    
    def generate_skill_questions(self, skill_category: str, difficulty_level: int, candidate_level: str = "mid") -> List[str]:
        """Generate questions based on skill category and difficulty using AI"""
        # This method now calls the AI-based generator
        return self.generate_initial_skill_questions(skill_category, candidate_level)
    
    def generate_behavioral_question(self, response_count: int) -> str:
        """Legacy method - now uses AI"""
        # Simple fallback for compatibility
        behavioral_questions = [
            "Describe a challenging project you worked on and how you overcame obstacles.",
            "Tell me about a time you had a disagreement with a team member and how you resolved it.",
            "How do you prioritize tasks when working on multiple projects with tight deadlines?",
        ]
        idx = min(response_count - 1, len(behavioral_questions) - 1)
        return behavioral_questions[idx]
    
    def generate_adaptive_question(self, skill_category: str, previous_responses: List[Dict]) -> str:
        """Generate adaptive question based on previous responses using AI"""
        if not previous_responses or len(previous_responses) <= 1:
            # First technical question after introduction
            questions = self.generate_initial_skill_questions(skill_category)
            if questions:
                question = questions[0]
                self.asked_questions.append(question)
                return question
        
        # Get the last Q&A pair
        last_response = previous_responses[-1]
        previous_question = last_response.get('question', '')
        previous_answer = last_response.get('answer', '')
        
        if not previous_question or not previous_answer:
            return "What are the key considerations when designing a scalable system?"
        
        # Calculate difficulty level based on performance
        recent_scores = [r.get('score', 5) for r in previous_responses[-2:]]
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 5
        
        if avg_score >= 8:
            difficulty_level = min(len(previous_responses) + 1, 5)
        elif avg_score >= 5:
            difficulty_level = len(previous_responses)
        else:
            difficulty_level = max(1, len(previous_responses) - 1)
        
        # Generate follow-up question
        followup = self.generate_adaptive_followup(
            previous_question=previous_question,
            candidate_answer=previous_answer,
            skill_category=skill_category,
            difficulty_level=difficulty_level
        )
        
        if followup and followup not in self.asked_questions:
            self.asked_questions.append(followup)
            return followup
        
        return "How would you approach debugging a performance issue in production?"
    
    def _get_fallback_questions(self, skill_category: str) -> List[str]:
        """Fallback questions if AI generation fails"""
        fallback_questions = {
            "backend": [
                "Explain the difference between synchronous and asynchronous programming.",
                "How would you design a rate-limiting system for an API?",
                "Describe database indexing and its impact on query performance."
            ],
            "frontend": [
                "What is the virtual DOM and why is it important in React?",
                "How would you optimize website performance for mobile devices?",
                "Explain the concept of state management in frontend applications."
            ],
            "devops": [
                "What is the difference between Docker and Kubernetes?",
                "How would you implement a CI/CD pipeline from scratch?",
                "Describe strategies for zero-downtime deployments."
            ],
            "data": [
                "Explain the bias-variance tradeoff in machine learning.",
                "How would you handle missing data in a dataset?",
                "Describe different types of database normalization."
            ]
        }
        
        return fallback_questions.get(skill_category, fallback_questions["backend"])
    
    def _get_generic_followup(self, skill_category: str) -> str:
        """Generic follow-up questions"""
        followups = {
            "backend": "Can you elaborate on how you would implement that in a production environment?",
            "frontend": "How would you test this approach across different browsers?",
            "devops": "What monitoring tools would you use to track this in production?",
            "data": "What metrics would you use to evaluate the success of this approach?"
        }
        return followups.get(skill_category, "Can you provide more details about your approach?")