import openai
import re
from typing import Dict, List, Tuple
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
from utils import extract_skills, analyze_response_quality
from config import SKILL_CATEGORIES
from skill_detector import SkillDetector 

class ResponseAnalyzer:
    def __init__(self):
        openai.api_key = OPENROUTER_API_KEY
        openai.api_base = OPENROUTER_BASE_URL

    def analyze_introduction(self, response: str) -> Dict: # type: ignore
        """Analyze candidate's introduction with better AI analysis"""
        prompt = f"""
        Analyze this candidate introduction comprehensively:

        Response: {response}

        Provide analysis in this exact format:
        Skills: [comma separated list]
        Experience Level: [junior/mid/senior]
        Primary Technical Area: [backend/frontend/fullstack/devops/data/mobile]
        Confidence: [low/medium/high]
        Communication: [weak/adequate/strong]
        Projects Mentioned: [number]

        Evaluate based on:
        1. Clarity of career narrative
        2. Technical skills demonstrated
        3. Project experience details
        4. Achievements mentioned
        5. Professional communication
        """

        try:
            response_analysis = openai.ChatCompletion.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are a technical recruiter evaluating candidate introductions in a medium-difficulty interview.
                            - Assume candidates are junior-to-mid level unless explicitly stated otherwise.
                            - Base all judgments strictly on the response; do not inflate skills, experience, or confidence.
                            - Focus on technical skills demonstrated, project experience, clarity of communication, and professional tone.
                            - Provide output EXACTLY in the format specified by the user.
                            - Be fair and slightly liberal in interpretation, but avoid exaggeration.
                        """
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=250
            )

            analysis_text = response_analysis.choices[0].message.content  # type: ignore
            return self._parse_intro_analysis(analysis_text, response)

        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._enhanced_fallback_analysis(response)


    def _parse_intro_analysis(self, analysis_text: str, original_response: str) -> Dict:
        """Parse introduction analysis with detailed metrics"""
        # Initialize with defaults
        result = {
            "skills": [],
            "experience": "mid",
            "primary_skill": "frontend",
            "confidence": "medium",
            "communication": "adequate",
            "projects_mentioned": 0,
            "word_count": len(original_response.split()),
            "intro_score": 7
        }
        
        # If analysis_text is empty or too short, use fallback
        if not analysis_text or len(analysis_text.strip()) < 20:
            print("AI analysis text too short, using enhanced fallback")
            return self._enhanced_fallback_analysis(original_response)
        
        lines = analysis_text.strip().split('\n')
        
        # Try to extract information with multiple patterns
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            
            # Extract skills with multiple patterns
            if "skill" in line_lower and ("primary" in line_lower or "main" in line_lower or ":" in line):
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        skill_text = parts[1].strip()
                        # Extract skill from text
                        skill = self._extract_skill_from_text(skill_text)
                        if skill:
                            result["primary_skill"] = skill
            
            # Extract experience level
            elif "experience" in line_lower and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    exp_text = parts[1].strip().lower()
                    result["experience"] = self._categorize_experience(exp_text)
            
            # Extract confidence
            elif "confidence" in line_lower and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    conf_text = parts[1].strip().lower()
                    result["confidence"] = self._categorize_confidence(conf_text)
            
            # Extract communication
            elif "communication" in line_lower and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    comm_text = parts[1].strip().lower()
                    result["communication"] = self._categorize_communication(comm_text)
            
            # Extract projects count
            elif "project" in line_lower and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    try:
                        result["projects_mentioned"] = int(parts[1].strip())
                    except:
                        # Try to extract number from text
                        numbers = re.findall(r'\d+', parts[1])
                        if numbers:
                            result["projects_mentioned"] = int(numbers[0])
            
            # Extract all skills mentioned (not just primary)
            elif "skill" in line_lower and ":" in line and "primary" not in line_lower and "main" not in line_lower:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    skills_text = parts[1].strip()
                    # Parse comma-separated skills
                    skills = [s.strip().lower() for s in skills_text.split(",") if s.strip()]
                    if skills:
                        result["skills"] = skills
        
        # If no skills extracted, use fallback extraction
        if not result["skills"]:
            result["skills"] = extract_skills(original_response)
        
        # Calculate a more nuanced score based on the actual response content
        result["intro_score"] = self._calculate_intro_score(result, original_response)
        
        # If we got generic defaults, try to infer better from the response
        if result["primary_skill"] == "frontend" and result["experience"] == "mid" and result["confidence"] == "medium":
            # Try to infer from response content
            result = self._infer_from_content(original_response, result)
        
        return result
    
    def _extract_skill_from_text(self, text: str) -> str:

        """Extract skill category from text"""
        return SkillDetector.detect_primary_skill(text)

    def _categorize_experience(self, text: str) -> str:
        """Categorize experience level from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["junior", "entry", "beginner", "early", "0-2", "1-3"]):
            return "junior"
        elif any(word in text_lower for word in ["senior", "lead", "principal", "expert", "5+", "7+", "10+"]):
            return "senior"
        else:
            return "mid"

    def _categorize_confidence(self, text: str) -> str:
        """Categorize confidence level from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["high", "strong", "very confident", "excellent"]):
            return "high"
        elif any(word in text_lower for word in ["low", "weak", "not confident", "poor"]):
            return "low"
        else:
            return "medium"

    def _categorize_communication(self, text: str) -> str:
        """Categorize communication quality from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["strong", "excellent", "good", "clear", "effective"]):
            return "strong"
        elif any(word in text_lower for word in ["weak", "poor", "unclear", "needs improvement"]):
            return "weak"
        else:
            return "adequate"

    def _calculate_intro_score(self, analysis: Dict, response: str) -> int:
        """Calculate introduction score based on multiple factors"""
        score = 7  # Base score
        
        # Factor 1: Word count (100-300 words is ideal)
        word_count = analysis["word_count"]
        if 150 <= word_count <= 350:
            score += 1
        elif word_count < 80:
            score -= 1
        elif word_count > 500:
            score -= 1
        
        # Factor 2: Skills mentioned
        skills_count = len(analysis["skills"])
        if skills_count >= 5:
            score += 1
        elif skills_count <= 2:
            score -= 1
        
        # Factor 3: Experience level (senior gets bonus)
        if analysis["experience"] == "senior":
            score += 1
        elif analysis["experience"] == "junior":
            score -= 0.5
        
        # Factor 4: Confidence
        if analysis["confidence"] == "high":
            score += 1
        elif analysis["confidence"] == "low":
            score -= 1
        
        # Factor 5: Communication
        if analysis["communication"] == "strong":
            score += 1
        elif analysis["communication"] == "weak":
            score -= 1
        
        # Factor 6: Projects mentioned
        if analysis["projects_mentioned"] >= 2:
            score += 1
        elif analysis["projects_mentioned"] == 0:
            score -= 1
        
        # Factor 7: Check for specific content indicators
        response_lower = response.lower()
        if any(term in response_lower for term in ["implemented", "developed", "built", "created"]):
            score += 0.5
        if any(term in response_lower for term in ["achieved", "improved", "increased", "reduced"]):
            score += 0.5
        if "team" in response_lower or "collaborat" in response_lower:
            score += 0.5
        
        # Ensure score is between 1-10
        return max(1, min(10, int(score)))

    def _infer_from_content(self, response: str, current_result: Dict) -> Dict:
        """Infer analysis from response content when AI gives generic results"""
        response_lower = response.lower()
        
        # Use SkillDetector
        primary_skill = SkillDetector.detect_primary_skill(response)
        skill_keywords = SkillDetector.get_skill_keywords(primary_skill)
        
        # Count keyword occurrences
        keyword_count = sum(1 for keyword in skill_keywords if keyword in response_lower)
        
        # Only update if we have strong evidence
        if keyword_count >= 2:
            current_result["primary_skill"] = primary_skill

        # Infer experience from content
        word_count = len(response.split())
        junior_indicators = [
            # Experience level phrases
            "junior", "entry", "fresher", "beginner", "early", "starting",

            # Education / transition
            "graduate", "recent graduate", "new graduate", "final year",
            "bootcamp", "intern", "internship", "trainee", "learning",

            # Experience years
            "0 years", "1 year", "2 years", "3 years"

            # Responsibility cues
            "assisted", "supported", "worked under",
            "followed guidance", "contributed",
            "basic understanding", "fundamentals",
            "hands-on practice", "hands on practice",

            # Job intent
            "seeking", "first role", "looking for opportunity",
            "open to learning", "eager to learn"
        ]

        senior_indicators = [
            # Titles / level
            "senior", "lead", "principal", "staff",
            "technical lead", "team lead",

            # Leadership & ownership
            "led", "managed", "owned", "mentored", "guided",
            "hired", "interviewed", "decision making",

            # Experience years
            "4 years", "5 years", "6 years", "7 years",
            "8 years", "9 years", "10 years", "11 years", "12 years",
        ]


        senior_count = sum(1 for indicator in senior_indicators if indicator in response_lower)
        junior_count = sum(1 for indicator in junior_indicators if indicator in response_lower)
        
        if senior_count > 2:
            current_result["experience"] = "senior"
            current_result["confidence"] = "high"
        elif junior_count > 1:
            current_result["experience"] = "junior"
            current_result["confidence"] = "medium"
        elif word_count > 300:
            current_result["experience"] = "senior"
            current_result["confidence"] = "high"
        elif word_count < 100:
            current_result["experience"] = "junior"
            current_result["confidence"] = "medium"
        
        # Infer confidence from sentence structure and assertiveness
        confident_indicators = ["confident", "experienced", "expert", "proficient", "strong", "extensive"]
        uncertain_indicators = ["basic", "familiar", "learning", "beginner", "some experience"]
        
        confident_count = sum(1 for indicator in confident_indicators if indicator in response_lower)
        uncertain_count = sum(1 for indicator in uncertain_indicators if indicator in response_lower)
        
        if confident_count > uncertain_count:
            current_result["confidence"] = "high"
        elif uncertain_count > confident_count:
            current_result["confidence"] = "low"
        
        return current_result

    def _enhanced_fallback_analysis(self, response: str) -> Dict:
        """Enhanced fallback analysis with better inference"""
        from utils import extract_skills
        
        skills = extract_skills(response)
        word_count = len(response.split())
        
        # Enhanced skill inference
        
        primary_skill = SkillDetector.detect_primary_skill(response)

        
        # Enhanced experience inference
        senior_keywords = ["led", "managed", "architected", "designed", "mentored", "10+", "6+", "7+", "8+", "9+", "senior", "principal", "lead"]
        junior_keywords = ["recent graduate", "bootcamp", "entry level", "seeking first","0-2 years", "1-3 years", "3 years", "months", "1 years", "2 years", "junior"]
        
        senior_count = sum(1 for keyword in senior_keywords if keyword in response.lower())
        junior_count = sum(1 for keyword in junior_keywords if keyword in response.lower())
        
        if senior_count > 2:
            experience = "senior"
            confidence = "high"
        elif junior_count > 1:
            experience = "junior"
            confidence = "medium"
        elif word_count > 400:
            experience = "senior"
            confidence = "high"
        elif word_count < 150:
            experience = "junior"
            confidence = "medium"
        else:
            experience = "mid"
            confidence = "medium"
        
        # Enhanced project counting
        project_patterns = [
            r"project\s+(?:called|named|titled)?\s*['\"]?([^'\"]+)['\"]?",
            r"built\s+(?:a|an)?\s*([^,.]+)",
            r"developed\s+(?:a|an)?\s*([^,.]+)",
            r"created\s+(?:a|an)?\s*([^,.]+)"
        ]
        
        projects_mentioned = 0
        for pattern in project_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            projects_mentioned += len(matches)
        
        # Enhanced communication assessment
        sentence_count = len([s for s in response.split('.') if s.strip()])
        avg_sentence_length = word_count / max(1, sentence_count)
        
        if avg_sentence_length > 25 or word_count > 500:
            communication = "weak"  # Too verbose
        elif avg_sentence_length < 10 or word_count < 80:
            communication = "weak"  # Too brief
        else:
            communication = "adequate"
        
        # Calculate score
        intro_score = 6
        if len(skills) >= 4:
            intro_score += 1
        if projects_mentioned >= 2:
            intro_score += 1
        if 150 <= word_count <= 400:
            intro_score += 1
        if confidence == "high":
            intro_score += 1
        if communication == "adequate":
            intro_score += 1
        
        return {
            "skills": skills,
            "experience": experience,
            "primary_skill": primary_skill,
            "confidence": confidence,
            "communication": communication,
            "projects_mentioned": projects_mentioned,
            "word_count": word_count,
            "intro_score": min(10, max(1, intro_score))
        }

    def evaluate_answer(self, question: str, answer: str) -> Dict:
        """Evaluate candidate's answer quality with detailed scoring"""
        
        # First, get basic metrics
        word_count = len(answer.split())
        metrics = analyze_response_quality(answer)
        
        # Use AI for detailed evaluation
        prompt = f"""
            Evaluate this technical interview answer:
            
            Question: {question}
            Answer: {answer}
            
            Score on a scale of 1-10 for each category:
            1. Technical Accuracy (1-10): How correct is the technical information?
            2. Completeness (1-10): Does it fully address the question?
            3. Clarity (1-10): Is it well-structured and easy to understand?
            4. Depth (1-10): Does it show deep understanding or just surface-level?
            5. Practicality (1-10): Does it include real-world examples or applications?
            
            Also consider:
            - Word count: {word_count} (ideal: 80-200 words)
            - Technical terms used appropriately?
            - Examples provided?
            - Structure and organization?
            
            Provide scores in this exact format:
            Technical Accuracy: [score]
            Completeness: [score]
            Clarity: [score]
            Depth: [score]
            Practicality: [score]
            Overall: [average score]
            Strengths: [key strengths]
            Weaknesses: [areas for improvement]
        """
        
        try:
            evaluation = openai.ChatCompletion.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {"role": "system", "content": "You are a technical interviewer evaluating answers. Be fair but critical."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=250
            )
            
            eval_text = evaluation.choices[0].message.content # type: ignore
            return self._parse_detailed_evaluation(eval_text, word_count, metrics)
            
        except Exception as e:
            print(f"AI evaluation error: {e}")
            # Fallback to rule-based scoring
            return self._fallback_evaluation(question, answer, word_count, metrics)

    def _parse_detailed_evaluation(self, eval_text: str, word_count: int, metrics: Dict) -> Dict:
        """Parse detailed AI evaluation"""
        scores = {
            "technical_accuracy": 5,
            "completeness": 5,
            "clarity": 5,
            "depth": 5,
            "practicality": 5,
            "overall": 5,
            "strengths": [],
            "weaknesses": []
        }
        
        lines = eval_text.strip().split('\n')
        strengths_found = False
        weaknesses_found = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Parse scores
            if "technical accuracy:" in line_lower:
                try:
                    scores["technical_accuracy"] = float(line.split(":", 1)[1].strip())
                except:
                    pass
            elif "completeness:" in line_lower:
                try:
                    scores["completeness"] = float(line.split(":", 1)[1].strip())
                except:
                    pass
            elif "clarity:" in line_lower:
                try:
                    scores["clarity"] = float(line.split(":", 1)[1].strip())
                except:
                    pass
            elif "depth:" in line_lower:
                try:
                    scores["depth"] = float(line.split(":", 1)[1].strip())
                except:
                    pass
            elif "practicality:" in line_lower:
                try:
                    scores["practicality"] = float(line.split(":", 1)[1].strip())
                except:
                    pass
            elif "overall:" in line_lower:
                try:
                    scores["overall"] = float(line.split(":", 1)[1].strip())
                except:
                    pass
            
            # Parse strengths and weaknesses
            elif "strengths:" in line_lower:
                strengths_found = True
                weaknesses_found = False
                strength_text = line.split(":", 1)[1].strip()
                if strength_text:
                    scores["strengths"].append(strength_text)
            elif "weaknesses:" in line_lower:
                strengths_found = False
                weaknesses_found = True
                weakness_text = line.split(":", 1)[1].strip()
                if weakness_text:
                    scores["weaknesses"].append(weakness_text)
            elif strengths_found and line_lower and not line_lower.startswith(("technical", "completeness", "clarity", "depth", "practicality", "overall", "weaknesses")):
                scores["strengths"].append(line.strip())
            elif weaknesses_found and line_lower and not line_lower.startswith(("technical", "completeness", "clarity", "depth", "practicality", "overall", "strengths")):
                scores["weaknesses"].append(line.strip())

        
        # Adjust based on word count (80-200 words ideal for technical answers)
        if 80 <= word_count <= 200:
            scores["completeness"] = min(10, scores["completeness"] + 1)
            scores["overall"] = min(10, (sum([scores["technical_accuracy"], scores["completeness"], 
                                            scores["clarity"], scores["depth"], scores["practicality"]]) / 5))
        elif word_count < 50:
            scores["completeness"] = max(1, scores["completeness"] - 2)
            scores["overall"] = max(1, scores["overall"] - 1)
        elif word_count > 300:
            scores["clarity"] = max(1, scores["clarity"] - 1)
        
        # Adjust based on metrics
        if metrics["has_examples"]:
            scores["practicality"] = min(10, scores["practicality"] + 1)
        
        if metrics["has_technical_terms"]:
            scores["technical_accuracy"] = min(10, scores["technical_accuracy"] + 0.5)
        
        # Ensure overall is average of categories
        category_scores = [scores["technical_accuracy"], scores["completeness"], 
                            scores["clarity"], scores["depth"], scores["practicality"]]
        scores["overall"] = sum(category_scores) / len(category_scores)
        
        # Round scores
        for key in scores:
            if isinstance(scores[key], (int, float)):
                scores[key] = round(scores[key], 1)
        
        return scores

    def _fallback_evaluation(self, question: str, answer: str, word_count: int, metrics: Dict) -> Dict:
        """Fallback evaluation when AI fails"""
        base_score = 5
        
        # Adjust based on word count
        if 100 <= word_count <= 250:
            base_score = 7
        elif 50 <= word_count < 100:
            base_score = 6
        elif word_count < 50:
            base_score = 4
        elif word_count > 300:
            base_score = 6  # Might be too verbose
        
        # Adjust based on metrics
        if metrics["has_examples"]:
            base_score += 1
        if metrics["has_technical_terms"]:
            base_score += 1
        if metrics["has_explanation"]:
            base_score += 1
        
        # Check for question-specific indicators
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        if "debug" in question_lower and any(term in answer_lower for term in ["log", "monitor", "analyze", "profile"]):
            base_score += 1
        
        if "design" in question_lower and any(term in answer_lower for term in ["scalable", "architecture", "components", "trade-off"]):
            base_score += 1
        
        if "difference between" in question_lower and any(term in answer_lower for term in ["vs", "versus", "while", "whereas", "on the other hand"]):
            base_score += 1
        
        # Cap score
        final_score = max(1, min(10, base_score))
        
        # Generate simple strengths/weaknesses
        strengths = []
        weaknesses = []
        
        if word_count >= 100:
            strengths.append("Provides detailed explanations")
        else:
            weaknesses.append("Could provide more detail")
        
        if metrics["has_examples"]:
            strengths.append("Uses practical examples")
        else:
            weaknesses.append("Lacks concrete examples")
        
        return {
            "technical_accuracy": final_score,
            "completeness": final_score,
            "clarity": final_score,
            "depth": final_score,
            "practicality": final_score,
            "overall": final_score,
            "strengths": strengths[:2],
            "weaknesses": weaknesses[:2]
        }

    def check_for_termination(self, response: str) -> Tuple[bool, str]:
        """Check if interview should be terminated"""
        from config import ABUSIVE_KEYWORDS, TERMINATION_KEYWORDS
        
        if not response or response.isspace():
            return False, ""
        
        response_lower = response.lower().strip()
        
        # Check for abusive language
        for keyword in ABUSIVE_KEYWORDS:
            if keyword in response_lower:
                return True, "misconduct"
        
        # Check for explicit termination request
        if response_lower in TERMINATION_KEYWORDS:
            return True, "candidate_request"
        
        # Check for extremely poor responses
        if len(response.split()) < 5 and "skip" not in response_lower:
            return True, "poor_response"
        
        return False, ""
    
    def analyze_introduction(self, response: str) -> Dict:
        """Analyze candidate's introduction with better AI analysis"""
        prompt = f"""
            Analyze the candidate's introduction as a technical recruiter conducting a
            medium-difficulty interview.

            Response:
            {response[:500]}

            Evaluation guidelines:
            - Be fair and slightly liberal in interpretation, but do NOT overestimate the
            candidate’s skills, experience, or confidence beyond what is clearly stated.
            - Base all judgments strictly on the content provided.
            - Assume a junior-to-mid level candidate unless strong evidence suggests otherwise.
            - Avoid generic assumptions or exaggerated classifications.

            Provide the analysis in EXACTLY the following format:

            Skills: [comma-separated list of specific technical skills explicitly mentioned or strongly implied]
            Experience Level: [junior/mid/senior]
            Primary Technical Area: [backend/frontend/fullstack/devops/data/mobile]
            Confidence: [low/medium/high]
            Communication: [weak/adequate/strong]
            Projects Mentioned: [number]

            Evaluation focus:
            - Technical skills demonstrated (not guessed)
            - Clarity and structure of the introduction
            - Evidence of hands-on or project experience
            - Professional tone and confidence level
        """
        
        try:
            print("[DEBUG] Sending to AI for analysis...")
            response_analysis = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": '''
                            You are a technical recruiter evaluating candidate responses during an interview. Analyze each answer carefully and provide specific, detailed, and objective feedback based strictly on the content provided.
                            Evaluate the candidate liberally and fairly, recognizing effort, clarity, and correct reasoning, but do not inflate scores or assessments beyond what the response genuinely demonstrates.
                            The interview difficulty level should be considered medium, so expectations should align with a competent junior-to-mid-level candidate rather than an expert.
                            Focus your evaluation on:
                            Technical correctness and conceptual understanding
                            Clarity of explanation and communication
                            Practical thinking and real-world relevance
                            Completeness of the response relative to the question
                            Be balanced in your judgment: acknowledge strengths clearly, point out gaps constructively, and avoid overly harsh or overly generous evaluations. The goal is to provide a realistic assessment of the candidate’s readiness at a medium-level technical interview. 
                    '''},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Slightly higher temperature for more varied responses
                max_tokens=250
            )
            
            analysis_text = response_analysis.choices[0].message.content # type: ignore
            # (f"[DEBUG] AI Response:\n{analysis_text}")
            
            return self._parse_intro_analysis(analysis_text, response)
        except Exception as e:
            print(f"[DEBUG] AI analysis error: {e}")
            return self._enhanced_fallback_analysis(response)
        
    