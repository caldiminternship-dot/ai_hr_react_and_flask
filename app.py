import streamlit as st
import time
import os
from config import MODEL_NAME
from skill_mapper import map_skills_to_category
from datetime import datetime
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from response_analyzer import ResponseAnalyzer
from report_manager import ReportManager
from question_generator import QuestionGenerator
from resume_parser import parse_resume
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
        'technical_questions': [],
        'behavioral_question': None,
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
        'total_questions_to_ask': 5, # 4 Technical + 1 Behavioral (Excluding Intro/Resume)
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
    """
    Generate ONLY domain-specific technical questions.
    Behavioral questions must NOT be generated here.
    """
    try:
        profile = st.session_state.get("candidate_profile", {})
        if not profile:
            return []

        skill_category = profile.get("primary_skill", "backend")
        experience_level = profile.get("experience_level", "mid")

        # 🔒 Generate domain-locked technical questions
        technical_questions = question_generator.generate_initial_skill_questions(
            skill_category=skill_category,
            candidate_level=experience_level
        )

        # Fallback if AI fails
        if not technical_questions:
            technical_questions = [
                f"Explain a core concept related to {skill_category}.",
                f"Describe a real-world problem you solved using {skill_category}.",
                f"What challenges do you commonly face when working in {skill_category}?"
            ]

        # 🔒 STRICT: return ONLY technical questions
        # Leave room for behavioral question later
        max_technical = st.session_state.total_questions_to_ask - 1
        return technical_questions[:max_technical]

    except Exception as e:
        st.error(f"Error generating adaptive questions: {e}")

        # Safe technical-only fallback
        return [
            "Describe a challenging technical problem you solved recently.",
            "Explain how you debug issues in complex systems.",
            "How do you ensure code quality and reliability?",
            "Describe your approach to system design."
        ]

def get_next_question():
    if not st.session_state.questions_generated:
        return None

    idx = st.session_state.current_question_index

    if idx > 0 and (idx - 1) < len(st.session_state.questions):
        return st.session_state.questions[idx - 1]

    return None


def process_response(response_text):
    """Process the candidate's response and update interview state"""

    if not response_text or response_text.strip() == "":
        st.warning("Please enter a response before submitting.")
        return

    # --------------------------------------------------
    # TAB SWITCH TERMINATION
    # --------------------------------------------------
    if "session terminated due to tab switching" in response_text.lower():
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = "misconduct"
        st.session_state.interview_active = False

        st.session_state.termination_log = st.session_state.get("termination_log", [])
        st.session_state.termination_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "reason": "misconduct",
            "response": "Tab switching detected"
        })

        st.rerun()
        return

    # --------------------------------------------------
    # KEYWORD TERMINATION / ABUSIVE LANGUAGE CHECK
    # --------------------------------------------------
    should_terminate, reason = analyzer.check_for_termination(response_text)
    if should_terminate:
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = reason
        st.session_state.interview_active = False
        
        st.session_state.termination_log = st.session_state.get("termination_log", [])
        st.session_state.termination_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "reason": reason,
            "response": response_text
        })
        
        if reason == "misconduct":
            st.error("Session terminated due to inappropriate language.")
        elif reason == "candidate_request":
            st.warning("Interview terminated by candidate request.")
            
        st.rerun()
        return

    # --------------------------------------------------
    # SAVE CANDIDATE MESSAGE
    # --------------------------------------------------
    st.session_state.messages.append({
        "role": "candidate",
        "content": response_text,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # --------------------------------------------------
    # INTRODUCTION (Q1)
    # --------------------------------------------------
    if st.session_state.current_question_index == 0:
        with st.spinner("Analyzing your introduction..."):
            analysis = analyzer.analyze_introduction(response_text)

        detected_skills = analysis.get("skills", [])

        # 🔒 LOCK SKILL USING CONFIG
        locked_skill = map_skills_to_category(detected_skills)

        st.session_state.candidate_profile = {
            "skills": detected_skills,
            "experience_level": analysis.get("experience", "mid"),
            "primary_skill": locked_skill,
            "confidence": analysis.get("confidence", "medium"),
            "communication": analysis.get("communication", "adequate"),
            "intro_score": analysis.get("intro_score", 5),
        }

        # --------------------------------------------------
        # 🔐 GENERATE QUESTIONS ONCE (TECHNICAL FIRST)
        # --------------------------------------------------
        if not st.session_state.get("questions_generated", False):

            technical_questions = question_generator.generate_initial_skill_questions(
                skill_category=locked_skill,
                candidate_level=st.session_state.candidate_profile["experience_level"]
            )

            # Safety fallback
            # Ensure we have enough technical questions
            num_technical_needed = st.session_state.total_questions_to_ask - 1
            
            if not technical_questions or len(technical_questions) < num_technical_needed:
                print(f"⚠️ Generated {len(technical_questions) if technical_questions else 0} questions, need {num_technical_needed}. Adding fallbacks.")
                fallbacks = [
                    f"Explain a core concept in {locked_skill}.",
                    f"Describe a real-world problem you solved using {locked_skill}.",
                    f"What challenges do you face when working in {locked_skill}?",
                    f"How do you handle performance optimization in {locked_skill}?",
                    f"Describe a time you had to debug a complex {locked_skill} issue.",
                    f"What are the key differences between versions of {locked_skill}?"
                ]
                
                if not technical_questions:
                    technical_questions = []
                    
                for q in fallbacks:
                    if q not in technical_questions:
                        technical_questions.append(q)
                    if len(technical_questions) >= num_technical_needed:
                        break

            # Behavioral LAST
            behavioral_question = question_generator.generate_behavioral_question_ai(
                candidate_background=st.session_state.candidate_profile
            )

            st.session_state.questions = (
                technical_questions[: st.session_state.total_questions_to_ask - 1]
                + [behavioral_question]
            )

            st.session_state.questions_generated = True

        st.session_state.introduction_analyzed = True
        st.session_state.current_question_index = 1

        st.session_state.messages.append({
            "role": "system",
            "content": f"🔒 Skill locked: **{locked_skill.upper()}**. Interview questions fixed.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        st.session_state.current_response = ""
        st.rerun()
        return

    # --------------------------------------------------
    # TECHNICAL / BEHAVIORAL QUESTIONS
    # --------------------------------------------------
    current_idx = st.session_state.current_question_index - 1

    if current_idx < len(st.session_state.questions):
        current_question = st.session_state.questions[current_idx]
    else:
        st.error("No more questions available.")
        st.session_state.interview_completed = True
        st.session_state.interview_active = False
        st.rerun()
        return

    evaluation = analyzer.evaluate_answer(current_question, response_text)

    st.session_state.question_evaluations.append({
        "question": current_question,
        "answer": response_text,
        "evaluation": evaluation,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Update score
    scores = [e["evaluation"]["overall"] for e in st.session_state.question_evaluations]
    st.session_state.overall_score = sum(scores) / len(scores)

    # Move forward or finish
    if st.session_state.current_question_index < st.session_state.total_questions_to_ask:
        st.session_state.current_question_index += 1
    else:
        st.session_state.interview_completed = True
        st.session_state.interview_active = False
        save_interview_report()

    st.session_state.messages.append({
        "role": "system",
        "content": "✅ Answer recorded.",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    st.session_state.current_response = ""
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
        st.markdown("### 📄 Upload Your Resume to Begin")
        uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx', 'doc'])
        
        if uploaded_file is not None:
            if st.button("Start Interview"):
                with st.spinner("Analyzing your resume..."):
                    # Parse resume
                    resume_text = parse_resume(uploaded_file)
                    
                    if not resume_text.strip():
                        st.error("Could not extract text from resume. Please try a different file.")
                        return

                    # Analyze resume as introduction
                    analysis = analyzer.analyze_introduction(resume_text)

                detected_skills = analysis.get("skills", [])

                # 🔒 LOCK SKILL USING CONFIG
                locked_skill = map_skills_to_category(detected_skills)

                st.session_state.candidate_profile = {
                    "skills": detected_skills,
                    "experience_level": analysis.get("experience", "mid"),
                    "primary_skill": locked_skill,
                    "confidence": analysis.get("confidence", "medium"),
                    "communication": analysis.get("communication", "adequate"),
                    "intro_score": analysis.get("intro_score", 5),
                }

                # --------------------------------------------------
                # 🔐 GENERATE QUESTIONS ONCE (TECHNICAL FIRST)
                # --------------------------------------------------
                if not st.session_state.get("questions_generated", False):
                    technical_questions = question_generator.generate_initial_skill_questions(
                        skill_category=locked_skill,
                        candidate_level=st.session_state.candidate_profile["experience_level"]
                    )

                    # Safety fallback
                    # Ensure we have enough technical questions
                    num_technical_needed = st.session_state.total_questions_to_ask - 1

                    if not technical_questions or len(technical_questions) < num_technical_needed:
                        fallbacks = [
                            f"Explain a core concept in {locked_skill}.",
                            f"Describe a real-world problem you solved using {locked_skill}.",
                            f"What challenges do you face when working in {locked_skill}?",
                            f"How do you handle performance optimization in {locked_skill}?",
                            f"Describe a time you had to debug a complex {locked_skill} issue.",
                            f"What are the key differences between versions of {locked_skill}?"
                        ]
                        
                        if not technical_questions:
                            technical_questions = []
                            
                        for q in fallbacks:
                            if q not in technical_questions:
                                technical_questions.append(q)
                            if len(technical_questions) >= num_technical_needed:
                                break

                    # Behavioral LAST
                    behavioral_question = question_generator.generate_behavioral_question_ai(
                        candidate_background=st.session_state.candidate_profile
                    )

                    st.session_state.questions = (
                        technical_questions[: st.session_state.total_questions_to_ask - 1]
                        + [behavioral_question]
                    )

                    st.session_state.questions_generated = True

                st.session_state.introduction_analyzed = True
                st.session_state.current_question_index = 1
                
                # Log system message
                st.session_state.messages.append({
                    "role": "system",
                    "content": f"📄 Resume analyzed. Skills detected: {', '.join(detected_skills) if detected_skills else 'None'}. Locking interview to: **{locked_skill.upper()}**.",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

                st.rerun()

    else:
        current_question = get_next_question()
        if current_question:
            current_prompt = current_question
        else:
            current_prompt = None # Handle completion separately
            
        # Display Current Question
        if current_prompt:
            st.markdown(f"""
            <div style="
                background: rgba(30, 41, 59, 0.7);
                border-left: 5px solid #6366f1;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-size: 1.1em;
                font-weight: 500;
            ">
                {current_prompt}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🎉 All questions completed! Please click 'End Interview' in the sidebar.")
        
        # Response input
        response = st.text_area(
            "Your Response:",
            value=st.session_state.get("current_response", ""),
            key=f"response_input_{st.session_state.current_question_index}",
            height=180,
            placeholder="Type your detailed response here...",
            help="Provide a comprehensive answer with examples where possible"
        )
        # 🔒 DISPLAY LOCKED SKILL AFTER INTRO QUESTION
        if st.session_state.introduction_analyzed and st.session_state.candidate_profile:
            locked_skill = st.session_state.candidate_profile.get("primary_skill", "").upper()
            detected_skills = st.session_state.candidate_profile.get("skills", [])

            st.markdown(
                f"""
                <div style="
                    margin-top: 10px;
                    padding: 12px 16px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.1));
                    border-left: 4px solid #10b981;
                    color: #d1fae5;
                    font-size: 0.95rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span>🔒 <strong>Skill Locked:</strong> {locked_skill}</span>
                    <span style="color:#a7f3d0; font-size: 0.85rem;">
                        Detected Keys: {", ".join(detected_skills[:5])}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        
        # Update session state with current response
        st.session_state.current_response = response
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if current_prompt:
                if st.button("📤 Submit Response", type="primary", use_container_width=True, key=f"submit_response_{st.session_state.current_question_index}"):
                    if response and response.strip():
                        # Process the response
                        process_response(response.strip())
                    else:
                        st.warning("Please enter a response before submitting.")
            else:
                # End Interview Button when completed
                if st.button("🏁 End Interview", type="primary", use_container_width=True, key="end_interview_main"):
                    st.session_state.interview_completed = True
                st.session_state.interview_active = False
                st.rerun()
    
    # Display progress
    st.markdown("---")
    total_questions = st.session_state.total_questions_to_ask
    
    # Display adaptive questions info if available
    if st.session_state.introduction_analyzed and st.session_state.questions:
        for i, question in enumerate(st.session_state.questions):
            # Q1 is actually index 0 in the list but displayed as Q1
            # "Introduction" was step 0 (before this list existed)
            
            # Logic: 
            # If current_question_index is 1, we are on the first technical question (idx 0 of questions list)
            
            display_idx = i + 1 
            is_past = display_idx < st.session_state.current_question_index 
            is_current = display_idx == st.session_state.current_question_index
            
            if is_past:
                pass # Hide past questions as requested
            elif is_current and not st.session_state.interview_completed:
                st.markdown(f"⏳ **Q{display_idx}:** (Current Question)")
            # else: Future questions are NOT displayed
    
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

def save_interview_report():
    """Save the interview report using ReportManager"""
    try:
        report_path = report_manager.save_interview_report(st.session_state)
        st.session_state.report_path = report_path
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")

def show_report():
    """Display the interview completion screen"""
    
    # Ensure report is saved once
    if not st.session_state.get('report_saved', False):
        save_interview_report()
        st.session_state.report_saved = True
        
    st.markdown("""
    <div class='main-header'>
        <h1>Interview Completed</h1>
        <p>Thank you for completing the technical interview.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ Your responses have been recorded and analyzed.")
    
    # Display Score
    score = st.session_state.get('overall_score', 0)

    st.info("ℹ️ A detailed report has been generated and sent to the hiring team. You may close this window.")
    
    if st.session_state.get('report_path'):
        st.caption(f"Report ID: {os.path.basename(st.session_state.report_path).replace('.json', '')}")


def check_and_process_termination():
    """Centralized logic to handle termination signals"""
    # 1. Check URL parameters first (Signal from JS)
    query_params = st.query_params
    print(f"🔍 DEBUG: query_params: {query_params}")
    
    # Helper to clean param value (handle list vs string)
    def get_param(key):
        if key not in query_params:
            return None
        val = query_params[key]
        if isinstance(val, list):
            return val[0]
        return val

    terminate_tab = get_param('terminate_tab')
    
    if terminate_tab == 'true':
        print("🛑 DEBUG: URL terminate_tab detected!")
        st.session_state.auto_terminate_tab_switch = True
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = "misconduct"
        st.session_state.interview_active = False
        
        tab_count_val = get_param('tab_count')
        if tab_count_val:
            try:
                st.session_state.tab_switch_count = int(tab_count_val)
            except:
                pass
                
        # Clear params and return True to signal termination handling
        st.query_params.clear()
        return True

    # 2. Check Session State flags
    print(f"🔍 DEBUG: State Check - auto_term: {st.session_state.get('auto_terminate_tab_switch')}, switch_count: {st.session_state.get('tab_switch_count')}")
    if st.session_state.get('auto_terminate_tab_switch', False) or \
       (st.session_state.get('tab_switch_count', 0) >= 2 and st.session_state.interview_active):
       
        print("🛑 DEBUG: State termination flag detected!")
        # Update values if needed
        st.session_state.interview_terminated = True
        st.session_state.termination_reason = "misconduct"
        st.session_state.interview_active = False
        st.session_state.auto_terminate_tab_switch = True
        return False # No reload needed for state check, just proceed to show termination screen
        
    return False

def main():
    """Main application function"""
    
    # ===== IMMEDIATE TAB SWITCHING TERMINATION CHECK =====
    # This MUST be at the VERY BEGINNING
    should_rerun = check_and_process_termination()
    print(f"🔍 DEBUG: main() - should_rerun: {should_rerun}, terminated: {st.session_state.get('interview_terminated')}")
    
    if st.session_state.get('interview_terminated', False):
        print("💀 DEBUG: Rendering termination screen...")
        # Add log if needed
        if "termination_log" not in st.session_state:
            st.session_state.termination_log = []
            
        already_logged = any(log.get('reason') == 'misconduct' for log in st.session_state.termination_log)
        if not already_logged:
            st.session_state.termination_log.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "reason": "misconduct",
                "details": f"Tab switching detected ({st.session_state.get('tab_switch_count', 0)} times)"
            })
            
        if should_rerun:
            st.rerun()
            
        show_termination_screen()
        return
    
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
                    try {{
                        const targetWindow = window.parent || window;
                        const url = new URL(targetWindow.location);
                        url.searchParams.set('tab_warning', 'true');
                        url.searchParams.set('tab_count', tabCount);
                        targetWindow.history.replaceState({{}}, '', url);
                        
                        // Force page reload to update session state
                        setTimeout(() => targetWindow.location.reload(), 500);
                    }} catch(e) {{
                        console.error('Error updating parent URL:', e);
                        // Fallback attempt
                        window.location.reload();
                    }}
                    
                }} else if (tabCount >= 2) {{
                    // SECOND SWITCH - TERMINATE IMMEDIATELY
                    alert('❌ INTERVIEW TERMINATED: Multiple tab switches detected. This violates interview rules.');
                    
                    // Set termination flag in URL
                    try {{
                        const targetWindow = window.parent || window;
                        const url = new URL(targetWindow.location);
                        url.searchParams.set('terminate_tab', 'true');
                        url.searchParams.set('tab_count', tabCount);
                        targetWindow.history.replaceState({{}}, '', url);
                    }} catch(e) {{
                        console.error('Error updating parent URL:', e);
                    }}
                    
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
                    setTimeout(() => {{
                        try {{
                            (window.parent || window).location.reload();
                        }} catch(e) {{
                            window.location.reload();
                        }}
                    }}, 1000);
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
    
    # ===== CHECK URL PARAMETERS (WARNINGS ONLY) =====
    # Termination is handled by check_and_process_termination at top
    query_params = st.query_params
    
    # Check for tab warning
    tab_warning = query_params.get('tab_warning')
    if isinstance(tab_warning, list):
        tab_warning = tab_warning[0]
        
    if tab_warning == 'true':
        st.session_state.tab_warning_given = True
        
        tab_count_val = query_params.get('tab_count')
        if isinstance(tab_count_val, list):
            tab_count_val = tab_count_val[0]
            
        if tab_count_val:
            try:
                st.session_state.tab_switch_count = int(tab_count_val)
            except:
                pass
        
        # Clear URL parameters
        st.query_params.clear()
        st.rerun()

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
            # st.caption(f"Question {st.session_state.current_question_index}/{total_questions}")
            
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
            # if st.session_state.overall_score > 0:
            #     st.metric("Overall Score", f"{st.session_state.overall_score:.1f}/10")
        
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