import time
from typing import Dict, List
from utils import Fore, Style, format_response, calculate_performance_score, calculate_detailed_score, get_performance_feedback, format_score_bar
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
        self.report_filename = f"/reports/interview_report_{timestamp}.txt"
        
        print(format_response("\n" + "="*60, Fore.CYAN))
        print(format_response("VIRTUAL HR INTERVIEWER (AI-Powered)", Fore.CYAN + Style.BRIGHT))
        print(format_response("="*60, Fore.CYAN))
        print(format_response("\nWelcome! Let's begin the AI-powered interview.", Fore.GREEN))
        print(format_response("Questions are dynamically generated based on your responses.", Fore.YELLOW))
        print(format_response("Type 'quit' to end or 'skip' to move to next question.", Fore.YELLOW))
        print(format_response(f"Report will be saved to: {self.report_filename}\n", Fore.YELLOW))
        
        # Initialize report file
        self._write_to_report("="*70)
        self._write_to_report("VIRTUAL HR INTERVIEWER - INTERVIEW REPORT")
        self._write_to_report("="*70)
        self._write_to_report(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._write_to_report("="*70 + "\n")
    
    def _write_to_report(self, text: str, include_timestamp: bool = False):
        """Write text to the report file"""
        try:
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
        print(format_response(f"\nInterviewer: {initial_question}", Fore.BLUE + Style.BRIGHT))
        print(format_response("\n(Press Enter after typing your response)", Fore.YELLOW))
        
        # Log to report
        self._write_to_report("INTERVIEW STARTED", include_timestamp=True)
        self._write_to_report(f"Interviewer: {initial_question}")
        self._write_to_report("="*40)
        
        return initial_question
    
    def process_response(self, response: str) -> Dict:
        """Process candidate response"""
        from utils import clean_text
        cleaned_response = clean_text(response)
        
        # Log candidate response (even if empty)
        if self.current_question_count == 0:
            self._write_to_report(f"Candidate (Introduction): {cleaned_response[:500]}...")
        else:
            self._write_to_report(f"Candidate: {cleaned_response}")
        
        # Check for empty response
        if not cleaned_response and self.current_question_count == 0:
            print(format_response("\n[Note] I notice you haven't provided a response.", Fore.YELLOW))
            print(format_response("Please share your background to help me understand your skills.", Fore.YELLOW))
            self.needs_more_info = True
            return {"terminate": False, "needs_more_info": True}
        
        # Check for termination conditions
        if cleaned_response:
            should_terminate, reason = self.response_analyzer.check_for_termination(cleaned_response)
            
            if should_terminate:
                self._write_to_report(f"INTERVIEW TERMINATED: {reason}", include_timestamp=True)
                return {"terminate": True, "reason": reason}
        
        # Handle "skip" command
        if cleaned_response.lower() == "skip":
            print(format_response("\n[Note] Moving to next question.", Fore.YELLOW))
            self._write_to_report("Candidate: [SKIPPED]", include_timestamp=True)
            return {"terminate": False, "skip": True}
        
        # Track actual questions asked
        if self.current_question_count > 0:
            self.interview_data["actual_questions_asked"] += 1
        
        # Analyze response
        if self.current_question_count == 0:
            # Initial "Tell me about yourself" response
            if len(cleaned_response.split()) < 10:
                print(format_response("\n[Note] Please provide more details about your background.", Fore.YELLOW))
                print(format_response("Include: 1) Your projects 2) Technical skills 3) Work experience", Fore.YELLOW))
                self.needs_more_info = True
                return {"terminate": False, "needs_more_info": True}
            
            analysis = self.response_analyzer.analyze_introduction(cleaned_response)
            self.interview_data["candidate_info"] = analysis
            
            # Show minimal feedback to candidate
            print(format_response(f"\n✓ Introduction received. Analyzing your background...", Fore.GREEN))
            
            # Store initial response
            response_data = {
                "question": self.interview_data["questions_asked"][-1],
                "answer": cleaned_response,
                "evaluation": {"overall": 7, "accuracy": 7, "relevance": 8, "depth": 6},
                "score": 7,
                "question_number": 1,
                "question_type": "intro",
                "word_count": len(cleaned_response.split())
            }
            self.interview_data["responses"].append(response_data)
            
            # Log AI analysis to report
            self._write_to_report("\n" + "="*40)
            self._write_to_report("AI ANALYSIS OF INTRODUCTION:")
            self._write_to_report(f"Primary Skill: {analysis['primary_skill'].title()}")
            self._write_to_report(f"Experience Level: {analysis['experience'].title()}")
            self._write_to_report(f"Confidence: {analysis['confidence'].title()}")
            self._write_to_report(f"Skills Identified: {', '.join(analysis.get('skills', [])[:10])}")
            self._write_to_report(f"Projects Mentioned: {analysis.get('projects_mentioned', 0)}")
            self._write_to_report(f"Introduction Score: {analysis.get('intro_score', 7)}/10")
            self._write_to_report("="*40 + "\n")
            
            # Determine number of questions based on introduction quality
            if analysis["confidence"] == "low" or len(analysis["skills"]) < 2:
                self.max_questions = MIN_QUESTIONS
                print(format_response(f"\n[Note] Proceeding with {self.max_questions} follow-up questions.", Fore.YELLOW))
            else:
                self.max_questions = MAX_QUESTIONS
                print(format_response(f"\n[Note] Generating {self.max_questions} adaptive questions.", Fore.GREEN))
            
            self.current_question_count = 1
            
        else:
            # Follow-up question response
            last_question = self.interview_data["questions_asked"][-1]
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
                "score": evaluation["overall"],
                "word_count": word_count,
                "question_number": len(self.interview_data["responses"]) + 1,
                "question_type": question_type
            }
            
            self.interview_data["responses"].append(response_data)
            
            # Minimal feedback to candidate
            score = evaluation["overall"]
            print(format_response(f"✓ Response noted", Fore.YELLOW))
            if score >= 8:
                self._write_to_report(format_response(f"✓ Strong answer", Fore.GREEN))
            elif score >= 5:
                self._write_to_report(format_response(f"✓ Good answer", Fore.YELLOW))   
            else:
                self._write_to_report(format_response(f"✓ Below average", Fore.RED))
            
            # Word count feedback (only if very short)
            if word_count < 30:
                print(format_response("   [Tip] Consider providing more detailed explanations.", Fore.YELLOW))
            
            # Log question and evaluation to report
            self._write_to_report("\n" + "-"*40)
            self._write_to_report(f"Question {len(self.interview_data['responses'])}: {last_question}")
            self._write_to_report(f"Answer (Word Count): {word_count} words")
            self._write_to_report(f"Score: {evaluation['overall']}/10")
            
            # Log detailed scores if available
            if 'technical_accuracy' in evaluation:
                self._write_to_report(f"Technical Accuracy: {evaluation.get('technical_accuracy', 0)}/10")
                self._write_to_report(f"Completeness: {evaluation.get('completeness', 0)}/10")
                self._write_to_report(f"Clarity: {evaluation.get('clarity', 0)}/10")
                self._write_to_report(f"Depth: {evaluation.get('depth', 0)}/10")
                self._write_to_report(f"Practicality: {evaluation.get('practicality', 0)}/10")
            
            # Log strengths and weaknesses
            if evaluation.get('strengths'):
                self._write_to_report(f"Strengths: {', '.join(evaluation['strengths'])}")
            if evaluation.get('weaknesses'):
                self._write_to_report(f"Areas for Improvement: {', '.join(evaluation['weaknesses'])}")
        
        self.needs_more_info = False
        return {"terminate": False}
    
    def get_next_question(self) -> str:
        """Get the next AI-generated question based on interview progress"""
        
        if self.current_question_count == 0:
            return None
        
        # Check if it's time for a behavioral question
        total_questions = len(self.interview_data["questions_asked"])
        if total_questions > 1 and total_questions % 3 == 0:
            # Generate AI-powered behavioral question
            question = self.question_generator.generate_behavioral_question_ai(
                self.interview_data["candidate_info"],
                self.interview_data["responses"]
            )
            question_type = "behavioral"
        else:
            # Generate adaptive technical question
            skill_category = self.interview_data["candidate_info"].get("primary_skill", "backend")
            question = self.question_generator.generate_adaptive_question(
                skill_category,
                self.interview_data["responses"]
            )
            question_type = "technical"
        
        if question:
            # Remove any existing AI tags for cleaner display
            if question.startswith("[AI-Generated"):
                # Extract just the question part
                if "] " in question:
                    question = question.split("] ", 1)[1]
            
            # Add question to tracking
            tagged_question = f"[AI-Generated {question_type.title()}] {question}"
            self.interview_data["questions_asked"].append(tagged_question)
            
            # Log question to report
            self._write_to_report("\n" + "="*40)
            self._write_to_report(f"Question {len(self.interview_data['questions_asked'])}:", include_timestamp=True)
            self._write_to_report(f"Type: {question_type.upper()}")
            self._write_to_report(f"Content: {question}")
            self._write_to_report("="*40)
            
            # Return only the clean question (without AI tag)
            return question  # Return the clean question without tag
        
        return None
    
    def should_continue(self) -> bool:
        """Determine if interview should continue"""
        total_questions = len(self.interview_data["questions_asked"])
        
        # Check if we've reached max questions
        if total_questions - 1 >= getattr(self, 'max_questions', MAX_QUESTIONS):
            return False
        
        # Check for early termination based on performance
        if len(self.interview_data["responses"]) > 2:
            # Get only technical question scores
            tech_scores = [r["score"] for r in self.interview_data["responses"] 
                          if r.get("question_type") == "technical" and "score" in r]
            
            if tech_scores and len(tech_scores) >= 2:
                recent_scores = tech_scores[-2:]
                avg_recent_score = sum(recent_scores) / len(recent_scores)
                
                # Terminate early if consistently poor performance
                if avg_recent_score < 3 and total_questions >= MIN_QUESTIONS + 1:
                    self._write_to_report("INTERVIEW TERMINATED: Poor performance", include_timestamp=True)
                    print(format_response("\n[Note] Interview concluded based on performance.", Fore.YELLOW))
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
        
        # Calculate questions asked
        actual_q_asked = max(0, len(self.interview_data["questions_asked"]) - 1)
        
        # Log end of interview to report
        self._write_to_report("\n" + "="*60)
        self._write_to_report(f"INTERVIEW COMPLETED - {time.strftime('%H:%M:%S')}")
        self._write_to_report(f"Duration: {duration_minutes:.1f} minutes")
        self._write_to_report(f"Total Questions: {actual_q_asked + 1}")
        self._write_to_report("="*60)
        
        
        if early_termination:
            if reason == "misconduct":
                print(format_response("\n❌ Interview terminated due to unprofessional conduct.", Fore.RED))
                self._write_to_report("STATUS: Terminated - Unprofessional conduct")
            elif reason == "candidate_request":
                print(format_response("\n⚠️  Interview ended per candidate request.", Fore.YELLOW))
                self._write_to_report("STATUS: Ended - Candidate request")
            elif reason == "poor_response":
                print(format_response("\n⚠️  Interview ended due to insufficient responses.", Fore.YELLOW))
                self._write_to_report("STATUS: Ended - Insufficient responses")
            else:
                print(format_response("\n⚠️  Interview concluded early.", Fore.YELLOW))
                self._write_to_report(f"STATUS: Ended early - {reason}")
        else:
            print(format_response(f"\n✅ Interview completed successfully.", Fore.GREEN))
            print(format_response(f"📊 Total questions: {actual_q_asked + 1} (1 intro + {actual_q_asked} follow-ups)", Fore.WHITE))
            print(format_response(f"⏱️  Duration: {duration_minutes:.1f} minutes", Fore.WHITE))
            print(format_response(f"🤖 Questions generated by: MiMo-V2-Flash (OpenRouter)", Fore.WHITE))
        
        # Provide AI-powered feedback and generate report
        if self.interview_data["responses"]:
            self._provide_ai_feedback()
        
        # Final message about report
        if hasattr(self, 'report_filename'):
            print(format_response(f"\n📋 Complete interview analysis saved to: {self.report_filename}", Fore.GREEN))
            print(format_response("   This includes full transcript, scores, and recommendations.", Fore.YELLOW))
    
    def _provide_ai_feedback(self):
        """Provide AI-powered detailed feedback and save to file"""
        if len(self.interview_data["responses"]) <= 1:
            print(format_response("\nInsufficient responses for analysis.", Fore.YELLOW))
            return
        
        # Check if already provided feedback
        if hasattr(self, '_feedback_provided') and self._feedback_provided:
            return
        
        # Calculate scores
        avg_score = calculate_performance_score(self.interview_data["responses"])
        detailed_scores = calculate_detailed_score(self.interview_data["responses"])
        
        # Generate AI summary
        ai_summary = self._generate_ai_summary()
        
        # Write comprehensive report to file
        self._write_comprehensive_report(avg_score, detailed_scores, ai_summary)
        
        # Display to console (minimal feedback)
        print(format_response("\n" + "="*60, Fore.MAGENTA))
        print(format_response("INTERVIEW ANALYSIS COMPLETE", Fore.MAGENTA + Style.BRIGHT))
        print(format_response("="*60, Fore.MAGENTA))
        print(format_response(f"\n📋 Detailed report saved to: {self.report_filename}", Fore.GREEN))
        print(format_response("   Review the report for complete analysis and feedback.", Fore.YELLOW))
        
        # Just show final score and recommendation
        self._write_to_report(format_response(f"\n📊 FINAL SCORE: {avg_score:.1f}/10", Fore.CYAN + Style.BRIGHT))
        
        # Simple recommendation
        if avg_score >= 7.0:
            self._write_to_report(format_response("🎯 Outcome: Strong candidate - Proceed to next round", Fore.GREEN))
        elif avg_score >= 5.0:
            self._write_to_report(format_response("🎯 Outcome: Moderate candidate - Consider with feedback", Fore.YELLOW))
        else:
            self._write_to_report(format_response("🎯 Outcome: Not suitable - Requires improvement", Fore.RED))
        
        self._write_to_report(format_response(f"\n📝 Full analysis available in: {self.report_filename}", Fore.CYAN))
        
        # Mark feedback as provided
        self._feedback_provided = True
    
    def _generate_ai_summary(self) -> str:
        """Generate AI summary of candidate performance"""
        try:
            # Prepare conversation history
            history_text = ""
            for i, response in enumerate(self.interview_data["responses"]):
                if i == 0:
                    continue  # Skip introduction
                history_text += f"Q{i}: {response['question']}\n"
                history_text += f"A{i}: {response['answer'][:100]}...\n"
            
            prompt = f"""
            Analyze this interview performance and provide a brief, professional summary.
            
            Candidate Background:
            Skills: {self.interview_data['candidate_info'].get('skills', [])[:5]}
            Experience: {self.interview_data['candidate_info'].get('experience', 'mid')}
            Confidence: {self.interview_data['candidate_info'].get('confidence', 'medium')}
            
            Interview Summary:
            {history_text}
            
            Overall Average Score: {calculate_performance_score(self.interview_data['responses']):.1f}/10
            
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
            # Write full report (overwriting the temporary log)
            with open(self.report_filename, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("VIRTUAL HR INTERVIEWER - COMPREHENSIVE INTERVIEW REPORT\n")
                f.write("="*70 + "\n\n")
                
                # Interview metadata
                f.write("INTERVIEW METADATA:\n")
                f.write("-"*40 + "\n")
                f.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.interview_data['start_time']))}\n")
                if self.interview_data['end_time']:
                    f.write(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.interview_data['end_time']))}\n")
                    duration = self.interview_data['end_time'] - self.interview_data['start_time']
                    f.write(f"Duration: {duration/60:.1f} minutes\n")
                f.write(f"Report Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Candidate Information
                f.write("\nCANDIDATE PROFILE:\n")
                f.write("-"*40 + "\n")
                candidate_info = self.interview_data['candidate_info']
                f.write(f"Primary Skill Area: {candidate_info.get('primary_skill', 'N/A').title()}\n")
                f.write(f"Experience Level: {candidate_info.get('experience', 'N/A').title()}\n")
                f.write(f"Confidence Level: {candidate_info.get('confidence', 'N/A').title()}\n")
                f.write(f"Communication: {candidate_info.get('communication', 'N/A').title()}\n")
                skills = candidate_info.get('skills', [])
                if skills:
                    f.write(f"Skills Identified: {', '.join(skills[:10])}\n")
                    if len(skills) > 10:
                        f.write(f"Additional Skills: {', '.join(skills[10:15])}\n")
                f.write(f"Projects Mentioned: {candidate_info.get('projects_mentioned', 0)}\n")
                f.write(f"Introduction Score: {candidate_info.get('intro_score', 0)}/10\n")
                
                # Interview Statistics
                f.write("\nINTERVIEW STATISTICS:\n")
                f.write("-"*40 + "\n")
                total_questions = len(self.interview_data['questions_asked']) - 1  # Exclude intro
                f.write(f"Total Questions Asked: {total_questions}\n")
                f.write(f"Technical Questions: {sum(1 for r in self.interview_data['responses'] if r.get('question_type') == 'technical')}\n")
                f.write(f"Behavioral Questions: {sum(1 for r in self.interview_data['responses'] if r.get('question_type') == 'behavioral')}\n")
                f.write(f"Total Words in Responses: {sum(r.get('word_count', 0) for r in self.interview_data['responses'][1:])}\n")
                f.write(f"Average Response Length: {sum(r.get('word_count', 0) for r in self.interview_data['responses'][1:])/max(1, len(self.interview_data['responses'])-1):.0f} words\n")
                
                # Overall Performance Summary
                f.write("\nOVERALL PERFORMANCE SUMMARY:\n")
                f.write("-"*40 + "\n")
                f.write(f"Final Score: {avg_score:.1f}/10\n")
                f.write(f"Performance Level: {get_performance_feedback(avg_score, detailed_scores)}\n\n")
                
                # Score Breakdown
                f.write("DETAILED SCORE BREAKDOWN:\n")
                f.write("-"*40 + "\n")
                f.write(f"Technical Accuracy: {detailed_scores.get('technical', 0):.1f}/10\n")
                f.write(f"Answer Completeness: {detailed_scores.get('completeness', 0):.1f}/10\n")
                f.write(f"Communication Clarity: {detailed_scores.get('clarity', 0):.1f}/10\n")
                f.write(f"Technical Depth: {detailed_scores.get('depth', 0):.1f}/10\n")
                f.write(f"Practical Application: {detailed_scores.get('practicality', 0):.1f}/10\n")
                
                # Technical vs Behavioral Comparison
                tech_responses = [r for r in self.interview_data["responses"] if r.get("question_type") == "technical"]
                behavioral_responses = [r for r in self.interview_data["responses"] if r.get("question_type") == "behavioral"]
                
                if tech_responses:
                    tech_scores = [r.get("score", 0) for r in tech_responses]
                    tech_avg = sum(tech_scores) / len(tech_scores)
                    f.write(f"\nTechnical Performance: {tech_avg:.1f}/10 ({len(tech_responses)} questions)\n")
                
                if behavioral_responses:
                    behavioral_scores = [r.get("score", 0) for r in behavioral_responses]
                    behavioral_avg = sum(behavioral_scores) / len(behavioral_scores)
                    f.write(f"Behavioral Performance: {behavioral_avg:.1f}/10 ({len(behavioral_responses)} questions)\n")
                
                # AI Assessment
                f.write("\nAI ASSESSMENT SUMMARY:\n")
                f.write("-"*40 + "\n")
                f.write(f"{ai_summary}\n")
                
                # Question-by-Question Analysis
                f.write("\n" + "="*70 + "\n")
                f.write("QUESTION-BY-QUESTION ANALYSIS\n")
                f.write("="*70 + "\n\n")
                
                for i, response in enumerate(self.interview_data['responses']):
                    if i == 0:
                        # Introduction
                        f.write("INTRODUCTION:\n")
                        f.write("-"*40 + "\n")
                        f.write(f"Question: {response['question']}\n\n")
                        f.write(f"Response: {response['answer']}\n\n")
                        f.write(f"Response Length: {response.get('word_count', 0)} words\n")
                        f.write(f"Score: {response.get('score', 0)}/10\n")
                        f.write("\nIntroduction Analysis:\n")
                        f.write(f"  • Primary Skill Identified: {candidate_info.get('primary_skill', 'N/A').title()}\n")
                        f.write(f"  • Experience Level: {candidate_info.get('experience', 'N/A').title()}\n")
                        f.write(f"  • Confidence Level: {candidate_info.get('confidence', 'N/A').title()}\n")
                        f.write(f"  • Communication Quality: {candidate_info.get('communication', 'N/A').title()}\n")
                        f.write("\n")
                    else:
                        # Regular questions
                        q_type = response.get('question_type', 'technical')
                        type_label = "TECHNICAL" if q_type == "technical" else "BEHAVIORAL"
                        
                        f.write(f"QUESTION {i} ({type_label}):\n")
                        f.write("-"*40 + "\n")
                        
                        # Clean question display
                        question_text = response['question']
                        if '[AI-Generated' in question_text:
                            question_text = question_text.split('] ', 1)[-1]
                        f.write(f"Question: {question_text}\n\n")
                        
                        f.write(f"Response: {response['answer']}\n\n")
                        f.write(f"Word Count: {response.get('word_count', 0)}\n")
                        f.write(f"Overall Score: {response.get('score', 0)}/10\n")
                        
                        # Detailed scores if available
                        evaluation = response.get('evaluation', {})
                        if 'technical_accuracy' in evaluation:
                            f.write("\nDetailed Evaluation:\n")
                            f.write(f"  • Technical Accuracy: {evaluation.get('technical_accuracy', 0)}/10\n")
                            f.write(f"  • Completeness: {evaluation.get('completeness', 0)}/10\n")
                            f.write(f"  • Clarity: {evaluation.get('clarity', 0)}/10\n")
                            f.write(f"  • Depth: {evaluation.get('depth', 0)}/10\n")
                            f.write(f"  • Practicality: {evaluation.get('practicality', 0)}/10\n")
                        
                        # Strengths and weaknesses
                        if evaluation.get('strengths'):
                            f.write(f"\nStrengths:\n")
                            for strength in evaluation['strengths']:
                                f.write(f"  • {strength}\n")
                        
                        if evaluation.get('weaknesses'):
                            f.write(f"\nAreas for Improvement:\n")
                            for weakness in evaluation['weaknesses']:
                                f.write(f"  • {weakness}\n")
                        
                        f.write("\n" + "-"*40 + "\n\n")
                
                # Final Recommendation
                f.write("\n" + "="*70 + "\n")
                f.write("FINAL RECOMMENDATION\n")
                f.write("="*70 + "\n\n")
                
                # Calculate recommendation
                tech_score = 0
                if tech_responses:
                    tech_score = sum(r.get("score", 0) for r in tech_responses) / len(tech_responses)
                
                behavioral_score = 0
                if behavioral_responses:
                    behavioral_score = sum(r.get("score", 0) for r in behavioral_responses) / len(behavioral_responses)
                
                # Write recommendation
                if avg_score >= 8.5 and tech_score >= 8:
                    f.write("RECOMMENDATION: STRONGLY ACCEPT ✅\n\n")
                    f.write("RATIONALE:\n")
                    f.write("- Excellent technical depth and problem-solving skills demonstrated\n")
                    f.write("- Strong communication abilities with clear, structured responses\n")
                    f.write("- Shows initiative, leadership potential, and practical experience\n")
                    f.write("- Consistently high performance across all question types\n")
                elif avg_score >= 7.0 and tech_score >= 6.5:
                    f.write("RECOMMENDATION: ACCEPT WITH CONFIDENCE 👍\n\n")
                    f.write("RATIONALE:\n")
                    f.write("- Solid technical foundation with good understanding of core concepts\n")
                    f.write("- Effective communication skills with room for refinement\n")
                    f.write("- Shows potential for growth and learning agility\n")
                    f.write("- Reliable performance with occasional excellence\n")
                elif avg_score >= 5.5:
                    f.write("RECOMMENDATION: CONDITIONAL ACCEPT ⚠️\n\n")
                    f.write("RATIONALE:\n")
                    f.write("- Shows potential but requires improvement in technical depth\n")
                    f.write("- Technical knowledge has noticeable gaps that need addressing\n")
                    f.write("- Could benefit from additional experience and mentorship\n")
                    f.write("- May succeed with proper onboarding and training\n")
                else:
                    f.write("RECOMMENDATION: REJECT ❌\n\n")
                    f.write("RATIONALE:\n")
                    f.write("- Does not meet minimum technical requirements for the role\n")
                    f.write("- Significant gaps in core knowledge areas identified\n")
                    f.write("- Requires substantial improvement before reconsideration\n")
                    f.write("- Responses lack depth and technical accuracy\n")
                
                # Development Plan
                f.write("\nDEVELOPMENT PLAN:\n")
                f.write("-"*40 + "\n")
                
                if tech_score < 6:
                    f.write("1. Technical Skills Development:\n")
                    primary_skill = candidate_info.get('primary_skill', 'backend').title()
                    f.write(f"   • Focus on core concepts in {primary_skill} development\n")
                    f.write("   • Practice explaining technical solutions step-by-step\n")
                    f.write("   • Build small projects to reinforce learning and gain hands-on experience\n")
                    f.write("   • Study system design principles and architectural patterns\n\n")
                
                if behavioral_score < 6 and behavioral_responses:
                    f.write("2. Communication & Behavioral Skills:\n")
                    f.write("   • Practice STAR method (Situation, Task, Action, Result) for behavioral questions\n")
                    f.write("   • Work on articulating project experiences with clear impact metrics\n")
                    f.write("   • Prepare specific examples of challenges overcome and lessons learned\n")
                    f.write("   • Develop concise yet comprehensive response strategies\n\n")
                
                if avg_score >= 7:
                    f.write("3. Next Steps for Strong Candidates:\n")
                    f.write("   • Consider advanced specialization in current skill area\n")
                    f.write("   • Prepare for technical coding rounds and system design interviews\n")
                    f.write("   • Research company-specific technologies and business domains\n")
                    f.write("   • Continue building portfolio with complex, real-world projects\n")
                else:
                    f.write("3. Improvement Roadmap:\n")
                    f.write("   • Complete foundational courses in identified weak areas\n")
                    f.write("   • Participate in coding challenges and technical communities\n")
                    f.write("   • Seek mentorship from experienced professionals\n")
                    f.write("   • Re-apply after 3-6 months of focused improvement\n")
                
                # Footer
                f.write("\n" + "="*70 + "\n")
                f.write("END OF REPORT\n")
                f.write("Generated by Virtual HR Interviewer v1.0\n")
                f.write("="*70 + "\n")
            
            print(f"\n✅ Comprehensive report saved to: {self.report_filename}")
            
        except Exception as e:
            print(f"Error writing comprehensive report: {e}")
            import traceback
            traceback.print_exc()
    
    def get_current_question(self) -> str:
        """Get the current question being asked"""
        if self.interview_data["questions_asked"]:
            last_question = self.interview_data["questions_asked"][-1]
            # Clean AI tags for display
            if '[AI-Generated' in last_question:
                if '] ' in last_question:
                    return last_question.split('] ', 1)[1]
            return last_question
        return ""
    
    def _generate_streamlit_report(self):
        """Generate a report optimized for Streamlit display"""
        # This can be a simplified version of your existing report generation
        # that formats data for easy display in Streamlit
        
        report_data = {
            "summary": {
                "total_questions": len(self.interview_data["questions_asked"]) - 1,
                "scores": [],
                "average_score": 0
            },
            "questions": []
        }
        
        # Calculate average score
        if len(self.interview_data["responses"]) > 1:
            scores = [r.get("score", 0) for r in self.interview_data["responses"][1:]]
            report_data["summary"]["average_score"] = sum(scores) / len(scores)
            report_data["summary"]["scores"] = scores
        
        # Format questions for display
        for i, response in enumerate(self.interview_data["responses"]):
            if i == 0:
                continue
            question_data = {
                "number": i,
                "question": response["question"],
                "answer": response["answer"],
                "score": response.get("score", 0),
                "word_count": response.get("word_count", 0)
            }
            if "evaluation" in response:
                question_data["evaluation"] = response["evaluation"]
            report_data["questions"].append(question_data)
        
        self.streamlit_report = report_data
        return report_data