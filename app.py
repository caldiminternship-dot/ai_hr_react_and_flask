import streamlit as st
import time
import json
import os
from datetime import datetime
from interview_manager import InterviewManager
from utils import format_response, Fore, Style
import base64
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Virtual HR Interviewer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
def init_session_state():
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'interview_manager' not in st.session_state:
        st.session_state.interview_manager = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'interview_history' not in st.session_state:
        st.session_state.interview_history = []
    if 'user_response' not in st.session_state:
        st.session_state.user_response = ""
    if 'interview_completed' not in st.session_state:
        st.session_state.interview_completed = False
    if 'report_data' not in st.session_state:
        st.session_state.report_data = None
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0

init_session_state()

# Helper functions
def add_to_history(role, content, score=None):
    """Add message to interview history"""
    st.session_state.interview_history.append({
        'role': role,
        'content': content,
        'timestamp': time.time(),
        'score': score
    })

def get_download_link(filename):
    """Create download link for report file"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{os.path.basename(filename)}">Download Full Report</a>'

def visualize_scores(scores_data):
    """Create score visualization"""
    if not scores_data:
        return None
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Overall Score Distribution', 'Category Breakdown'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    # Pie chart for overall score
    labels = ['Excellent (8-10)', 'Good (6-7)', 'Average (4-5)', 'Poor (0-3)']
    values = [0, 0, 0, 0]
    overall_score = scores_data.get('overall', 0)
    
    if overall_score >= 8:
        values[0] = 1
    elif overall_score >= 6:
        values[1] = 1
    elif overall_score >= 4:
        values[2] = 1
    else:
        values[3] = 1
    
    fig.add_trace(
        go.Pie(labels=labels, values=values, hole=0.3, marker_colors=['#00cc96', '#ffa15a', '#ef553b', '#636efa']),
        row=1, col=1
    )
    
    # Bar chart for category scores
    categories = ['Technical Accuracy', 'Completeness', 'Clarity', 'Depth', 'Practicality']
    category_scores = [
        scores_data.get('technical_accuracy', 0),
        scores_data.get('completeness', 0),
        scores_data.get('clarity', 0),
        scores_data.get('depth', 0),
        scores_data.get('practicality', 0)
    ]
    
    fig.add_trace(
        go.Bar(x=categories, y=category_scores, marker_color='#636efa'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=True)
    return fig

# Main application
def main():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🎯 Virtual HR Interviewer")
        st.markdown("### AI-Powered Technical & Behavioral Screening")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Interview Dashboard")
        
        if st.session_state.interview_started:
            # Progress tracking
            progress = st.session_state.question_count / 8
            st.progress(progress)
            st.caption(f"Question {st.session_state.question_count}/8")
            
            # Quick stats
            if st.session_state.interview_manager and st.session_state.interview_manager.interview_data['responses']:
                responses = st.session_state.interview_manager.interview_data['responses']
                if len(responses) > 1:
                    avg_score = sum(r.get('score', 0) for r in responses[1:]) / len(responses[1:])
                    st.metric("Current Score", f"{avg_score:.1f}/10")
            
            # Control buttons
            st.markdown("---")
            if st.button("⏹️ End Interview", type="secondary"):
                st.session_state.interview_started = False
                st.session_state.interview_completed = True
                if st.session_state.interview_manager:
                    st.session_state.interview_manager.end_interview(early_termination=True, reason="candidate_request")
                st.rerun()
        
        # About section
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This AI-powered interviewer:
        - 🧠 Analyzes your introduction
        - 🔄 Generates adaptive questions
        - 📊 Evaluates responses in real-time
        - 📝 Creates detailed reports
        """)
    
    # Main content area
    if not st.session_state.interview_started and not st.session_state.interview_completed:
        # Welcome screen
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("### 🚀 Ready to Begin?")
            st.markdown("""
            **How it works:**
            1. You'll introduce yourself with your technical background
            2. AI will analyze your skills and generate relevant questions
            3. Answer 7-8 adaptive questions (mix of technical & behavioral)
            4. Receive immediate feedback and a comprehensive report
            
            **Tips for best results:**
            - Be specific about your projects and skills
            - Aim for 100-200 words per answer
            - Include real-world examples
            - Take your time to think before responding
            """)
            
            if st.button("🎤 Start Interview", type="primary", use_container_width=True):
                st.session_state.interview_manager = InterviewManager()
                st.session_state.interview_started = True
                st.session_state.current_question = st.session_state.interview_manager.ask_initial_question()
                add_to_history('interviewer', st.session_state.current_question)
                st.rerun()
            
            # Past reports section (if any)
            if os.path.exists('reports'):
                report_files = [f for f in os.listdir('reports') if f.endswith('.txt')]
                if report_files:
                    st.markdown("---")
                    st.markdown("### 📁 Previous Reports")
                    for report in report_files[-3:]:  # Show last 3
                        with open(f"reports/{report}", 'r') as f:
                            content = f.read(200) + "..."
                        with st.expander(f"📄 {report}"):
                            st.text(content[:500])
                            st.download_button(
                                label="Download",
                                data=open(f"reports/{report}", 'r').read(),
                                file_name=report,
                                mime="text/plain"
                            )
    
    elif st.session_state.interview_started and not st.session_state.interview_completed:
        # Interview in progress
        st.markdown("---")
        
        # Interview chat display
        chat_container = st.container()
        with chat_container:
            st.markdown("### 💬 Interview Dialogue")
            
            for i, message in enumerate(st.session_state.interview_history):
                if message['role'] == 'interviewer':
                    with st.chat_message("assistant", avatar="💼"):
                        st.markdown(f"**Interviewer:** {message['content']}")
                        if 'score' in message and message['score']:
                            st.caption(f"Score: {message['score']}/10")
                elif message['role'] == 'candidate':
                    with st.chat_message("user", avatar="🧑‍💻"):
                        st.markdown(f"**You:** {message['content']}")
                elif message['role'] == 'feedback':
                    with st.chat_message("assistant", avatar="📊"):
                        st.markdown(f"📈 **Feedback:** {message['content']}")
        
        # Current question display
        if st.session_state.current_question:
            st.markdown("---")
            st.markdown(f"### 📝 **Current Question**")
            st.info(st.session_state.current_question)
        
        # Response input
        st.markdown("---")
        st.markdown("### 💭 Your Response")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            response = st.text_area(
                "Type your answer here:",
                value=st.session_state.user_response,
                height=150,
                key="response_input",
                placeholder="Provide a detailed answer (100-200 words recommended)...",
                label_visibility="collapsed"
            )
            st.session_state.user_response = response
        
        with col2:
            st.markdown("###")
            if st.button("📤 Submit Answer", type="primary", use_container_width=True):
                if response.strip():
                    # Process response
                    add_to_history('candidate', response)
                    
                    # Process through interview manager
                    manager = st.session_state.interview_manager
                    result = manager.process_response(response)
                    
                    # Add feedback to history
                    if 'score' in result:
                        score = result.get('score', 0)
                        feedback_msg = f"Response scored: {score}/10"
                        if score >= 8:
                            feedback_msg += " - Excellent!"
                        elif score >= 6:
                            feedback_msg += " - Good job!"
                        else:
                            feedback_msg += " - Needs improvement."
                        add_to_history('feedback', feedback_msg, score)
                    
                    # Get next question or end interview
                    if manager.should_continue():
                        next_question = manager.get_next_question()
                        if next_question:
                            st.session_state.current_question = next_question
                            st.session_state.question_count += 1
                            add_to_history('interviewer', next_question)
                        else:
                            st.session_state.interview_completed = True
                            manager.end_interview()
                    else:
                        st.session_state.interview_completed = True
                        manager.end_interview()
                    
                    # Clear response
                    st.session_state.user_response = ""
                    st.rerun()
                else:
                    st.warning("Please enter a response before submitting.")
            
            if st.button("⏭️ Skip Question", type="secondary", use_container_width=True):
                add_to_history('candidate', "[Skipped]")
                manager = st.session_state.interview_manager
                next_question = manager.get_next_question()
                if next_question:
                    st.session_state.current_question = next_question
                    st.session_state.question_count += 1
                    add_to_history('interviewer', next_question)
                    st.rerun()
    
    elif st.session_state.interview_completed:
        # Report display
        st.markdown("---")
        st.markdown("## 📊 Interview Analysis Complete")
        
        if st.session_state.interview_manager:
            manager = st.session_state.interview_manager
            interview_data = manager.interview_data
            
            # Create tabs for different report sections
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Summary", "📝 Detailed Analysis", "📋 Transcript", "💡 Recommendations"])
            
            with tab1:
                # Overall summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_q = len(interview_data['questions_asked']) - 1
                    st.metric("Questions Answered", total_q)
                
                with col2:
                    if interview_data['responses']:
                        avg_score = sum(r.get('score', 0) for r in interview_data['responses'][1:]) / len(interview_data['responses'][1:])
                        st.metric("Average Score", f"{avg_score:.1f}/10")
                
                with col3:
                    primary_skill = interview_data['candidate_info'].get('primary_skill', 'N/A').title()
                    st.metric("Primary Skill", primary_skill)
                
                # Score visualization
                if interview_data['responses']:
                    scores = []
                    for response in interview_data['responses'][1:]:
                        if 'evaluation' in response:
                            scores.append(response['evaluation'])
                    
                    if scores:
                        avg_scores = {
                            'overall': avg_score,
                            'technical_accuracy': sum(s.get('technical_accuracy', 0) for s in scores) / len(scores),
                            'completeness': sum(s.get('completeness', 0) for s in scores) / len(scores),
                            'clarity': sum(s.get('clarity', 0) for s in scores) / len(scores),
                            'depth': sum(s.get('depth', 0) for s in scores) / len(scores),
                            'practicality': sum(s.get('practicality', 0) for s in scores) / len(scores),
                        }
                        
                        fig = visualize_scores(avg_scores)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Question-by-question analysis
                st.markdown("### 📋 Question Analysis")
                
                for i, response in enumerate(interview_data['responses']):
                    if i == 0:
                        # Introduction
                        with st.expander(f"📄 Introduction", expanded=False):
                            st.markdown(f"**Question:** {response['question']}")
                            st.markdown(f"**Your Answer:** {response['answer'][:500]}...")
                            st.markdown(f"**Score:** {response.get('score', 'N/A')}/10")
                    else:
                        # Regular questions
                        with st.expander(f"Q{i}: {response['question'][:50]}...", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Question:** {response['question']}")
                                st.markdown(f"**Your Answer:** {response['answer']}")
                            with col2:
                                score = response.get('score', 0)
                                score_color = "🟢" if score >= 8 else "🟡" if score >= 5 else "🔴"
                                st.metric("Score", f"{score}/10", delta=score_color)
                            
                            if 'evaluation' in response:
                                eval_data = response['evaluation']
                                st.markdown("**Detailed Evaluation:**")
                                
                                eval_cols = st.columns(5)
                                metrics = [
                                    ("Technical", eval_data.get('technical_accuracy', 0)),
                                    ("Complete", eval_data.get('completeness', 0)),
                                    ("Clear", eval_data.get('clarity', 0)),
                                    ("Deep", eval_data.get('depth', 0)),
                                    ("Practical", eval_data.get('practicality', 0))
                                ]
                                
                                for idx, (label, value) in enumerate(metrics):
                                    with eval_cols[idx]:
                                        st.progress(value/10)
                                        st.caption(f"{label}: {value}/10")
            
            with tab3:
                # Full transcript
                st.markdown("### 📜 Complete Interview Transcript")
                
                transcript = ""
                for i, response in enumerate(interview_data['responses']):
                    if i == 0:
                        transcript += f"### Introduction\n\n"
                        transcript += f"**Interviewer:** {response['question']}\n\n"
                        transcript += f"**Candidate:** {response['answer']}\n\n"
                    else:
                        transcript += f"### Question {i}\n\n"
                        transcript += f"**Interviewer:** {response['question']}\n\n"
                        transcript += f"**Candidate:** {response['answer']}\n\n"
                        transcript += f"**Score:** {response.get('score', 'N/A')}/10\n\n"
                        transcript += "---\n\n"
                
                st.text_area("Transcript", transcript, height=600)
                
                # Download button for transcript
                if st.button("📥 Download Transcript", type="secondary"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"reports/interview_transcript_{timestamp}.txt"
                    os.makedirs("reports", exist_ok=True)
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    st.success(f"Transcript saved to {filename}")
            
            with tab4:
                # Recommendations
                st.markdown("### 🎯 Final Recommendation")
                
                if interview_data['responses']:
                    avg_score = sum(r.get('score', 0) for r in interview_data['responses'][1:]) / len(interview_data['responses'][1:])
                    
                    if avg_score >= 7:
                        st.success("**✅ STRONGLY RECOMMEND - Proceed to Next Round**")
                        st.markdown("""
                        **Strengths identified:**
                        - Demonstrates solid technical understanding
                        - Provides clear, structured responses
                        - Shows practical application knowledge
                        
                        **Next steps:**
                        - Schedule technical coding interview
                        - Prepare system design questions
                        - Review company-specific tech stack
                        """)
                    elif avg_score >= 5:
                        st.warning("**⚠️ CONDITIONAL RECOMMEND - Consider with Feedback**")
                        st.markdown("""
                        **Areas for improvement:**
                        - Technical depth could be enhanced
                        - Some gaps in advanced concepts
                        - Could benefit from more examples
                        
                        **Development suggestions:**
                        - Practice explaining complex concepts
                        - Work on project portfolio
                        - Consider mentorship program
                        """)
                    else:
                        st.error("**❌ NOT RECOMMENDED - Requires Improvement**")
                        st.markdown("""
                        **Key concerns:**
                        - Significant technical knowledge gaps
                        - Responses lack depth and clarity
                        - Limited practical application
                        
                        **Improvement roadmap:**
                        - Focus on foundational concepts
                        - Complete relevant coursework
                        - Gain hands-on project experience
                        - Re-apply in 3-6 months
                        """)
            
            # Report download section
            st.markdown("---")
            st.markdown("### 📄 Full Report Download")
            
            col1, col2 = st.columns(2)
            with col1:
                if hasattr(manager, 'report_filename') and os.path.exists(manager.report_filename):
                    with open(manager.report_filename, 'r') as f:
                        report_content = f.read()
                    st.download_button(
                        label="📥 Download Comprehensive Report",
                        data=report_content,
                        file_name=os.path.basename(manager.report_filename),
                        mime="text/plain",
                        type="primary",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🔄 Start New Interview", type="secondary", use_container_width=True):
                    # Reset session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    init_session_state()
                    st.rerun()

if __name__ == "__main__":
    main()