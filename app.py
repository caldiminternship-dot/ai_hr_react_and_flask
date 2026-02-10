import streamlit as st
import time
import os
from config import MODEL_NAME, MAX_QUESTIONS
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
from auth import login_user, create_user
from models import init_db, SessionLocal

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

# Light Glassmorphism Theme (Candidate Portal)
# Enterprise Light Theme (Minimalist & Professional)
css_light = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* ===== DESIGN TOKENS ===== */
:root {
    --bg-main: #F1F5F9; /* Professional Light Gray Base */
    --panel-bg: #FFFFFF;
    --sidebar-bg: #FFFFFF;
    --primary: #1E3A8A; /* Navy Blue Accent */
    --text-main: #0F172A; 
    --text-muted: #64748B;
    --border: #E2E8F0;
    --radius-lg: 16px;
    --radius-sm: 8px;
}

/* ===== APP BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 25%, #E0E7FF 50%, #DDD6FE 75%, #EDE9FE 100%);
    color: var(--text-main);
    font-family: 'Plus Jakarta Sans', sans-serif;
    min-height: 100vh;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border-right: 1px solid var(--border);
    box-shadow: 2px 0 12px rgba(30, 58, 138, 0.08);
}

/* ===== MAIN CONTENT WRAPPER ===== */
.main > div {
    max-width: 900px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(30, 58, 138, 0.1);
}

/* ===== SECTION HEADERS ===== */
h1, h2, h3 {
    color: #1E3A8A; /* Navy Blue Headers */
    font-weight: 700;
}

/* ===== PRIMARY CONTENT CARD ===== */
div.block-container {
    background: transparent; /* Clean Slate */
}

/* ===== FILE UPLOADER (NARROWER) ===== */
[data-testid="stFileUploader"] {
    max-width: 500px !important;
    margin: 0 auto !important; /* Center it */
}

[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    border: 1px dashed #CBD5E1 !important;
    border-radius: 12px;
    padding: 1.5rem !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: all 0.2s;
}

[data-testid="stFileUploader"] section:hover {
    border-color: var(--primary) !important;
    background: #F8FAFC !important;
}

/* ===== BROWSE FILES BUTTON ===== */
[data-testid="stFileUploader"] button {
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    color: #1E3A8A; /* Navy Text */
    font-weight: 600;
}

/* ===== PRIMARY CTA ===== */
.stButton > button {
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    padding: 0.9rem 2rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    width: auto !important;
    min-width: 150px;
}

.stButton > button:hover {
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.3);
    transform: translateY(-1px);
}

/* ===== REMOVE STREAMLIT NOISE ===== */
div[data-testid="stToolbar"],
footer {
    display: none !important;
}

/* ===== VISUAL POLISH ===== */
.verified-badge {
    background: linear-gradient(135deg, #DEF7EC 0%, #E1EFFE 100%);
    color: #03543F;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid #BCF0DA;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    vertical-align: middle;
    margin-left: 12px;
}

.step-card {
    background: #FFFFFF;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 0.75rem 0;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #3B82F6; /* Default Blue Accent */
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 16px;
}

.step-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    border-left-color: #2563EB;
}


</style>
"""

# Professional Light Login Theme
css_login = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ===== GLOBAL VARIABLES (LOGIN) ===== */
    :root {
        --bg-color: #F8FAFC; 
        --card-bg: #FFFFFF;
        --text-heading: #0F172A;
        --text-body: #475569;
        
        --primary: #4F46E5; /* Indigo-600 */
        --primary-hover: #4338CA;
        
        --radius: 12px;
    }

    /* ===== BASE ===== */
    /* ===== BASE ===== */
    .stApp {
        background-color: #F8FAFC;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        background-size: 200% 200%;
        animation: gradient-animation 15s ease infinite;
        color: var(--text-body);
        font-family: 'Inter', sans-serif;
    }
    
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Overlay for lightness (since we want light theme but colorful) */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.85); /* Glass overlay */
        backdrop-filter: blur(100px);
        z-index: -1;
    }
    
    h1 {
        color: var(--text-heading) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* ===== NAVY BLUE TITLE ===== */
    .gradient-text {
        background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%); /* Navy Blue Gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
        font-weight: 800 !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }

    /* ===== LOGIN INPUTS ===== */
    .stTextInput > div > div > input {
        background-color: #F8FAFC;
        color: #0F172A; /* Dark Text */
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1e3a8a; /* Navy focus */
        background-color: #FFFFFF;
        box-shadow: 0 0 0 4px rgba(30, 58, 138, 0.1);
        outline: none;
    }

    /* ===== LOGIN CARD (ATTRACTIVE) ===== */
    /* Target the tab container specifically */
    .stTabs {
        background-color: rgba(255, 255, 255, 0.95); /* More solid for contrast */
        backdrop-filter: blur(25px);
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.15), /* Deep shadow */
            0 0 0 1px rgba(255, 255, 255, 1) inset; /* Inner highlight */
        border: 1px solid rgba(226, 232, 240, 0.6);
        max-width: 450px;
        margin: 0 auto;
    }
    
    label {
        color: #475569 !important;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
        letter-spacing: 0.01em;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%); /* Navy Blue Gradient */
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 0;
        width: 100%;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.3);
        letter-spacing: 0.02em;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #172554 0%, #0f172a 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 2rem;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #64748B;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #EFF6FF; /* Very light blue */
        color: #1e3a8a; /* Navy Blue Text */
    }
    
    .stTabs [aria-selected="false"]:hover {
        background-color: #F8FAFC;
        color: #475569;
    }
    
</style>
"""

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
        'total_questions_to_ask': MAX_QUESTIONS, # Technical + Behavioral (Excluding Intro/Resume)
        'questions_generated': False,
        # TAB SWITCHING DETECTION VARIABLES
        'tab_switch_count': 0,
        'tab_warning_given': False,
        'tab_switch_count': 0,
        'tab_warning_given': False,
        'auto_terminate_tab_switch': False,
        'user': None,
        'user_id': None,
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
                candidate_level=st.session_state.candidate_profile["experience_level"],
                specific_skills=detected_skills
            )
            
            st.session_state.questions = technical_questions
            st.session_state.questions_generated = True

        st.session_state.introduction_analyzed = True
        st.session_state.current_question_index = 1

        st.session_state.current_response = ""
        st.rerun()
        return

    # --------------------------------------------------
    # TECHNICAL / BEHAVIORAL QUESTIONS
    # --------------------------------------------------
    current_idx = st.session_state.current_question_index - 1

    if current_idx < len(st.session_state.questions):
        # 🔒 FORCE LAST QUESTION TO BE BEHAVIORAL
        # If this is the final slot allowed (based on limit), we grab the Behavioral Question
        # which is always kept at the end of the list.
        if current_idx == st.session_state.total_questions_to_ask - 1:
            current_question = st.session_state.questions[-1]
        else:
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

    # --- STRICT LIMIT CHECK ---
    # Check if we have reached the limit of questions asked (Main + Follow-up)
    # We use the length of 'question_evaluations' as the source of truth for how many questions have been answered.
    if len(st.session_state.question_evaluations) >= st.session_state.total_questions_to_ask:
        st.session_state.interview_completed = True
        st.session_state.interview_active = False
        save_interview_report()
        st.rerun()
        return

    # --- Proceed to next question ---
    # --- Proceed to next question ---
    st.session_state.current_question_index += 1

    # --- DYNAMIC FOLLOW-UP LOGIC ---
    # Apply only during Section 2 (the middle 10 questions: roughly indices 5-14)
    # Target Mix:
    # Junior: 2 Follow-ups (Indices ~5-14)
    # Mid: 5 Follow-ups
    # Senior: 8 Follow-ups
    
    current_idx = st.session_state.current_question_index
    # Only trigger if within the Technical Section (before Behavioral at 15)
    # And specifically targeting the "Mixed" section (starts around Q6 i.e. index 5)
    is_mixed_section = 5 <= current_idx < 15
    
    c_level = st.session_state.candidate_profile.get("experience_level", "mid").lower()
    if "junior" in c_level or "beginner" in c_level:
        target_followups = 2
    elif "senior" in c_level or "expert" in c_level:
        target_followups = 8
    else:
        target_followups = 5
        
    current_followups = st.session_state.get("followup_count", 0)
    
    if is_mixed_section and current_followups < target_followups:
        try:
            # Generate the follow-up
            followup = question_generator.generate_followup_question(
                current_question,
                response_text,
                st.session_state.candidate_profile.get("primary_skill")
            )
            
            if followup:
                # Insert at next position (current_idx is already incremented, so insert AT current_idx)
                # This pushes existing questions down.
                st.session_state.questions.insert(current_idx, f"Follow-up: {followup}")
                
                # To maintain COUNT (20), remove a future question from Section 2.
                # The safest one to remove is the LAST generic technical question.
                # Index of last technical generic question is roughly 15 (before Behavioral starts)
                # But since we inserted one, the list grew by 1.
                # Behavioral started at 15, now at 16.
                # So we want to remove index 15 (the last technical question).
                
                # Verify we are popping a technical question, not a behavioral one.
                # How? We assume the generator put 5 behavioral at end during init.
                # The list has grown by 1 (inserted at current_idx).
                # New length is 21. Last 5 are Behavioral (indices 16,17,18,19,20).
                # The Technical Section (Section 2) ends at index 15.
                
                pop_target = len(st.session_state.questions) - 6
                
                # Ensure we don't pop the one we just inserted (current_idx) or anything weird
                if pop_target > current_idx:
                    removed = st.session_state.questions.pop(pop_target)
                    print(f"Removed '{removed}' to maintain 20 questions.")
                    
                    st.session_state.followup_count = current_followups + 1
                    
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"🔍 Follow-up question added: {followup}",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
        except Exception as e:
            print(f"Dynamic follow-up error: {e}") 

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
    <div class='main-header' style='
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
    '>
        <h1 style='margin-bottom: 0.5rem;'>Interview in Progress</h1>
        <p style='margin-bottom: 0;'>Complete the technical interview questions below</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Question display
    if not st.session_state.get("introduction_analyzed", False):
        st.markdown("### 📄 Job Application - Step 1: Resume Upload")
        uploaded_file = st.file_uploader("To begin your application, please upload your resume (PDF or DOCX)", type=['pdf', 'docx', 'doc'])
        
        if uploaded_file is not None:
            if st.button("Submit Application & Start Interview"):
                with st.spinner("Processing application..."):
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
                        candidate_level=st.session_state.candidate_profile["experience_level"],
                        specific_skills=detected_skills
                    )

                    st.session_state.questions = technical_questions

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
                background: #EFF6FF;
                border: 1px solid #BFDBFE;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                font-size: 1.15em;
                font-weight: 500;
                color: #1E293B;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
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
            height=200,
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
                    margin: 1rem 0 2rem 0;
                    padding: 8px 16px;
                    border-radius: 20px;
                    background: #F1F5F9;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    border: 1px solid #E2E8F0;
                ">
                    <span style="color: #64748B;">🔒 Skill:</span>
                    <strong style="color: #0F172A;">{locked_skill}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

        
        # Update session state with current response
        st.session_state.current_response = response
        
        # Submit button - Centralized Focal Point
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Use columns to assign position to right
        if current_prompt:
            c1, c2 = st.columns([5, 1])
            with c2:
                if st.button("Submit Response", type="primary", use_container_width=True, key=f"submit_response_{st.session_state.current_question_index}"):
                    if response and response.strip():
                        process_response(response.strip())
                    else:
                        st.warning("Please enter a response before submitting.")
        else:
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
    # col1, col2, col3 = st.columns([1, 3, 1])
    # with col2:
    with st.container():

        # Welcome content
        st.markdown("""
        <div style='
            text-align: center; 
            margin-bottom: 3rem;
            background: linear-gradient(135deg, #FFFFFF 0%, #F0F9FF 100%);
            padding: 2.5rem 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(59, 130, 246, 0.15);
            border: 1px solid #BFDBFE;
        '>
            <div style='margin-bottom: 1rem;'>
                <span class='verified-badge'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Enterprise Verified
                </span>
            </div>
            <h1 style='color: #1E3A8A; font-size: 32px; font-weight: 700; margin-bottom: 0.5rem;'>Welcome to Your Technical Interview</h1>
            <p style='color: #475569; font-size: 1.1rem; max-width: 600px; margin: 0 auto;'>
                Prepare to showcase your skills through an AI-powered adaptive interview process
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # How it works section (Redesigned)
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
        '>
        </div>
        """, unsafe_allow_html=True)
        
        # Minimized, compact list without heavy divisions
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #DBEAFE 0%, #E0E7FF 50%, #DDD6FE 100%);
            border-radius: 16px; 
            padding: 2rem; 
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.15);
            border: 1px solid #BFDBFE;
            margin-top: 1rem;
        '>
            <p style='color: #1E3A8A; font-size: 1rem; font-weight: 500; margin: 0; line-height: 1.8;'>
                This interview uses AI to generate adaptive questions based on your responses, providing a more personalized and relevant assessment of your skills.
            </p>
        </div>
        """, unsafe_allow_html=True)

        
        # AI-Powered note
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); 
            border: 1px solid #A7F3D0; 
            border-radius: 12px; 
            padding: 1.5rem; 
            margin-top: 2rem;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
        '>
            <h4 style='color: #065F46; margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 600;'>🤖 AI-Powered Interview</h4>
            <p style='color: #047857; margin: 0; font-size: 0.95rem; line-height: 1.6;'>
                This interview uses AI to generate adaptive questions based on your responses, 
                providing a more personalized and relevant assessment of your skills.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start button
        st.markdown("<br>", unsafe_allow_html=True)
        # col1, col2, col3 = st.columns([1, 2, 1])
        # with col2:
        # Start Interview Button - Centered
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Start Interview", type="primary", use_container_width=True, key="start_interview_btn"):
                st.session_state.interview_started = True
                st.session_state.interview_active = True
                st.rerun()

def show_termination_screen():
    """Display termination screen"""
    
    st.markdown("""
    <div class='main-header' style='border-color: #FECACA;'>
        <h1 style='color: #DC2626 !important;'>⛔ Interview Terminated</h1>
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
    
    # Styled Warning Card
    st.markdown(f"""
    <div style='
        background: #FEF2F2; 
        border: 1px solid #FECACA; 
        border-radius: 12px; 
        padding: 1.5rem; 
        margin: 2rem 0;
    '>
        <h4 style='color: #B91C1C; margin-top: 0; font-size: 1.1rem;'>Termination Reason</h4>
        <p style='color: #7F1D1D; font-size: 1rem; margin: 0;'>{reasons_map.get(reason, reason)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.termination_log:
        with st.expander("📋 Termination Details", expanded=True):
            for log in st.session_state.termination_log:
                st.markdown(f"""
                <div style='
                    background: #FFFFFF; 
                    padding: 1rem; 
                    border-radius: 8px; 
                    margin: 0.5rem 0; 
                    border: 1px solid #E2E8F0;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                '>
                    <strong style='color: #0F172A;'>Time:</strong> <span style='color: #475569;'>{log.get('time', 'N/A')}</span><br>
                    <strong style='color: #0F172A;'>Reason:</strong> <span style='color: #475569;'>{log.get('reason', 'N/A')}</span><br>
                    <strong style='color: #0F172A;'>Response:</strong> <span style='color: #475569;'>{log.get('response', 'N/A')}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")

def save_interview_report():
    """Save the interview report using ReportManager"""
    try:
        report_path = report_manager.save_interview_report(st.session_state)
        st.session_state.report_path = report_path
        # Mark report as saved to avoid duplicate saves on reruns
        st.session_state.report_saved = True
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        # Ensure flag is unset on failure so retries can occur
        st.session_state.report_saved = False

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

    return False

def login_page():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2.5rem; margin-top: 4rem;'>
            <h1 class='gradient-text' style='font-size: 3.5rem; margin-bottom: 0.5rem; letter-spacing: -0.03em;'>AI Recruiter</h1>
            <p style='color: #64748B; font-size: 1.15rem; font-weight: 500;'>The Future of Hiring, Automated.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Concise Centered Layout
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:


        # Create a container for the card effect (styled via CSS)
        with st.container():
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    try:
                        db = SessionLocal()
                        user = login_user(db, email, password)
                        db.close()
                        if user:
                            st.session_state.user = user.email
                            st.session_state.user_id = user.id
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                    except Exception as e:
                        st.error(f"Database error: {e}")
        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_signup = st.form_submit_button("Sign Up")
                
                if submit_signup:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        try:
                            db = SessionLocal()
                            user, msg = create_user(db, new_email, new_password)
                            db.close()
                            if user:
                                st.session_state.user = user.email
                                st.session_state.user_id = user.id
                                st.success("Account created! Logging in...")
                                st.rerun()
                            else:
                                st.error(f"Error: {msg}")
                        except Exception as e:
                            st.error(f"Database error: {e}")

def main():
    """Main application function"""
    try:
        init_db()
    except Exception as e:
        st.error(f"Database connection error: {e}")

    if 'user' not in st.session_state:
        st.session_state.user = None
        
    # ===== THEME INJECTION =====
    # Conditional CSS based on login state
    if not st.session_state.user:
        st.markdown(css_login, unsafe_allow_html=True)
        login_page()
        return
    else:
        st.markdown(css_light, unsafe_allow_html=True)

    # Sidebar user info now moved to bottom
    # with st.sidebar:
        # User info is now handled in the main sidebar block
        # pass

    
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
    <div class='main-header' style='
        text-align: center;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #6366F1 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.2);
    '>
        <h1 style='color: #FFFFFF; margin-bottom: 0.5rem; font-size: 2rem; font-weight: 700;'>Virtual HR</h1>
        <p style='color: #E0E7FF; margin: 0; font-size: 1rem;'>AI-Powered Adaptive Technical & Behavioral Screening Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
        '>
            <h3 style='color: #FFFFFF; margin: 0; font-size: 1.1rem; font-weight: 600; text-align: center;'>Interview Dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        if st.session_state.interview_active:
            # Progress
            total_questions = st.session_state.total_questions_to_ask
            current_q = min(st.session_state.current_question_index, total_questions)
            progress = min(current_q / total_questions, 1.0)
            
            st.markdown(f"**Question {current_q} of {total_questions}**")
            st.progress(progress)
            
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
        
        # About section
        st.markdown("---")
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
            border: 1px solid #BFDBFE;
        '>
            <h3 style='color: #1E3A8A; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600;'>ℹ️ About This Tool</h3>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem;'>
                <span style='color: #2563EB; font-size: 1.2rem;'>✓</span>
                <span style='color: #1E40AF; font-weight: 500; font-size: 0.9rem;'>AI-Generated Questions</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem;'>
                <span style='color: #2563EB; font-size: 1.2rem;'>✓</span>
                <span style='color: #1E40AF; font-weight: 500; font-size: 0.9rem;'>Adaptive Follow-ups</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem;'>
                <span style='color: #2563EB; font-size: 1.2rem;'>✓</span>
                <span style='color: #1E40AF; font-weight: 500; font-size: 0.9rem;'>Real-time Analysis</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span style='color: #2563EB; font-size: 1.2rem;'>✓</span>
                <span style='color: #1E40AF; font-weight: 500; font-size: 0.9rem;'>Detailed Reports</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile Pill at Bottom
        st.markdown("---")
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #EFF6FF 0%, #E0E7FF 100%); 
            padding: 12px; 
            border-radius: 10px; 
            display: flex; 
            align-items: center; 
            gap: 12px;
            border: 1px solid #BFDBFE;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
        '>
            <div style='
                width: 36px; 
                height: 36px; 
                background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%); 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
            '>
                {st.session_state.user[0].upper() if st.session_state.user else 'U'}
            </div>
            <div style='overflow: hidden;'>
                <div style='font-size: 11px; color: #64748B; font-weight: 500;'>Logged in as</div>
                <div style='font-size: 14px; color: #1E3A8A; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{st.session_state.user}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Center the logout button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Logout", key="logout_btn", use_container_width=True):
                st.session_state.user = None
                st.session_state.user_id = None
                st.rerun()

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