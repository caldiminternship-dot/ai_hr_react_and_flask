import time
from typing import Dict, List
from utils import Fore, Style, format_response, calculate_performance_score, calculate_detailed_score, get_performance_feedback
from question_generator import QuestionGenerator
from response_analyzer import ResponseAnalyzer
from config import MAX_QUESTIONS, MIN_QUESTIONS
import openai
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

class InterviewManager: 
    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.response_analyzer = ResponseAnalyzer()
        self.interview_data = {
            "candidate_info": {},
            "questions_asked": [],
            "responses": [],
            "start_time": None,
            "end_time": None,
            "status": "not_started",
            "actual_questions_asked": 0
        }
        self.current_question_count = 0
        self.needs_more_info = False
        self.technical_question_count = 0
        self.report_filename = None
    
    def start_interview(self):
        """Start the interview session"""
        self.interview_data["start_time"] = time.time()
        self.interview_data["status"] = "in_progress"
        
        # Create timestamp for filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.report_filename = f"reports/interview_report_{timestamp}.txt"
        
        # Initialize report file
        try:
            self._write_to_report("="*70)
            self._write_to_report("VIRTUAL HR INTERVIEWER - INTERVIEW REPORT")
            self._write_to_report("="*70)
            self._write_to_report(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            self._write_to_report("="*70 + "\n")
        except Exception as e:
            print(f"Warning: Could not create report file: {e}")
    
    def _write_to_report(self, text: str, include_timestamp: bool = False):
        """Write text to the report file"""
        try:
            if self.report_filename:
                with open(self.report_filename, 'a', encoding='utf-8') as f:
                    if include_timestamp:
                        timestamp = time.strftime("%H:%M:%S")
                        f.write(f"[{timestamp}] {text}\n")
                    else:
                        f.write(f"{text}\n")
        except Exception as e:
            print(f"Error writing to report file: {e}")
    
    def ask_initial_question(self) -> str:
        """Ask the initial introduction question"""
        initial_question = "Tell me about yourself, including your projects, technical skills, and work experience."
        
        # Log to report
        self._write_to_report("INTERVIEW STARTED", include_timestamp=True)
        self._write_to_report(f"Interviewer: {initial_question}")
        self._write_to_report("="*40)
        
        return initial_question
    
    def process_response(self, response: str) -> Dict:
        """Process candidate response"""
        from utils import clean_text
        cleaned_response = clean_text(response)
        
        # Log candidate response
        if self.current_question_count == 0:
            self._write_to_report(f"Candidate (Introduction): {cleaned_response[:500]}...")
        else:
            self._write_to_report(f"Candidate: {cleaned_response}")
        
        # Check for empty response on first question
        if not cleaned_response and self.current_question_count == 0:
            return {"terminate": False, "needs_more_info": True}
        
        # Check for termination conditions
        if cleaned_response:
            should_terminate, reason = self.response_analyzer.check_for_termination(cleaned_response)
            
            if should_terminate:
                self._write_to_report(f"INTERVIEW TERMINATED: {reason}", include_timestamp=True)
                return {"terminate": True, "reason": reason}
        
        # Handle "skip" command
        if cleaned_response and cleaned_response.lower() == "skip":
            self._write_to_report("Candidate: [SKIPPED]", include_timestamp=True)
            return {"terminate": False, "skip": True}
        
        # Process the actual response
        if cleaned_response:
            # Track actual questions asked
            if self.current_question_count > 0:
                self.interview_data["actual_questions_asked"] += 1
            
            # Analyze response
            if self.current_question_count == 0:
                # Initial "Tell me about yourself" response
                if len(cleaned_response.split()) < 10:
                    self.needs_more_info = True
                    return {"terminate": False, "needs_more_info": True}
                
                # Analyze introduction
                analysis = self.response_analyzer.analyze_introduction(cleaned_response)
                self.interview_data["candidate_info"] = analysis
                
                # Get the question (handle edge case)
                if self.interview_data["questions_asked"]:
                    question = self.interview_data["questions_asked"][-1]
                else:
                    question = "Tell me about yourself, including your projects, technical skills, and work experience."
                
                # Store initial response
                response_data = {
                    "question": question,
                    "answer": cleaned_response,
                    "evaluation": {"overall": 7, "accuracy": 7, "relevance": 8, "depth": 6},
                    "score": 7,
                    "question_number": 1,
                    "question_type": "intro",
                    "word_count": len(cleaned_response.split())
                }
                self.interview_data["responses"].append(response_data)
                
                # Increment question count
                self.current_question_count += 1
                
                return {"terminate": False, "score": 7}
                
            else:
                # Follow-up question response
                if not self.interview_data["questions_asked"]:
                    last_question = "Tell me about yourself"
                else:
                    last_question = self.interview_data["questions_asked"][-1]
                
                # Evaluate the answer
                evaluation = self.response_analyzer.evaluate_answer(last_question, cleaned_response)
                word_count = len(cleaned_response.split())
                
                # Determine question type
                question_type = "behavioral" if "behavioral" in last_question.lower() or \
                    any(word in last_question.lower() for word in ["team", "project", "challenge", "disagreement"]) \
                    else "technical"
                
                # Track technical questions
                if question_type == "technical":
                    self.technical_question_count += 1
                
                # Store response
                response_data = {
                    "question": last_question,
                    "answer": cleaned_response,
                    "evaluation": evaluation,
                    "score": evaluation.get("overall", 0),
                    "word_count": word_count,
                    "question_number": len(self.interview_data["responses"]) + 1,
                    "question_type": question_type
                }
                
                self.interview_data["responses"].append(response_data)
                
                # Log to report
                self._write_to_report("\n" + "-"*40)
                self._write_to_report(f"Question {len(self.interview_data['responses'])}: {last_question}")
                self._write_to_report(f"Answer (Word Count): {word_count} words")
                self._write_to_report(f"Score: {evaluation.get('overall', 0)}/10")
                
                return {"terminate": False, "score": evaluation.get("overall", 0)}
        
        self.needs_more_info = False
        return {"terminate": False}
    
    def get_next_question(self) -> str:
        """Get the next AI-generated question based on interview progress"""
        
        # If it's the first follow-up question (after introduction)
        if self.current_question_count == 1:
            # Generate first adaptive question
            skill_category = self.interview_data["candidate_info"].get("primary_skill", "backend")
            question = self.question_generator.generate_adaptive_question(
                skill_category,
                self.interview_data["responses"]
            )
        else:
            # Check if it's time for a behavioral question (every 3rd question)
            total_questions = len(self.interview_data.get("questions_asked", [])) - 1
            if total_questions > 0 and total_questions % 3 == 0:
                # Generate AI-powered behavioral question
                question = self.question_generator.generate_behavioral_question_ai(
                    self.interview_data["candidate_info"],
                    self.interview_data["responses"]
                )
            else:
                # Generate adaptive technical question
                skill_category = self.interview_data["candidate_info"].get("primary_skill", "backend")
                question = self.question_generator.generate_adaptive_question(
                    skill_category,
                    self.interview_data["responses"]
                )
        
        if question:
            # Clean question for display
            clean_question = question
            if isinstance(question, str) and question.startswith("[AI-Generated"):
                if "] " in question:
                    clean_question = question.split("] ", 1)[1]
            
            # Store with tag for tracking
            tagged_question = f"[AI-Generated {question_type if 'question_type' in locals() else 'Technical'}] {clean_question}"
            if "questions_asked" not in self.interview_data:
                self.interview_data["questions_asked"] = []
            self.interview_data["questions_asked"].append(tagged_question)
            
            # Log to report
            self._write_to_report("\n" + "="*40)
            self._write_to_report(f"Question {len(self.interview_data['questions_asked'])}:", include_timestamp=True)
            self._write_to_report(f"Type: {question_type if 'question_type' in locals() else 'Technical'}")
            self._write_to_report(f"Content: {clean_question}")
            self._write_to_report("="*40)
            
            # Increment question count
            self.current_question_count += 1
            
            return clean_question
        
        return None
    
    def should_continue(self) -> bool:
        """Determine if interview should continue"""
        total_questions = len(self.interview_data.get("questions_asked", [])) - 1
        
        # Check if we've reached max questions
        if total_questions >= MAX_QUESTIONS:
            return False
        
        # Check for early termination based on performance
        if len(self.interview_data.get("responses", [])) > 2:
            # Get only technical question scores
            tech_scores = []
            for r in self.interview_data["responses"]:
                if r.get("question_type") == "technical" and "score" in r:
                    tech_scores.append(r["score"])
            
            if tech_scores and len(tech_scores) >= 2:
                recent_scores = tech_scores[-2:]
                avg_recent_score = sum(recent_scores) / len(recent_scores)
                
                # Terminate early if consistently poor performance
                if avg_recent_score < 3 and total_questions >= MIN_QUESTIONS + 1:
                    self._write_to_report("INTERVIEW TERMINATED: Poor performance", include_timestamp=True)
                    return False
        
        return True
    
    def end_interview(self, early_termination: bool = False, reason: str = ""):
        """End the interview session"""
        self.interview_data["end_time"] = time.time()
        self.interview_data["status"] = "completed"
        
        # Calculate duration
        if self.interview_data["start_time"] and self.interview_data["end_time"]:
            duration_seconds = self.interview_data["end_time"] - self.interview_data["start_time"]
            duration_minutes = duration_seconds / 60
        else:
            duration_minutes = 0
        
        # Log end of interview to report
        self._write_to_report("\n" + "="*60)
        self._write_to_report(f"INTERVIEW COMPLETED - {time.strftime('%H:%M:%S')}")
        self._write_to_report(f"Duration: {duration_minutes:.1f} minutes")
        total_q = len(self.interview_data.get("questions_asked", [])) - 1
        self._write_to_report(f"Total Questions: {max(0, total_q) + 1}")
        self._write_to_report("="*60)
        
        # Provide AI-powered feedback and generate report
        if self.interview_data.get("responses"):
            self._provide_ai_feedback()
    
    def _provide_ai_feedback(self):
        """Provide AI-powered detailed feedback"""
        if len(self.interview_data.get("responses", [])) <= 1:
            return
        
        # Generate AI summary
        ai_summary = self._generate_ai_summary()
        
        # Write comprehensive report
        if self.report_filename and self.interview_data.get("responses"):
            avg_score = calculate_performance_score(self.interview_data["responses"])
            detailed_scores = calculate_detailed_score(self.interview_data["responses"])
            self._write_comprehensive_report(avg_score, detailed_scores, ai_summary)
    
    def _generate_ai_summary(self) -> str:
        """Generate AI summary of candidate performance"""
        try:
            # Prepare conversation history
            history_text = ""
            for i, response in enumerate(self.interview_data.get("responses", [])):
                if i == 0:
                    continue
                history_text += f"Q{i}: {response.get('question', '')}\n"
                history_text += f"A{i}: {response.get('answer', '')[:100]}...\n"
            
            prompt = f"""
            Analyze this interview performance and provide a brief, professional summary.
            
            Candidate Background:
            Skills: {self.interview_data['candidate_info'].get('skills', [])[:5]}
            Experience: {self.interview_data['candidate_info'].get('experience', 'mid')}
            
            Interview Summary:
            {history_text}
            
            Provide a 2-3 sentence summary highlighting key strengths and areas for improvement.
            """
            
            openai.api_key = OPENROUTER_API_KEY
            openai.api_base = OPENROUTER_BASE_URL
            response = openai.ChatCompletion.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "You are an HR analyst providing interview feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "AI analysis unavailable. See detailed scores below."
    
    def _write_comprehensive_report(self, avg_score: float, detailed_scores: Dict, ai_summary: str):
        """Write comprehensive interview report to file"""
        try:
            # Your existing report writing code (simplified)
            with open(self.report_filename, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("VIRTUAL HR INTERVIEWER - COMPREHENSIVE INTERVIEW REPORT\n")
                f.write("="*70 + "\n\n")
                
                # Add your report content here...
                f.write(f"Average Score: {avg_score:.1f}/10\n")
                f.write(f"AI Summary: {ai_summary}\n")
                
        except Exception as e:
            print(f"Error writing comprehensive report: {e}")