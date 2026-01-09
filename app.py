import streamlit as st
import time
import os
from datetime import datetime
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from response_analyzer import ResponseAnalyzer
from report_manager import ReportManager
from question_generator import QuestionGenerator
import json

# Initialize report manager
report_manager = ReportManager()

# Initialize the analyzer
analyzer = ResponseAnalyzer()

# Initialize QuestionGenerator
question_generator = QuestionGenerator()

# Page configuration
st.set_page_config(
    page_title="Virtual HR Interviewer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
css = """
<style>
    /* ===== BASE THEME ===== */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ===== HEADER STYLING ===== */
    .main-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin: 1rem auto 2rem;
        max-width: 95%;
        box-shadow: 
            0 10px 25px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
    }

    .main-header h1 {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.75rem;
        text-align: center;
    }

    .main-header p {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
        text-align: center;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .header {
        text-align:center;
        padding: 1.5rem 1rem;
        margin: 0.5rem 0 1.5rem;
    }
    
    /* ===== CARD STYLING ===== */
    .stCard {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .stCard:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    /* ===== CHAT INTERFACE ===== */
    .chat-container {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }

    .chat-message {
        padding: 1.25rem;
        border-radius: 14px;
        margin: 1rem 0;
        border-left: 4px solid;
        animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .interviewer-message {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(67, 56, 202, 0.1) 100%);
        border-color: #4f46e5;
        margin-right: 2rem;
    }

    .candidate-message {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-color: #10b981;
        margin-left: 2rem;
    }

    .system-message {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
        border-color: #f59e0b;
        margin: 1rem auto;
        max-width: 90%;
    }

    /* ===== BUTTON STYLING ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.6s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(99, 102, 241, 0.3);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* ===== INPUT FIELDS ===== */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.8);
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        min-height: 150px;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        outline: none;
    }

    .stTextArea textarea::placeholder {
        color: #64748b;
    }

    /* ===== METRIC CARDS ===== */
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }

    .stMetric > div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .stMetric > div[data-testid="stMetricValue"] {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        border-radius: 10px;
    }

    .stProgress > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 10px;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    section[data-testid="stSidebar"] .stButton > button {
        margin-bottom: 0.75rem;
        width: 100%;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30, 41, 59, 0.5);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.7);
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem 1.25rem;
    }

    .streamlit-expanderContent {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.25rem;
    }

    /* ===== STATUS MESSAGES ===== */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }

    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }

    /* ===== CUSTOM STATUS ===== */
    .custom-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-left: 4px solid #10b981;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1.25rem 0;
    }

    .custom-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1.25rem 0;
    }

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9;
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    h1 {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    h2 {
        font-size: 2rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    p, div, span {
        color: #cbd5e1;
        line-height: 1.6;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        margin: 2rem 0;
    }

    /* ===== CODE BLOCKS ===== */
    code {
        background: rgba(30, 41, 59, 0.8);
        color: #7dd3fc;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* ===== SCROLLBAR STYLING ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
    }

    /* ===== GLASS EFFECT UTILITY ===== */
    .glass-effect {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
    }

    /* ===== TOOLTIP STYLING ===== */
    .stTooltip {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.9rem;
    }

    /* ===== ANIMATIONS ===== */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }

    .pulse-animation {
        animation: pulse 2s infinite;
    }

    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1rem;
            margin: 0.5rem 0 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .stCard {
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.75rem 0;
        }
        
        .stButton > button {
            padding: 0.625rem 1.25rem;
            font-size: 0.9rem;
        }
    }

    /* ===== FOCUS STATES ===== */
    :focus-visible {
        outline: 2px solid #6366f1;
        outline-offset: 2px;
        border-radius: 4px;
    }

    /* ===== SELECTION COLOR ===== */
    ::selection {
        background: rgba(99, 102, 241, 0.3);
        color: white;
    }

    /* ===== LOADING SPINNER ===== */
    .stSpinner > div {
        border-color: #6366f1 transparent transparent transparent;
    }

    /* ===== DATA FRAME STYLING ===== */
    .dataframe {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
    }

    /* ===== FORM STYLING ===== */
    .stSelectbox, .stMultiselect, .stNumberInput, .stDateInput {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
    }

    /* ===== RADIO BUTTONS ===== */
    .stRadio > div {
        background: rgba(15, 23, 42, 0.8);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* ===== CHECKBOX STYLING ===== */
    .stCheckbox > label {
        color: #cbd5e1;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'interview_started': False,
        'interview_active': False,
        'interview_completed': False,
        'interview_terminated': False,
        'current_question_index': 0,
        'questions': [],
        'messages': [],
        'candidate_profile': {},
        'question_evaluations': [],
        'overall_score': 0,
        'final_score': 0,
        'introduction_analyzed': False,
        'intro_analysis': None,
        'termination_reason': '',
        'termination_log': [],
        'current_response': '',
        'total_questions_to_ask': 15,
        'questions_generated': False,
        # TAB SWITCHING DETECTION VARIABLES
        'tab_switch_count': 0,
        'tab_warning_given': False,
        'auto_terminate_tab_switch': False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def generate_adaptive_questions():
    """Generate adaptive questions based on candidate profile"""
    try:
        if not st.session_state.candidate_profile:
            return None
        
        skill_category = st.session_state.candidate_profile.get("primary_skill", "backend")
        experience_level = st.session_state.candidate_profile.get("experience_level", "mid")
        
        # Generate initial skill-based questions
        initial_questions = question_generator.generate_initial_skill_questions(
            skill_category=skill_category,
            candidate_level=experience_level
        )
        
        if not initial_questions:
            # Fallback to default questions if AI generation fails
            initial_questions = [
                "Describe a challenging technical problem you solved recently and how you approached it.",
                "Explain the difference between REST and GraphQL APIs and when you would use each.",
                "How do you handle debugging a complex issue in a production system?"
            ]
        
        # Always include at least one behavioral question
        behavioral_question = question_generator.generate_behavioral_question_ai(
            candidate_background=st.session_state.candidate_profile,
            context=st.session_state.question_evaluations
        )
        
        if behavioral_question:
            initial_questions.append(behavioral_question)
        
        return initial_questions[:st.session_state.total_questions_to_ask]
    
    except Exception as e:
        st.error(f"Error generating adaptive questions: {e}")
        # Fallback to static questions
        return [
            "Describe a challenging technical problem you solved recently and how you approached it.",
            "Explain the difference between REST and GraphQL APIs and when you would use each.",
            "How do you handle debugging a complex issue in a production system?",
            "Describe your experience with version control systems and your typical workflow.",
            "What's your approach to learning new technologies or frameworks?",
            "Tell me about a time you had to work with a difficult team member and how you handled it.",
            "Where do you see yourself in your career in 3-5 years?"
        ]

def get_next_question():
    """Get the next question, generating adaptively if needed"""
    # If we need to generate questions for the first time
    if not st.session_state.questions_generated and st.session_state.introduction_analyzed:
        questions = generate_adaptive_questions()
        if questions:
            st.session_state.questions = questions
            st.session_state.questions_generated = True
            return questions[0] if questions else None
    
    # If we have questions in the list
    if st.session_state.questions:
        current_idx = st.session_state.current_question_index
        if current_idx < len(st.session_state.questions):
            return st.session_state.questions[current_idx]
    
    return None

def process_response(response_text):
    """Process the candidate's response and update interview state"""
    
    if not response_text or response_text.strip() == "":
        st.warning("Please enter a response before submitting.")
        return
    
    # Special handling for tab switching termination
    if "session terminated due to tab switching" in response_text.lower():
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = "misconduct"
        st.session_state.interview_active = False
        
        # Log termination
        if "termination_log" not in st.session_state:
            st.session_state.termination_log = []
        st.session_state.termination_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "reason": "misconduct",
            "response": "Tab switching detected multiple times"
        })
        
        st.rerun()
        return

    # Update chat history
    st.session_state.messages.append({
        "role": "candidate",
        "content": response_text,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Check for termination
    try:
        should_terminate, reason = analyzer.check_for_termination(response_text)
        if should_terminate:
            st.session_state.interview_terminated = True
            st.session_state.termination_reason = reason
            st.session_state.interview_active = False
            
            # Log termination
            if "termination_log" not in st.session_state:
                st.session_state.termination_log = []
            st.session_state.termination_log.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "reason": reason,
                "response": response_text[:100] + "..." if len(response_text) > 100 else response_text
            })
            
            st.rerun()
            return
    except Exception as e:
        st.error(f"Error checking termination: {e}")
    
    # Analyze the response
    try:
        with st.spinner("Analyzing your response..."):
            # For introduction (first response)
            if st.session_state.current_question_index == 0:
                analysis = analyzer.analyze_introduction(response_text)
                
                # Check if interview was terminated by AI analysis
                if analysis.get("terminated", False):
                    st.session_state.interview_terminated = True
                    st.session_state.termination_reason = analysis.get("termination_reason", "unknown")
                    st.session_state.interview_active = False
                    st.rerun()
                    return
                
                # Update candidate profile
                st.session_state.candidate_profile.update({
                    "skills": analysis.get("skills", []),
                    "experience_level": analysis.get("experience", "mid"),
                    "primary_skill": analysis.get("primary_skill", "backend"),
                    "confidence": analysis.get("confidence", "medium"),
                    "communication": analysis.get("communication", "adequate"),
                    "intro_score": analysis.get("intro_score", 5)
                })
                
                # Store introduction analysis
                st.session_state.intro_analysis = analysis
                st.session_state.introduction_analyzed = True
                
                # Move to next question
                st.session_state.current_question_index += 1
                
                # Add system message
                st.session_state.messages.append({
                    "role": "system",
                    "content": f"✅ Introduction analyzed. Generating adaptive questions...",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            
            # For regular questions
            else:
                # Get the current question
                current_question = get_next_question()
                if not current_question and st.session_state.questions:
                    # Fallback to stored questions
                    question_idx = st.session_state.current_question_index - 1
                    if question_idx < len(st.session_state.questions):
                        current_question = st.session_state.questions[question_idx]
                
                if current_question:
                    evaluation = analyzer.evaluate_answer(current_question, response_text)
                    
                    # Store evaluation
                    st.session_state.question_evaluations.append({
                        "question": current_question,
                        "answer": response_text,
                        "evaluation": evaluation,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Update overall score
                    current_score = st.session_state.get("overall_score", 0)
                    num_questions = len(st.session_state.question_evaluations)
                    new_overall = (current_score * (num_questions - 1) + evaluation.get("overall", 5)) / num_questions
                    st.session_state.overall_score = new_overall
                    
                    # Move to next question or end interview
                    if st.session_state.current_question_index < st.session_state.total_questions_to_ask:
                        st.session_state.current_question_index += 1
                        
                        # Generate adaptive follow-up question if we're running out
                        if len(st.session_state.questions) <= st.session_state.current_question_index:
                            try:
                                skill_category = st.session_state.candidate_profile.get("primary_skill", "backend")
                                experience_level = st.session_state.candidate_profile.get("experience_level", "mid")
                                
                                # Generate adaptive follow-up
                                last_response = st.session_state.question_evaluations[-1]
                                followup_question = question_generator.generate_adaptive_followup(
                                    previous_question=last_response["question"],
                                    candidate_answer=last_response["answer"],
                                    skill_category=skill_category,
                                    difficulty_level=min(5, st.session_state.current_question_index + 1)
                                )
                                
                                if followup_question and followup_question not in st.session_state.questions:
                                    st.session_state.questions.append(followup_question)
                            except Exception as e:
                                st.warning(f"Could not generate adaptive follow-up: {e}")
                    else:
                        st.session_state.interview_completed = True
                        st.session_state.interview_active = False
                        
                        # Calculate final scores
                        if st.session_state.question_evaluations:
                            scores = [e["evaluation"]["overall"] for e in st.session_state.question_evaluations]
                            st.session_state.final_score = sum(scores) / len(scores)
                        
                        try:
                            report_path = save_interview_report()
                            if report_path:
                                st.success("✅ Interview completed and report saved!")
                            else:
                                st.warning("⚠️ Interview completed but report not saved.")
                        except Exception as e:
                            st.error(f"❌ Error saving report: {e}")
                    
                    # MODIFIED: Remove score from feedback
                    score = evaluation.get("overall", 5)
                    feedback_icon = "✅" if score >= 7 else "⚠️" if score >= 5 else "❌"
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"{feedback_icon} Answer received and analyzed.",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                
                else:
                    # No question available
                    st.error("No question available. Ending interview.")
                    st.session_state.interview_completed = True
                    st.session_state.interview_active = False
    
    except Exception as e:
        st.error(f"Error analyzing response: {e}")
        st.session_state.messages.append({
            "role": "system",
            "content": f"❌ Error analyzing response. Please continue.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    # Clear the current response for next question
    st.session_state.current_response = ""
    
    # Force rerun to update UI
    st.rerun()

def show_interview_in_progress():
    """Display interview interface when interview is active"""
    
    st.markdown("""
    <div class='main-header'>
        <h1>Interview in Progress</h1>
        <p>Complete the technical interview questions below</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Question display
    if not st.session_state.get("introduction_analyzed", False):
        current_prompt = "Please introduce yourself, including your experience, skills, and relevant projects."
    else:
        current_question = get_next_question()
        if current_question:
            current_prompt = current_question
        else:
            current_prompt = "All questions completed. Thank you!"
    
    st.info(f"**Current Question:** {current_prompt}")
    
    # Response input
    response = st.text_area(
        "Your Response:",
        value=st.session_state.get("current_response", ""),
        key=f"response_input_{st.session_state.current_question_index}",
        height=180,
        placeholder="Type your detailed response here...",
        help="Provide a comprehensive answer with examples where possible"
    )
    
    # Update session state with current response
    st.session_state.current_response = response
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📤 Submit Response", type="primary", use_container_width=True, key=f"submit_response_{st.session_state.current_question_index}"):
            if response and response.strip():
                # Process the response
                process_response(response.strip())
            else:
                st.warning("Please enter a response before submitting.")
    
    # Display progress
    st.markdown("---")
    total_questions = st.session_state.total_questions_to_ask
    
    # Display adaptive questions info if available
    if st.session_state.introduction_analyzed and st.session_state.questions:
        with st.expander("📋 Interview Questions", expanded=False):
            for i, question in enumerate(st.session_state.questions):
                status = "✅" if i < st.session_state.current_question_index - 1 else "⏳" if i == st.session_state.current_question_index - 1 else "🔲"
                st.markdown(f"{status} **Q{i+1}:** {question}")
    
    # Display chat history
    st.markdown("### 💬 Conversation History")
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.get("messages", []):
            if msg["role"] == "candidate":
                with st.chat_message("user"):
                    st.markdown(f"**You** ({msg.get('timestamp', '')}):")
                    st.write(msg["content"])
            elif msg["role"] == "system":
                with st.chat_message("assistant"):
                    st.markdown(f"**System** ({msg.get('timestamp', '')}):")
                    st.write(msg["content"])

def show_welcome_screen():
    """Display welcome screen"""
    
    # Welcome content in a centered layout
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #64B5F6;'>Welcome to Your Technical Interview</h2>
            <p style='color: #B0BEC5; font-size: 1.1rem;'>
                Prepare to showcase your skills through an AI-powered adaptive interview process
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # How it works section
        st.markdown("### 📋 How it works:")
        
        steps = [
            (" Introduction", "Share your background, skills, and relevant experience"),
            (" AI Analysis", "Our system evaluates your technical profile"),
            (" Adaptive Questions", "Answer AI-generated tailored technical questions"),
            (" Dynamic Follow-ups", "Questions adapt based on your previous answers"),
            (" Comprehensive Review", "HR team receives detailed analysis")
        ]
        
        for icon, description in steps:
            st.markdown(f"""
            <div style='background: #1e1e2e; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #64B5F6;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='font-size: 1.5rem; width: 28%;'>{icon}</span>
                    <div>
                        <strong style='color: #E2E8F0;'>{' '.join(icon.split()[1:])}</strong><br>
                        <span style='color: #CBD5E0;'>{description}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # AI-Powered note
        st.markdown("""
        <div class='custom-success'>
            <h4 style='color: #4CAF50; margin-top: 0;'>🤖 AI-Powered Interview</h4>
            <p>This interview uses AI to generate adaptive questions based on your responses, 
            providing a more personalized and relevant assessment of your skills.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Interview", type="primary", use_container_width=True, key="start_interview_btn"):
                st.session_state.interview_started = True
                st.session_state.interview_active = True
                st.rerun()

def show_termination_screen():
    """Display termination screen"""
    
    st.markdown("""
    <div class='main-header' style='background: linear-gradient(135deg, #2c003e 0%, #4a148c 100%);'>
        <h1>⛔ Interview Terminated</h1>
        <p>The interview session has been concluded</p>
    </div>
    """, unsafe_allow_html=True)
    
    reason = st.session_state.termination_reason
    reasons_map = {
        "misconduct": "Inappropriate behavior detected",
        "candidate_request": "Candidate requested to end the interview",
        "poor_response": "Response quality too low to continue",
        "insufficient_response": "Response was too brief or unclear"
    }
    
    st.markdown(f"""
    <div class='custom-warning'>
        <h4 style='color: #FFC107; margin-top: 0;'>Termination Reason</h4>
        <p style='font-size: 1.1rem;'>{reasons_map.get(reason, reason)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.termination_log:
        with st.expander("📋 Termination Details", expanded=True):
            for log in st.session_state.termination_log:
                st.markdown(f"""
                <div style='background: #1e1e2e; padding: 1rem; border-radius: 6px; margin: 0.5rem 0; border: 1px solid #2d3748;'>
                    <strong>Time:</strong> {log.get('time', 'N/A')}<br>
                    <strong>Reason:</strong> {log.get('reason', 'N/A')}<br>
                    <strong>Response:</strong> {log.get('response', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")

def show_report():
    """Display interview completion screen"""
    
    # Save report if not already saved
    if not st.session_state.get('report_saved', False):
        try:
            report_path = save_interview_report()
            st.session_state.report_saved = True
        except Exception as e:
            st.error(f"Error saving report: {e}")
    
    st.markdown("""
    <div class='main-header' style='background: linear-gradient(135deg, #00695c 0%, #004d40 100%);'>
        <h1>Interview Completed Successfully!</h1>
        <p>Thank you for participating</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Success message
    st.markdown("""
    <div class='custom-success'>
        <h3 style='color: #4CAF50; margin-top: 0;'>✅ Interview Submitted</h3>
        <p style='font-size: 1.1rem;'>
            Your interview responses have been successfully submitted and analyzed.
            The AI-powered adaptive questions provided a personalized assessment of your skills.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # What happens next
    st.markdown("### What happens next:")
    
    next_steps = [
        ("📄 Response Analysis", "Your answers are being processed by our AI system"),
        ("🤖  AI Evaluation", " Adaptive question performance analyzed for skill assessment"),
        ("👥 HR Review", "The HR team will review your interview results"),
        ("📧 Contact", "You will be contacted regarding next steps within 3-5 business days")
    ]
    
    for step, description in next_steps:
        st.markdown(f"""
        <div style='background: #1e1e2e; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #2196F3;'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <span style='font-size: 1.5rem;'>{step.split()[0]}</span>
                <div>
                    <strong style='color: #E2E8F0; font-size: 1.1rem;'>{' '.join(step.split()[1:])}</strong><br>
                    <span style='color: #CBD5E0;'>{description}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Simple stats
    st.markdown("### Summary")
    st.metric("Questions Answered", len(st.session_state.question_evaluations))
    st.markdown("---")

def save_interview_report():
    """Save interview report using ReportManager"""
    try:
        # VALIDATION: Check if we have enough data to save
        if (len(st.session_state.question_evaluations) == 0 or 
            not st.session_state.candidate_profile or
            st.session_state.overall_score == 0):
            
            print(f"⚠️ Insufficient data for report:")
            print(f"   - Questions answered: {len(st.session_state.question_evaluations)}")
            print(f"   - Candidate profile exists: {bool(st.session_state.candidate_profile)}")
            print(f"   - Overall score: {st.session_state.overall_score}")
            return None
        
        # Ensure directory exists
        os.makedirs("interview_reports", exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"interview_reports/candidate_report_{timestamp}.json"
        txt_filename = f"interview_reports/candidate_report_{timestamp}.txt"
        
        # Prepare report data WITH ALL REQUIRED FIELDS
        report_data = {
            "report_id": f"INT{timestamp}",
            "timestamp": datetime.now().isoformat(),
            "display_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "candidate_profile": st.session_state.candidate_profile,
            "question_evaluations": st.session_state.question_evaluations,
            "questions_asked": st.session_state.questions[:len(st.session_state.question_evaluations)],
            "overall_score": st.session_state.overall_score,
            "final_score": st.session_state.final_score,
            "introduction_analyzed": st.session_state.introduction_analyzed,
            "total_questions_answered": len(st.session_state.question_evaluations),
            "total_questions": st.session_state.total_questions_to_ask,
            "messages": st.session_state.messages[:5] if st.session_state.messages else [],
            "adaptive_interview": True,
            # Add tab switching info if applicable
            "tab_switch_count": st.session_state.get('tab_switch_count', 0),
            "terminated_by_tab_switch": st.session_state.get('auto_terminate_tab_switch', False)
        }
        
        # DEBUG: Print what we're saving
        print(f"📊 Saving report with data:")
        print(f"   - Report ID: {report_data['report_id']}")
        print(f"   - Questions: {len(report_data['question_evaluations'])}")
        print(f"   - Score: {report_data['overall_score']}")
        print(f"   - JSON file: {json_filename}")
        
        # Save JSON report
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Verify file was written
        if os.path.exists(json_filename) and os.path.getsize(json_filename) > 0:
            print(f"✅ JSON report saved successfully: {os.path.getsize(json_filename)} bytes")
        else:
            print(f"❌ JSON file creation failed: {json_filename}")
            return None
        
        # Save text report
        try:
            text_report = generate_readable_report(report_data)
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(text_report)
            
            if os.path.exists(txt_filename) and os.path.getsize(txt_filename) > 0:
                print(f"✅ Text report saved successfully: {os.path.getsize(txt_filename)} bytes")
            else:
                print(f"⚠️ Text file creation had issues: {txt_filename}")
                
        except Exception as text_error:
            print(f"⚠️ Text report error (continuing with JSON): {text_error}")
        
        return json_filename
        
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        import traceback
        traceback.print_exc()
        return None
    
def generate_readable_report(report_data: dict) -> str:
    """Generate a human-readable text report from report data"""
    report = "=" * 60 + "\n"
    report += "VIRTUAL HR INTERVIEWER - CANDIDATE REPORT\n"
    report += "=" * 60 + "\n\n"
    
    # Basic info with safe access
    report += f"Report Generated: {report_data.get('timestamp', 'N/A')}\n"
    report += f"Interview Type: {'AI Adaptive' if report_data.get('adaptive_interview', False) else 'Standard'}\n"
    
    # Use get() with default values
    total_questions = report_data.get('total_questions_answered', 
                                    len(report_data.get('question_evaluations', [])))
    report += f"Total Questions Answered: {total_questions}\n"
    
    report += f"Overall Score: {report_data.get('overall_score', 0):.2f}/10\n"
    report += f"Final Score: {report_data.get('final_score', 0):.2f}/10\n\n"
    
    # Candidate Profile with safe access
    profile = report_data.get('candidate_profile', {})
    report += "CANDIDATE PROFILE\n"
    report += "-" * 40 + "\n"
    report += f"Experience Level: {profile.get('experience_level', 'N/A')}\n"
    report += f"Primary Skill: {profile.get('primary_skill', 'N/A')}\n"
    report += f"Confidence: {profile.get('confidence', 'N/A')}\n"
    report += f"Communication: {profile.get('communication', 'N/A')}\n"
    report += f"Introduction Score: {profile.get('intro_score', 'N/A')}/10\n"
    
    skills = profile.get("skills", [])
    if skills:
        report += f"Skills Detected: {', '.join(skills)}\n"
    report += "\n"
    
    # Question-by-Question Analysis
    report += "QUESTION ANALYSIS\n"
    report += "-" * 40 + "\n"
    
    evaluations = report_data.get('question_evaluations', [])
    questions_asked = report_data.get('questions_asked', [])
    
    for i, eval_data in enumerate(evaluations):
        evaluation = eval_data.get('evaluation', {})
        score = evaluation.get("overall", 0)
        
        # Get the actual question asked
        question = eval_data.get('question', 'N/A')
        if i < len(questions_asked):
            question = questions_asked[i]
        
        report += f"\nQuestion {i+1}: {question}\n"
        report += f"Score: {score}/10\n"
        
        # Category scores with safe access
        categories = [
            ("Technical Accuracy", "technical_accuracy"),
            ("Completeness", "completeness"),
            ("Clarity", "clarity"),
            ("Depth", "depth"),
            ("Practicality", "practicality")
        ]
        
        for label, key in categories:
            cat_score = evaluation.get(key, 0)
            report += f"  {label}: {cat_score}/10\n"
        
        if evaluation.get("strengths"):
            report += "  Strengths:\n"
            for strength in evaluation["strengths"]:
                report += f"    - {strength}\n"
        
        if evaluation.get("weaknesses"):
            report += "  Areas for Improvement:\n"
            for weakness in evaluation["weaknesses"]:
                report += f"    - {weakness}\n"
        
        report += "-" * 40 + "\n"
    
    # Summary Statistics
    report += "\nSUMMARY STATISTICS\n"
    report += "-" * 40 + "\n"
    
    scores = [e.get("evaluation", {}).get("overall", 0) for e in evaluations]
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        report += f"Average Score: {avg_score:.2f}/10\n"
        report += f"Highest Score: {max_score}/10\n"
        report += f"Lowest Score: {min_score}/10\n"
        report += f"Score Range: {max_score - min_score:.2f}\n"
    
    # Recommendation
    report += "\nRECOMMENDATION\n"
    report += "-" * 40 + "\n"
    
    overall = report_data.get('overall_score', 0)
    if overall >= 7:
        report += "✅ STRONGLY RECOMMEND - Proceed to Next Round\n"
        report += "Candidate demonstrates strong technical understanding and communication skills.\n"
    elif overall >= 5:
        report += "⚠️ CONDITIONAL RECOMMEND - Consider with Feedback\n"
        report += "Candidate shows potential but needs improvement in some areas.\n"
    else:
        report += "❌ NOT RECOMMENDED - Requires Significant Improvement\n"
        report += "Candidate needs to strengthen technical fundamentals and communication.\n"
    
    report += "\n" + "=" * 60 + "\n"
    report += "END OF REPORT\n"
    report += "=" * 60
    
    return report

def main():
    """Main application function"""
    
    # ===== IMMEDIATE TAB SWITCHING TERMINATION CHECK =====
    # This MUST be at the VERY BEGINNING
    if st.session_state.get('auto_terminate_tab_switch', False) and st.session_state.interview_active:
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = "misconduct"
        st.session_state.interview_active = False
        
        # Add to termination log
        if "termination_log" not in st.session_state:
            st.session_state.termination_log = []
        st.session_state.termination_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "reason": "misconduct",
            "details": f"Tab switching detected ({st.session_state.get('tab_switch_count', 0)} times)"
        })
        
        st.rerun()
        return  # Stop execution - termination screen will show
    
    # ===== TAB SWITCH DETECTION JAVASCRIPT =====
    if st.session_state.interview_active and not st.session_state.interview_terminated:
        
        js_code = f"""
        <script>
        let tabCount = {st.session_state.get('tab_switch_count', 0)};
        let warned = {str(st.session_state.get('tab_warning_given', False)).lower()};
        
        document.addEventListener('visibilitychange', function() {{
            if (document.hidden) {{
                tabCount++;
                console.log('Tab switch #' + tabCount);
                
                if (tabCount === 1 && !warned) {{
                    // First switch - show warning
                    warned = true;
                    alert('⚠️ WARNING: Tab switching detected. Next switch will terminate the interview immediately!');
                    
                    // Update URL to communicate with Streamlit
                    const url = new URL(window.location);
                    url.searchParams.set('tab_warning', 'true');
                    url.searchParams.set('tab_count', tabCount);
                    window.history.replaceState({{}}, '', url);
                    
                    // Force page reload to update session state
                    setTimeout(() => window.location.reload(), 500);
                    
                }} else if (tabCount >= 2) {{
                    // SECOND SWITCH - TERMINATE IMMEDIATELY
                    alert('❌ INTERVIEW TERMINATED: Multiple tab switches detected. This violates interview rules.');
                    
                    // Set termination flag in URL
                    const url = new URL(window.location);
                    url.searchParams.set('terminate_tab', 'true');
                    url.searchParams.set('tab_count', tabCount);
                    window.history.replaceState({{}}, '', url);
                    
                    // Auto-fill termination message
                    setTimeout(() => {{
                        const textareas = document.querySelectorAll('textarea');
                        for (let textarea of textareas) {{
                            if (textarea.placeholder && textarea.placeholder.includes('Type your detailed response')) {{
                                textarea.value = 'session terminated due to tab switching';
                                const inputEvent = new Event('input', {{ bubbles: true }});
                                textarea.dispatchEvent(inputEvent);
                                
                                // Auto-click submit button
                                const buttons = document.querySelectorAll('button');
                                for (let button of buttons) {{
                                    if (button.innerText && (
                                        button.innerText.includes('Submit Response') || 
                                        button.innerText.includes('📤 Submit Response')
                                    )) {{
                                        setTimeout(() => button.click(), 300);
                                        break;
                                    }}
                                }}
                                break;
                            }}
                        }}
                    }}, 300);
                    
                    // Force immediate reload
                    setTimeout(() => window.location.reload(), 1000);
                }}
            }}
        }});
        
        // Prevent keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && ['t', 'n', 'T', 'N'].includes(e.key)) {{
                e.preventDefault();
                tabCount++;
                
                if (tabCount >= 2) {{
                    alert('❌ INTERVIEW TERMINATED: Attempted to open new tab/window.');
                    const url = new URL(window.location);
                    url.searchParams.set('terminate_tab', 'true');
                    url.searchParams.set('tab_count', tabCount);
                    window.history.replaceState({{}}, '', url);
                    setTimeout(() => window.location.reload(), 500);
                }}
            }}
        }});
        </script>
        """
        
        st.components.v1.html(js_code, height=0)
    
    # ===== CHECK URL PARAMETERS =====
    query_params = st.query_params
    
    # Check for tab warning
    if 'tab_warning' in query_params and query_params['tab_warning'][0] == 'true':
        st.session_state.tab_warning_given = True
        if 'tab_count' in query_params:
            st.session_state.tab_switch_count = int(query_params['tab_count'][0])
        
        # Clear URL parameters
        st.query_params.clear()
        st.rerun()
    
    # Check for termination due to tab switching
    if 'terminate_tab' in query_params and query_params['terminate_tab'][0] == 'true':
        st.session_state.auto_terminate_tab_switch = True
        if 'tab_count' in query_params:
            st.session_state.tab_switch_count = int(query_params['tab_count'][0])
        
        # Clear URL parameters
        st.query_params.clear()
        st.rerun()
    
    # ===== DIRECT TERMINATION CHECK =====
    if st.session_state.get('tab_switch_count', 0) >= 2 and st.session_state.interview_active:
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = "misconduct"
        st.session_state.interview_active = False
        st.session_state.auto_terminate_tab_switch = True
        
        st.rerun()
    
    # ===== SHOW WARNING IF APPLICABLE =====
    if st.session_state.tab_switch_count == 1 and not st.session_state.tab_warning_given:
        st.session_state.tab_warning_given = True
        st.error("⚠️ **WARNING:** Tab switching detected. Next switch will terminate the interview immediately!")
    
    # ===== HEADER =====
    st.markdown("""
    <div class='main-header'>
        <h1>Virtual HR</h1>
        <p>AI-Powered Adaptive Technical & Behavioral Screening Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("### Interview Dashboard")
        st.markdown("---")
        
        if st.session_state.interview_active:
            # Progress
            total_questions = st.session_state.total_questions_to_ask
            progress = min(st.session_state.current_question_index / total_questions, 1.0)
            
            st.markdown("**Progress**")
            st.progress(progress)
            st.caption(f"Question {st.session_state.current_question_index}/{total_questions}")
            
            # Quick actions
            st.markdown("---")
            st.markdown("**Quick Actions**")
            
            if st.button("End Interview", type="secondary", use_container_width=True, key="end_interview_sidebar"):
                st.session_state.interview_completed = True
                st.session_state.interview_active = False
                st.rerun()

        elif st.session_state.interview_completed:
            st.markdown("### ✅ Interview Complete")
            st.markdown("Your interview has been successfully submitted.")
            st.markdown("---")
            if st.session_state.overall_score > 0:
                st.metric("Overall Score", f"{st.session_state.overall_score:.1f}/10")
        
        # About section
        st.markdown("---")
        st.markdown("### ℹ️ About This Tool")
        st.markdown("""
        <div style='background: #1e1e2e; padding: 1rem; border-radius: 8px;'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;'>
                <span>🤖</span><span>AI-Generated Questions</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;'>
                <span>🔄</span><span>Adaptive Follow-ups</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;'>
                <span>📊</span><span>Real-time Analysis</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span>📝</span><span>Detailed Reports</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== MAIN CONTENT ROUTING =====
    if not st.session_state.interview_started:
        show_welcome_screen()
    elif st.session_state.interview_terminated:
        show_termination_screen()
    elif st.session_state.interview_active:
        show_interview_in_progress()
    elif st.session_state.interview_completed:
        show_report()

if __name__ == "__main__":
    main()