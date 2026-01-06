import streamlit as st
import time
import os
from datetime import datetime
from interview_manager import InterviewManager
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Virtual HR Interviewer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Simplified version
css = """
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.header-container {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(90deg, #1a237e, #283593);
    border-radius: 15px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid;
}
.interviewer-message {
    background: rgba(66, 133, 244, 0.1);
    border-color: #4285F4;
}
.candidate-message {
    background: rgba(52, 168, 83, 0.1);
    border-color: #34A853;
}
.feedback-message {
    background: rgba(251, 188, 5, 0.1);
    border-color: #FBBC05;
}
.score-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 15px;
    font-size: 0.8em;
    font-weight: bold;
    margin-left: 10px;
}
.score-excellent { background: #4CAF50; color: white; }
.score-good { background: #8BC34A; color: white; }
.score-average { background: #FF9800; color: white; }
.score-poor { background: #F44336; color: white; }
.progress-container {
    background: rgba(255, 255, 255, 0.9);
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'interview_started': False,
        'interview_manager': None,
        'current_question': None,
        'interview_history': [],
        'user_response': "",
        'interview_completed': False,
        'question_count': 0,
        'total_questions': 7,
        'scores': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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

def safe_file_read(filename):
    """Safely read file with multiple encoding attempts"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # If all encodings fail, try binary read
    with open(filename, 'rb') as f:
        return f.read().decode('utf-8', errors='ignore')

def visualize_scores(scores_data):
    """Create score visualization"""
    if not scores_data or not isinstance(scores_data, dict):
        # Create a placeholder visualization for no data
        fig = go.Figure()
        fig.add_annotation(
            text="No score data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(height=400)
        return fig
    
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

def get_score_badge(score):
    """Get CSS class for score badge"""
    if score >= 8:
        return "score-excellent"
    elif score >= 6:
        return "score-good"
    elif score >= 4:
        return "score-average"
    else:
        return "score-poor"

def show_welcome_screen():
    """Display welcome screen"""
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <h2>🚀 Welcome to Virtual HR Interviewer</h2>
            <p style='font-size: 1.2em;'>AI-Powered Technical Screening Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### How it works:
        1. **Introduction**: Share your background, skills, and experience
        2. **AI Analysis**: Our system identifies your primary skills
        3. **Adaptive Questions**: Get 7-8 tailored technical and behavioral questions
        4. **Real-time Feedback**: Receive scores and feedback after each answer
        5. **Comprehensive Report**: Get detailed analysis and recommendations
        
        ### Tips for success:
        - Be specific about your projects and skills
        - Aim for 100-200 words per answer
        - Include real-world examples
        - Take your time to think before responding
        """)
        
        # Past reports section
        if os.path.exists('reports'):
            report_files = [f for f in os.listdir('reports') if f.endswith('.txt')]
            if report_files:
                st.markdown("---")
                st.markdown("### 📁 Previous Interview Reports")
                for report in sorted(report_files[-3:], reverse=True):
                    try:
                        content = safe_file_read(f"reports/{report}")[:300] + "..."
                        with st.expander(f"📄 {report}", expanded=False):
                            st.text(content)
                            
                            # Safe download
                            try:
                                file_content = safe_file_read(f"reports/{report}")
                                st.download_button(
                                    label="📥 Download Report",
                                    data=file_content,
                                    file_name=report,
                                    mime="text/plain",
                                    key=f"dl_{report}"
                                )
                            except:
                                st.warning("Could not load file for download")
                    except Exception as e:
                        st.error(f"Error reading report: {str(e)}")
        
        # Start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎤 Start New Interview", type="primary", use_container_width=True, key="start_btn"):
                try:
                    manager = InterviewManager()
                    st.session_state.interview_manager = manager
                    st.session_state.interview_started = True
                    
                    # Get initial question
                    initial_question = "Tell me about yourself, including your projects, technical skills, and work experience."
                    st.session_state.current_question = initial_question
                    
                    # Ensure questions_asked list exists
                    if not hasattr(manager.interview_data, 'questions_asked') or manager.interview_data.get('questions_asked') is None:
                        manager.interview_data['questions_asked'] = []
                    
                    manager.interview_data['questions_asked'].append(initial_question)
                    
                    # Add to history
                    add_to_history('interviewer', initial_question)
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error starting interview: {str(e)}")
                    st.exception(e)

def show_interview_in_progress():
    """Display interview in progress"""
    st.markdown("---")
    
    # Progress bar
    progress = min(st.session_state.question_count / st.session_state.total_questions, 1.0)
    st.markdown(f"""
    <div class='progress-container'>
        <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
            <span><strong>Progress:</strong> Question {st.session_state.question_count}/{st.session_state.total_questions}</span>
            <span><strong>{(progress*100):.0f}% Complete</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat display
    st.markdown("### 💬 Interview Dialogue")
    
    for message in st.session_state.interview_history:
        if message['role'] == 'interviewer':
            st.markdown(f"""
            <div class='chat-message interviewer-message'>
                <strong>💼 Interviewer:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        elif message['role'] == 'candidate':
            st.markdown(f"""
            <div class='chat-message candidate-message'>
                <strong>🧑‍💻 You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        elif message['role'] == 'feedback':
            score_badge = ""
            if message.get('score') is not None:
                score = message['score']
                badge_class = get_score_badge(score)
                score_badge = f"<span class='score-badge {badge_class}'>{score}/10</span>"
            
            st.markdown(f"""
            <div class='chat-message feedback-message'>
                <strong>📊 Feedback:</strong> {message['content']} {score_badge}
            </div>
            """, unsafe_allow_html=True)
    
    # Current question
    if st.session_state.current_question:
        st.markdown("---")
        st.markdown("### 📝 **Current Question**")
        st.info(st.session_state.current_question)
    
    # Response input
    st.markdown("---")
    st.markdown("### 💭 Your Response")
    
    response = st.text_area(
        "Type your answer here:",
        value=st.session_state.user_response,
        height=150,
        key="response_input",
        placeholder="Provide your detailed answer here...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("📤 Submit Answer", type="primary", use_container_width=True, disabled=not response.strip()): # type: ignore
            process_response(response)
    
    with col2:
        if st.button("⏭️ Skip Question", type="secondary", use_container_width=True):
            skip_question()



def skip_question():
    """Skip current question"""
    add_to_history('candidate', "[Question skipped]")
    
    manager = st.session_state.interview_manager
    next_q = manager.get_next_question()
    
    if next_q:
        st.session_state.current_question = next_q
        st.session_state.question_count += 1
        add_to_history('interviewer', next_q)
        st.rerun()
    else:
        end_interview()

def end_interview():
    """End the interview"""
    st.session_state.interview_completed = True
    if st.session_state.interview_manager:
        try:
            st.session_state.interview_manager.end_interview()
        except Exception as e:
            st.warning(f"Note: Could not generate final report: {str(e)}")
    st.rerun()

def get_download_link(filename):
    """Create download link for report file"""
    if filename and os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            b64 = base64.b64encode(content.encode()).decode()
            return f'<a href="data:file/txt;base64,{b64}" download="{os.path.basename(filename)}">Download Full Report</a>'
        except Exception as e:
            return f"Error generating download link: {str(e)}"
    return "Report not available"

def show_report():
    """Display interview report"""
    st.markdown("---")
    
    if not st.session_state.interview_manager:
        st.error("No interview data available.")
        return
    
    manager = st.session_state.interview_manager
    interview_data = manager.interview_data
    
    # Calculate summary statistics
    total_questions = len(interview_data.get('questions_asked', [])) - 1
    total_questions = max(0, total_questions)
    
    avg_score = 0
    if interview_data.get('responses') and len(interview_data['responses']) > 1:
        scores = [r.get('score', 0) for r in interview_data['responses'][1:]]
        avg_score = sum(scores) / len(scores) if scores else 0
    
    primary_skill = interview_data.get('candidate_info', {}).get('primary_skill', 'Not identified')
    
    # Header
    st.markdown("""
    <div class='header-container'>
        <h2>📊 Interview Analysis Complete</h2>
        <p>Your detailed performance report is ready</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Answered", total_questions)
    with col2:
        st.metric("Average Score", f"{avg_score:.1f}/10")
    with col3:
        st.metric("Primary Skill", primary_skill.title())
    
    # interview_data = manager.interview_data

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualization", "📋 Detailed Analysis", "📜 Transcript", "🎯 Recommendation"])
    
    with tab1:
        # Score visualization
        if st.session_state.scores:
            fig = visualize_scores(st.session_state.scores)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No score data available for visualization.")
    
    with tab2:
        # Question-by-question analysis
        if interview_data.get('responses'):
            st.markdown("### Question Analysis")
            
            for i, response in enumerate(interview_data['responses']):
                if i == 0:
                    continue  # Skip introduction
                
                with st.expander(f"Q{i}: {response.get('question', 'Question')[0:50]}...", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Question:** {response.get('question', 'N/A')}")
                        st.markdown(f"**Your Answer:** {response.get('answer', 'N/A')}")
                    with col2:
                        score = response.get('score', 0)
                        badge_class = get_score_badge(score)
                        st.markdown(f"<div style='text-align: center;'><span class='score-badge {badge_class}'>{score}/10</span></div>", unsafe_allow_html=True)
        else:
            st.info("No detailed analysis available.")
    
    with tab3:
        # Transcript
        transcript = ""
        if interview_data.get('responses'):
            for i, response in enumerate(interview_data['responses']):
                if i == 0:
                    transcript += f"### Introduction\n\n"
                    transcript += f"**Interviewer:** {response.get('question', 'Tell me about yourself...')}\n\n"
                    transcript += f"**You:** {response.get('answer', '')}\n\n"
                else:
                    transcript += f"### Question {i}\n\n"
                    transcript += f"**Interviewer:** {response.get('question', 'Question')}\n\n"
                    transcript += f"**You:** {response.get('answer', 'Answer')}\n\n"
                    transcript += f"**Score:** {response.get('score', 'N/A')}/10\n\n"
                    transcript += "---\n\n"
        
        st.text_area("Interview Transcript", transcript or "No transcript available", height=400)
        
        # Download transcript
        if transcript:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/interview_transcript_{timestamp}.txt"
            os.makedirs("reports", exist_ok=True)
            
            if st.button("📥 Download Transcript", key="download_transcript"):
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    st.success(f"Transcript saved to {filename}")
                    
                    # Provide download link
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    b64 = base64.b64encode(content.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="{os.path.basename(filename)}">Click here to download</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error saving transcript: {str(e)}")
    
    with tab4:
        # Recommendation
        st.markdown("### Final Recommendation")
        
        if avg_score >= 7:
            st.success("""
            **✅ STRONGLY RECOMMEND - Proceed to Next Round**
            
            **Strengths identified:**
            - Strong technical understanding
            - Clear and structured communication
            - Good practical knowledge
            
            **Next steps:**
            - Schedule technical coding interview
            - Prepare system design questions
            - Review advanced concepts in primary skill area
            """)
        elif avg_score >= 5:
            st.warning("""
            **⚠️ CONDITIONAL RECOMMEND - Consider with Feedback**
            
            **Areas for improvement:**
            - Technical depth needs enhancement
            - Some gaps in advanced concepts
            - Could use more practical examples
            
            **Development suggestions:**
            - Practice explaining complex concepts
            - Work on hands-on projects
            - Consider targeted learning resources
            """)
        else:
            st.error("""
            **❌ NOT RECOMMENDED - Requires Improvement**
            
            **Key concerns:**
            - Significant knowledge gaps
            - Responses lack depth
            - Limited practical application
            
            **Improvement roadmap:**
            - Focus on foundational concepts
            - Complete relevant courses
            - Gain project experience
            - Re-apply in 3-6 months
            """)
    
    # Report download and restart
    # Report download section
    st.markdown("---")
    st.markdown("### 📄 Full Report Download")
    
    # Check if report was generated and has a valid filename
    report_generated = False
    report_content = ""
    report_filename = ""
    
    if hasattr(manager, 'report_filename') and manager.report_filename:
        try:
            if os.path.exists(manager.report_filename):
                with open(manager.report_filename, 'r') as f:
                    report_content = f.read()
                report_generated = True
                report_filename = manager.report_filename
        except (TypeError, FileNotFoundError):
            # If file doesn't exist or path is invalid, generate a new one
            pass
    
    # If report wasn't properly generated, create it now
    if not report_generated:
        # Generate a timestamp for the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reports/interview_report_{timestamp}.txt"
        os.makedirs("reports", exist_ok=True)
        
        # Create report content
        report_content = f"Interview Report - {timestamp}\n"
        report_content += "="*50 + "\n\n"
        report_content += f"Candidate: {interview_data['candidate_info'].get('name', 'N/A')}\n"
        report_content += f"Primary Skill: {interview_data['candidate_info'].get('primary_skill', 'N/A')}\n"
        report_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add summary
        if interview_data['responses']:
            avg_score = sum(r.get('score', 0) for r in interview_data['responses'][1:]) / len(interview_data['responses'][1:])
            report_content += f"Overall Score: {avg_score:.1f}/10\n"
            report_content += f"Questions Answered: {len(interview_data['questions_asked']) - 1}\n\n"
        
        # Save the report
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Update the manager with the new filename
        manager.report_filename = report_filename
    
    col1, col2 = st.columns(2)
    with col1:
        # Now we know the report exists
        st.download_button(
            label="📥 Download Comprehensive Report",
            data=report_content,
            file_name=os.path.basename(report_filename),
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

def main():
    """Main application function"""
    # Header
    st.markdown("""
    <div class='header-container'>
        <h1>🎯 Virtual HR Interviewer</h1>
        <p style='font-size: 1.2em;'>AI-Powered Technical & Behavioral Screening</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Interview Dashboard")
        
        if st.session_state.interview_started:
            # Progress
            progress = min(st.session_state.question_count / st.session_state.total_questions, 1.0)
            st.progress(progress)
            st.caption(f"Question {st.session_state.question_count}/{st.session_state.total_questions}")
            
            # Score display if available
            if st.session_state.scores:
                avg_score = sum(st.session_state.scores) / len(st.session_state.scores) if st.session_state.scores else 0
                st.metric("Current Average", f"{avg_score:.1f}/10")
            
            # Controls
            st.markdown("---")
            if st.button("⏹️ End Interview", type="secondary", use_container_width=True):
                st.session_state.interview_started = False
                st.session_state.interview_completed = True
                st.rerun()
        
        # About
        st.markdown("---")
        st.markdown("### ℹ️ About This Tool")
        st.markdown("""
        This AI-powered interviewer:
        - 🧠 Analyzes your technical background
        - 🔄 Generates adaptive questions
        - 📊 Provides real-time feedback
        - 📝 Creates detailed reports
        """)
    
    # Main content routing
    if not st.session_state.interview_started and not st.session_state.interview_completed:
        show_welcome_screen()
    elif st.session_state.interview_started and not st.session_state.interview_completed:
        show_interview_in_progress()

    elif st.session_state.interview_completed:
        st.markdown("---")
        st.markdown("## 📊 Interview Analysis Complete")
        
        if not st.session_state.interview_manager:
            st.error("Interview data not found. Please start a new interview.")
            if st.button("🔄 Start New Interview", type="primary"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session_state()
                st.rerun()
            return
        
        manager = st.session_state.interview_manager
        
        # Ensure interview_data exists
        if not hasattr(manager, 'interview_data'):
            st.error("No interview data available. Please start a new interview.")
            if st.button("🔄 Start New Interview", type="primary"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session_state()
                st.rerun()
            return

        show_report()
        
if __name__ == "__main__":
    main()