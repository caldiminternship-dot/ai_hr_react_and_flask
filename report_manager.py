# report_manager.py
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

class ReportManager:
    def __init__(self, reports_dir: str = "interview_reports"):
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def save_interview_report(self, session_state: Dict) -> str:
        """Save interview report to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"candidate_report_{timestamp}"
        
        # Save JSON report
        json_path = os.path.join(self.reports_dir, f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self._prepare_report_data(session_state), f, indent=2, ensure_ascii=False)
        
        # Save text report
        text_path = os.path.join(self.reports_dir, f"{filename}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_text_report(session_state))
        
        # Save CSV summary
        csv_path = os.path.join(self.reports_dir, f"{filename}.csv")
        self._save_csv_summary(session_state, csv_path)
        
        return json_path
    
    def _prepare_report_data(self, session_state: Dict) -> Dict:
        """Prepare report data for JSON serialization"""
        return {
            "report_id": f"INT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "candidate_profile": session_state.get('candidate_profile', {}),
            "question_evaluations": session_state.get('question_evaluations', []),
            "overall_score": session_state.get('overall_score', 0),
            "final_score": session_state.get('final_score', 0),
            "total_questions": len(session_state.get('questions', [])),
            "questions_answered": len(session_state.get('question_evaluations', [])),
            "introduction_analyzed": session_state.get('introduction_analyzed', False),
            "interview_duration": self._calculate_duration(session_state),
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_duration(self, session_state: Dict) -> Optional[str]:
        """Calculate interview duration from messages"""
        messages = session_state.get('messages', [])
        if len(messages) >= 2:
            try:
                first_time = messages[0].get('timestamp', '00:00:00')
                last_time = messages[-1].get('timestamp', '00:00:00')
                
                # Simple duration calculation
                fmt = "%H:%M:%S"
                t1 = datetime.strptime(first_time, fmt)
                t2 = datetime.strptime(last_time, fmt)
                duration = t2 - t1
                return str(duration)
            except:
                return None
        return None
    
    def _generate_text_report(self, session_state: Dict) -> str:
        """Generate human-readable text report"""
        report = "=" * 70 + "\n"
        report += "VIRTUAL HR INTERVIEWER - CANDIDATE REPORT\n"
        report += "=" * 70 + "\n\n"
        
        # Header
        report += f"Report ID: INT{datetime.now().strftime('%Y%m%d%H%M%S')}\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "-" * 70 + "\n\n"
        
        # Summary
        profile = session_state.get('candidate_profile', {})
        report += "CANDIDATE SUMMARY\n"
        report += "-" * 40 + "\n"
        report += f"Experience Level: {profile.get('experience_level', 'N/A')}\n"
        report += f"Primary Skill Area: {profile.get('primary_skill', 'N/A')}\n"
        report += f"Confidence Level: {profile.get('confidence', 'N/A')}\n"
        report += f"Communication: {profile.get('communication', 'N/A')}\n"
        report += f"Introduction Score: {profile.get('intro_score', 'N/A')}/10\n"
        
        skills = profile.get("skills", [])
        if skills:
            report += f"Skills Identified: {', '.join(skills)}\n"
        
        report += f"Questions Answered: {len(session_state.get('question_evaluations', []))}\n"
        report += f"Overall Score: {session_state.get('overall_score', 0):.2f}/10\n"
        report += f"Final Score: {session_state.get('final_score', 0):.2f}/10\n\n"
        
        # Detailed Question Analysis
        report += "DETAILED QUESTION ANALYSIS\n"
        report += "-" * 40 + "\n\n"
        
        evaluations = session_state.get('question_evaluations', [])
        for i, eval_data in enumerate(evaluations):
            evaluation = eval_data['evaluation']
            report += f"QUESTION {i+1}\n"
            report += f"Question: {eval_data['question']}\n"
            report += f"Score: {evaluation.get('overall', 0)}/10\n"
            
            # Category scores
            categories = [
                ("Technical Accuracy", "technical_accuracy"),
                ("Completeness", "completeness"),
                ("Clarity", "clarity"),
                ("Depth", "depth"),
                ("Practicality", "practicality")
            ]
            
            for label, key in categories:
                score = evaluation.get(key, 0)
                report += f"  {label}: {score}/10\n"
            
            if evaluation.get('strengths'):
                report += "  Strengths:\n"
                for strength in evaluation['strengths']:
                    report += f"    • {strength}\n"
            
            if evaluation.get('weaknesses'):
                report += "  Areas for Improvement:\n"
                for weakness in evaluation['weaknesses']:
                    report += f"    • {weakness}\n"
            
            report += "\n" + "-" * 40 + "\n\n"
        
        # Statistics
        if evaluations:
            scores = [e["evaluation"]["overall"] for e in evaluations]
            report += "STATISTICS\n"
            report += "-" * 40 + "\n"
            report += f"Average Score: {sum(scores)/len(scores):.2f}/10\n"
            report += f"Highest Score: {max(scores)}/10\n"
            report += f"Lowest Score: {min(scores)}/10\n"
            report += f"Score Range: {max(scores) - min(scores):.2f}\n\n"
        
        # Recommendation
        report += "RECOMMENDATION\n"
        report += "-" * 40 + "\n"
        
        overall = session_state.get('overall_score', 0)
        if overall >= 7:
            report += "✅ STRONGLY RECOMMEND\n"
            report += "The candidate demonstrates strong technical understanding,\n"
            report += "excellent communication skills, and shows good potential.\n"
        elif overall >= 5:
            report += "⚠️ CONDITIONAL RECOMMEND\n"
            report += "The candidate shows potential but needs improvement in\n"
            report += "some technical areas or communication.\n"
        else:
            report += "❌ NOT RECOMMENDED\n"
            report += "The candidate needs significant improvement in technical\n"
            report += "knowledge and communication skills.\n"
        
        report += "\n" + "=" * 70 + "\n"
        report += "END OF REPORT\n"
        report += "=" * 70
        
        return report
    
    def _save_csv_summary(self, session_state: Dict, csv_path: str):
        """Save summary as CSV for easy analysis"""
        evaluations = session_state.get('question_evaluations', [])
        
        if evaluations:
            data = []
            for i, eval_data in enumerate(evaluations):
                evaluation = eval_data['evaluation']
                row = {
                    'question_number': i + 1,
                    'overall_score': evaluation.get('overall', 0),
                    'technical_accuracy': evaluation.get('technical_accuracy', 0),
                    'completeness': evaluation.get('completeness', 0),
                    'clarity': evaluation.get('clarity', 0),
                    'depth': evaluation.get('depth', 0),
                    'practicality': evaluation.get('practicality', 0)
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
    
    def get_all_reports(self) -> List[Dict]:
        """Load all saved reports"""
        reports = []
        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.reports_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        report['filename'] = filename
                        report['filepath'] = filepath
                        reports.append(report)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return reports