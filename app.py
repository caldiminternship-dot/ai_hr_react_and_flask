import streamlit as st
import time
import os
from datetime import datetime
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from response_analyzer import ResponseAnalyzer
from report_manager import ReportManager
import json
# Initialize report manager
report_manager = ReportManager()
# Initialize the analyzer
analyzer = ResponseAnalyzer()

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
    /* Base styling */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Main containers */
    .main-header {
        text-align: center;
        padding: 2.5rem 1rem;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #2d3748;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        color: #64B5F6;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    
    .main-header p {
        color: #B0BEC5;
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Card styling */
    .stCard {
        background-color: #1e1e2e;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #2d3748;
        margin-bottom: 1rem;
    }
    
    /* Chat messages */
    .chat-container {
        background-color: #1a1a2e;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #2d3748;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid;
    }
    
    .interviewer-message {
        background: rgba(100, 181, 246, 0.1);
        border-color: #64B5F6;
    }
    
    .candidate-message {
        background: rgba(76, 175, 80, 0.1);
        border-color: #4CAF50;
    }
    
    .system-message {
        background: rgba(255, 193, 7, 0.1);
        border-color: #FFC107;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .primary-button > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .secondary-button > button {
        background: linear-gradient(135deg, #434343 0%, #000000 100%);
    }
    
    /* Metrics and stats */
    .stMetric {
        background-color: #1e1e2e;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #2d3748;
    }
    
    .stMetric > div[data-testid="stMetricLabel"] {
        color: #B0BEC5;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .stMetric > div[data-testid="stMetricValue"] {
        color: #64B5F6;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .stMetric > div[data-testid="stMetricDelta"] {
        color: #4CAF50;
    }
    
    /* Text areas and inputs */
    .stTextArea textarea {
        background-color: #1e1e2e;
        color: #FAFAFA;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #64B5F6;
        box-shadow: 0 0 0 2px rgba(100, 181, 246, 0.2);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1a2e;
        border-right: 1px solid #2d3748;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e1e2e;
        padding: 4px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #B0BEC5;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #64B5F6;
        color: #0E1117;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 4px solid #2196F3;
    }
    
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #FFC107;
    }
    
    .stError {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #F44336;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1e1e2e;
        color: #FAFAFA;
        border: 1px solid #2d3748;
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background-color: #1a1a2e;
        border: 1px solid #2d3748;
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    /* Divider */
    hr {
        border-color: #2d3748;
        margin: 2rem 0;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #E2E8F0;
    }
    
    /* Text */
    p, div, span {
        color: #CBD5E0;
    }
    
    /* Code blocks */
    code {
        background-color: #2d3748;
        color: #81E6D9;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }
    
    /* Placeholder text */
    ::placeholder {
        color: #718096;
    }
    
    /* Custom success/warning/error styling */
    .custom-success {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .custom-warning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
        border-left: 4px solid #FFC107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .custom-error {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(244, 67, 54, 0.05));
        border-left: 4px solid #F44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
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
        'questions': [
            "Describe a challenging technical problem you solved recently and how you approached it.",
            "Explain the difference between REST and GraphQL APIs and when you would use each.",
            "How do you handle debugging a complex issue in a production system?",
            "Describe your experience with version control systems and your typical workflow.",
            "What's your approach to learning new technologies or frameworks?",
            "Tell me about a time you had to work with a difficult team member and how you handled it.",
            "Where do you see yourself in your career in 3-5 years?"
        ],
        'messages': [],
        'candidate_profile': {},
        'question_evaluations': [],
        'overall_score': 0,
        'final_score': 0,
        'introduction_analyzed': False,
        'intro_analysis': None,
        'termination_reason': '',
        'termination_log': [],
        'current_response': ''
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def process_response(response_text):
    """Process the candidate's response and update interview state"""
    
    # Clear the input after processing
    st.session_state.current_response = ""
    
    if not response_text or response_text.strip() == "":
        st.warning("Please enter a response before submitting.")
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
                    "primary_skill": analysis.get("primary_skill", "unknown"),
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
                    "content": f"✅ Introduction analyzed.",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            
            # For regular questions
            else:
                question_idx = st.session_state.current_question_index - 1
                if question_idx < len(st.session_state.questions):
                    question = st.session_state.questions[question_idx]
                    evaluation = analyzer.evaluate_answer(question, response_text)
                    
                    # Store evaluation
                    st.session_state.question_evaluations.append({
                        "question": question,
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
                    if st.session_state.current_question_index < len(st.session_state.questions):
                        st.session_state.current_question_index += 1
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
                        st.session_state.current_response = ""
                        
                    # MODIFIED: Remove score from feedback
                    score = evaluation.get("overall", 5)
                    feedback_icon = "✅" if score >= 7 else "⚠️" if score >= 5 else "❌"
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"{feedback_icon} Answer received and analyzed.",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
    
    except Exception as e:
        st.error(f"Error analyzing response: {e}")
        st.session_state.messages.append({
            "role": "system",
            "content": f"❌ Error analyzing response. Please continue.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
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
        current_question_index = st.session_state.current_question_index
        if current_question_index < len(st.session_state.questions):
            current_prompt = st.session_state.questions[current_question_index - 1]
        else:
            current_prompt = "All questions completed. Thank you!"
    
    st.info(f"**Current Question:** {current_prompt}")
    
    # Response input
    response = st.text_area(
        "Your Response:",
        value=st.session_state.get("current_response", ""),
        key="response_input",
        height=180,
        placeholder="Type your detailed response here...",
        help="Provide a comprehensive answer with examples where possible"
    )
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📤 Submit Response", type="primary", use_container_width=True, key="submit_response_btn"):
            if response and response.strip():
                # Process the response
                process_response(response.strip())
            else:
                st.warning("Please enter a response before submitting.")
    
    # Display progress
    st.markdown("---")
    total_questions = len(st.session_state.questions)
    progress = min(st.session_state.current_question_index / total_questions, 1.0)
    st.progress(progress, text=f"Progress: Question {st.session_state.current_question_index} of {total_questions}")
    
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
    
    st.markdown("""
    <div class='main-header'>
        <h1>🚀 Virtual HR Interviewer</h1>
        <p>AI-Powered Technical Screening Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome content in a centered layout
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #64B5F6;'>Welcome to Your Technical Interview</h2>
            <p style='color: #B0BEC5; font-size: 1.1rem;'>
                Prepare to showcase your skills through an AI-powered interview process
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # How it works section
        st.markdown("### 📋 How it works:")
        
        steps = [
            (" **Introduction**", "Share your background, skills, and relevant experience"),
            (" **AI Analysis**", "Our system evaluates your technical profile"),
            (" **Adaptive Questions**", "Answer 7-8 tailored technical questions"),
            (" **Real-time Interaction**", "Engage with our AI interview system"),
            (" **Comprehensive Review**", "HR team receives detailed analysis")
        ]
        
        for icon, description in steps:
            st.markdown(f"""
            <div style='background: #1e1e2e; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #64B5F6;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='font-size: 1.5rem;'>{icon.split()[0]}</span>
                    <div>
                        <strong style='color: #E2E8F0;'>{' '.join(icon.split()[1:])}</strong><br>
                        <span style='color: #CBD5E0;'>{description}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tips section
        st.markdown("### 💡 Tips for success:")
        
        tips = [
            "Be specific about your projects and achievements",
            "Aim for 100-200 words per answer for optimal detail",
            "Include real-world examples and outcomes",
            "Take your time to think before responding",
            "Focus on clear, structured communication"
        ]
        
        for tip in tips:
            st.markdown(f"""
            <div style='background: #1e1e2e; padding: 0.8rem 1rem; border-radius: 6px; margin: 0.3rem 0; border: 1px solid #2d3748;'>
                ✓ {tip}
            </div>
            """, unsafe_allow_html=True)
        
        # Start button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start New Interview", type="primary", use_container_width=True, key="start_interview_btn"):
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
        "misconduct": "Inappropriate language or behavior detected",
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True, key="start_new_elsewhere"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            st.rerun()

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
        <h1>🎉 Interview Completed Successfully!</h1>
        <p>Thank you for participating in the virtual interview</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Success message
    st.markdown("""
    <div class='custom-success'>
        <h3 style='color: #4CAF50; margin-top: 0;'>✅ Interview Submitted</h3>
        <p style='font-size: 1.1rem;'>
            Your interview responses have been successfully submitted and analyzed.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # What happens next
    st.markdown("### 📋 What happens next:")
    
    next_steps = [
        ("📄 Response Analysis", "Your answers are being processed by our AI system"),
        ("👥 HR Review", "The HR team will review your interview results"),
        ("📧 Contact", "You will be contacted regarding next steps within 3-5 business days"),
        ("📊 Internal Assessment", "Detailed scoring and analysis are for HR review only")
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
    st.markdown("### 📊 Interview Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Answered", len(st.session_state.question_evaluations))
    with col2:
        profile = st.session_state.candidate_profile
        st.metric("Experience Level", profile.get("experience_level", "N/A").title())
    with col3:
        skills = profile.get("skills", [])
        st.metric("Skills Detected", len(skills))
    
    # Restart button
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem;'>
        <p style='color: #B0BEC5; margin-bottom: 1rem;'>
            Ready for another interview or want to practice more?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True, key="restart_interview_final"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            st.rerun()

def main():
    """Main application function"""
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>Virtual HR Interviewer</h1>
        <p>AI-Powered Technical & Behavioral Screening Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Interview Dashboard")
        st.markdown("---")
        
        if st.session_state.interview_active:
            # Progress
            total_questions = len(st.session_state.questions)
            progress = min(st.session_state.current_question_index / total_questions, 1.0)
            
            st.markdown("**Progress**")
            st.progress(progress)
            st.caption(f"Question {st.session_state.current_question_index}/{total_questions}")
            
            # Quick actions
            st.markdown("---")
            st.markdown("**Quick Actions**")
            
            if st.button("⏸️ Pause Interview", use_container_width=True, key="pause_interview_btn"):
                st.session_state.interview_active = False
                st.rerun()
            
            if st.button("⏹️ End Interview", type="secondary", use_container_width=True, key="end_interview_sidebar"):
                st.session_state.interview_completed = True
                st.session_state.interview_active = False
                st.rerun()
            
            # Current stats
            st.markdown("---")
            st.markdown("**Current Status**")
            
            if st.session_state.get("introduction_analyzed", False):
                profile = st.session_state.get("candidate_profile", {})
                st.metric("Experience", profile.get("experience_level", "Not set"))
                st.metric("Primary Skill", profile.get("primary_skill", "Not set"))
        
        elif st.session_state.interview_completed:
            st.markdown("### ✅ Interview Complete")
            st.markdown("Your interview has been successfully submitted.")
            st.markdown("---")
        
        # About section
        st.markdown("---")
        st.markdown("### ℹ️ About This Tool")
        st.markdown("""
        <div style='background: #1e1e2e; padding: 1rem; border-radius: 8px;'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;'>
                <span>🧠</span><span>AI Analysis</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;'>
                <span>🔄</span><span>Adaptive Questions</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;'>
                <span>📊</span><span>Real-time Feedback</span>
            </div>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span>📝</span><span>Detailed Reports</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content routing
    if not st.session_state.interview_started:
        show_welcome_screen()
    elif st.session_state.interview_terminated:
        show_termination_screen()
    elif st.session_state.interview_active:
        show_interview_in_progress()
    elif st.session_state.interview_completed:
        show_report()

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
            "overall_score": st.session_state.overall_score,
            "final_score": st.session_state.final_score,
            "introduction_analyzed": st.session_state.introduction_analyzed,
            "total_questions_answered": len(st.session_state.question_evaluations),
            "total_questions": len(st.session_state.questions),
            "messages": st.session_state.messages[:5] if st.session_state.messages else []
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
        traceback.print_exc()  # Print full traceback for debugging
        return None
    
def generate_readable_report(report_data: dict) -> str:
    """Generate a human-readable text report from report data"""
    report = "=" * 60 + "\n"
    report += "VIRTUAL HR INTERVIEWER - CANDIDATE REPORT\n"
    report += "=" * 60 + "\n\n"
    
    # Basic info with safe access
    report += f"Report Generated: {report_data.get('timestamp', 'N/A')}\n"
    
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
    for i, eval_data in enumerate(evaluations):
        evaluation = eval_data.get('evaluation', {})
        score = evaluation.get("overall", 0)
        
        report += f"\nQuestion {i+1}: {eval_data.get('question', 'N/A')}\n"
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

if __name__ == "__main__":
    main()