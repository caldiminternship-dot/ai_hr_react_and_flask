# dashboard.py - For HR/Reviewer to view interview reports
import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

from models import SessionLocal

st.set_page_config(
    page_title="HR Interview Dashboard",
    layout="wide",
    page_icon="📊"
)

# Enterprise Light Theme CSS (HR Portal)
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ===== GLOBAL VARIABLES (ENTERPRISE) ===== */
    :root {
        --bg-color: #F8FAFC; /* Slate-50 */
        --sidebar-bg: #FFFFFF;
        --sidebar-border: #E2E8F0; /* Slate-200 */
        
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        
        --text-heading: #0F172A; /* Slate-900 */
        --text-body: #334155; /* Slate-700 */
        --text-muted: #64748B; /* Slate-500 */
        
        --primary: #2563EB; /* Blue-600 */
        --primary-hover: #1D4ED8; /* Blue-700 */
        --primary-light: #EFF6FF; /* Blue-50 */
        
        --success: #059669; /* Emerald-600 */
        --warning: #D97706; /* Amber-600 */
        --danger: #DC2626; /* Red-600 */
        
        --radius: 8px; /* Professional, tighter radius */
        --font-main: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* ===== BASE ===== */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-body);
        font-family: var(--font-main);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-heading) !important;
        font-family: var(--font-main);
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    /* ===== METRICS ===== */
    .stMetric {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
    }
    
    .stMetric > div[data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric > div[data-testid="stMetricValue"] {
        color: var(--text-heading) !important;
        font-weight: 700;
        font-size: 2rem;
    }

    /* ===== CARDS ===== */
    .custom-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: var(--primary);
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--sidebar-border);
        box-shadow: 2px 0 8px rgba(0,0,0,0.02);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: var(--radius);
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        border: 1px solid transparent;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-hover);
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }

    /* ===== ALERTS ===== */
    .stSuccess { background-color: #ECFDF5; border-left: 4px solid var(--success); color: #065F46; }
    .stWarning { background-color: #FFFBEB; border-left: 4px solid var(--warning); color: #92400E; }
    .stError { background-color: #FEF2F2; border-left: 4px solid var(--danger); color: #991B1B; }

    /* ===== DATAFRAME ===== */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        overflow: hidden;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

def load_reports():
    """Load all interview reports from the reports directory"""
    reports = []
    report_dir = "interview_reports"
    
    if not os.path.exists(report_dir):
        st.warning(f"No reports directory found: {report_dir}")
        return reports
    
    for filename in os.listdir(report_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(report_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    
                    # Ensure all required fields exist with default values
                    report_data.setdefault('total_questions_answered', 
                                         len(report_data.get('question_evaluations', [])))
                    report_data.setdefault('overall_score', 0)
                    report_data.setdefault('final_score', 0)
                    report_data.setdefault('candidate_profile', {})
                    report_data.setdefault('question_evaluations', [])
                    report_data.setdefault('timestamp', '')
                    
                    report_data['filename'] = filename
                    report_data['filepath'] = filepath
                    
                    # Determine status based on score
                    overall_score = report_data.get('overall_score', 0)
                    if overall_score >= 7:
                        report_data['status'] = 'Selected'
                        report_data['status_color'] = 'success'
                    elif overall_score >= 6:
                        report_data['status'] = 'Conditional'
                        report_data['status_color'] = 'warning'
                    else:
                        report_data['status'] = 'Rejected'
                        report_data['status_color'] = 'error'
                    
                    # Parse timestamp for display
                    timestamp_str = report_data.get('timestamp', '')
                    if timestamp_str:
                        try:
                            if 'Z' in timestamp_str:
                                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            else:
                                dt = datetime.fromisoformat(timestamp_str)
                            report_data['display_date'] = dt.strftime("%Y-%m-%d %H:%M:%S")
                            report_data['display_date_short'] = dt.strftime("%b %d, %Y")
                        except:
                            report_data['display_date'] = timestamp_str
                            report_data['display_date_short'] = timestamp_str
                    
                    reports.append(report_data)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    
    # Sort by timestamp (newest first)
    reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return reports

def create_score_chart(report_data, chart_id="default"):
    """Create visualization charts for a report with unique ID"""
    if not report_data.get('question_evaluations'):
        return None
    
    # Extract scores
    question_scores = [e["evaluation"]["overall"] for e in report_data['question_evaluations']]
    intro_score = report_data['candidate_profile'].get('intro_score', 0)
    all_scores = [intro_score] + question_scores
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Score Distribution', 'Category Breakdown', 
                       'Score Trend', 'Performance Summary'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}],
               [{'type': 'scatter'}, {'type': 'box'}]]
    )
    
    labels = ['Excellent (8-10)', 'Good (6-7)', 'Average (4-5)', 'Poor (0-3)']
    values = [0, 0, 0, 0]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    if avg_score >= 8:
        values[0] = 1
    elif avg_score >= 6:
        values[1] = 1
    elif avg_score >= 4:
        values[2] = 1
    else:
        values[3] = 1
    
    fig.add_trace(
        go.Pie(labels=labels, values=values, hole=0.3,
               marker_colors=['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
               name=f"pie_{chart_id}"),
        row=1, col=1
    )
    
    # 2. Bar chart for category scores
    if report_data['question_evaluations']:
        categories = ['Technical', 'Completeness', 'Clarity', 'Depth', 'Practical']
        category_keys = ['technical_accuracy', 'completeness', 'clarity', 'depth', 'practicality']
        
        category_scores = []
        for key in category_keys:
            scores = [e["evaluation"].get(key, 0) for e in report_data['question_evaluations']]
            avg = sum(scores) / len(scores) if scores else 0
            category_scores.append(avg)
        
        fig.add_trace(
            go.Bar(x=categories, y=category_scores, marker_color='#4f46e5',
                   text=[f'{score:.1f}' for score in category_scores],
                   textposition='auto',
                   name=f"bar_{chart_id}"),
            row=1, col=2
        )
    
    # 3. Line chart for score trend
    question_numbers = list(range(1, len(question_scores) + 1))
    fig.add_trace(
        go.Scatter(x=question_numbers, y=question_scores, mode='lines+markers',
                   name=f'line_{chart_id}', line=dict(color='#f59e0b', width=3),
                   marker=dict(size=8)),
        row=2, col=1
    )
    
    # Add average line
    if question_scores:
        avg_line = [sum(question_scores)/len(question_scores)] * len(question_numbers)
        fig.add_trace(
            go.Scatter(x=question_numbers, y=avg_line, mode='lines',
                       name=f'avg_{chart_id}', line=dict(color='#10b981', width=2, dash='dash')),
            row=2, col=1
        )
    
    # 4. Box plot for score distribution
    if question_scores:
        fig.add_trace(
            go.Box(y=question_scores, name=f'box_{chart_id}', 
                   marker_color='#3b82f6', boxmean=True),
            row=2, col=2
        )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#334155')
    )
    
    # Update subplot titles
    fig.update_annotations(font_size=14, font_color='#1e293b')
    
    return fig

def generate_readable_report_locally(report_data: dict) -> str:
    """Generate a human-readable text report locally"""
    report = "=" * 60 + "\n"
    report += "VIRTUAL HR INTERVIEWER - CANDIDATE REPORT\n"
    report += "=" * 60 + "\n\n"
    
    # Basic info
    report += f"Report Generated: {report_data.get('timestamp', 'N/A')}\n"
    total_questions = report_data.get('total_questions_answered', 
                                    len(report_data.get('question_evaluations', [])))
    report += f"Total Questions Answered: {total_questions}\n"
    report += f"Overall Score: {report_data.get('overall_score', 0):.2f}/10\n"
    report += f"Final Score: {report_data.get('final_score', 0):.2f}/10\n\n"
    
    # Candidate Profile
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

# Login removed: HR dashboard is accessible without authentication in this deployment.
# The previous `login_page` and session-based gating were removed to allow direct access.

def main():
    # Authentication removed — dashboard is accessible without login.

    st.title("HR Interview Dashboard")
    st.markdown("Analyze candidate interview results and performance metrics")
    
    # Load reports
    reports = load_reports()
    
    if not reports:
        st.info("No interview reports found. Run some interviews first.")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("## 🔍 Filters")
        st.markdown("---")
        
        # Status filter (NEW FEATURE)
        st.markdown("### Status Filter")
        status_options = ['All', 'Selected', 'Conditional', 'Rejected']
        selected_status = st.selectbox(
            "Select candidate status to view:",
            status_options,
            index=0
        )
        
        # Experience filter
        st.markdown("### Experience Level")
        experience_levels = list(set([r['candidate_profile'].get('experience_level', 'N/A') 
                                    for r in reports]))
        experience_levels.sort()
        selected_experience = st.multiselect(
            "Filter by experience:", 
            experience_levels, 
            default=experience_levels
        )
        
        # Score range filter
        st.markdown("### Score Range")
        score_range = st.slider(
            "Overall Score Range:",
            0.0, 10.0,
            (0.0, 10.0),
            0.1
        )
        
        # Skill filter
        st.markdown("### Primary Skill")
        all_skills = list(set([r['candidate_profile'].get('primary_skill', 'N/A') 
                              for r in reports]))
        all_skills.sort()
        selected_skills = st.multiselect(
            "Filter by primary skill:",
            all_skills,
            default=all_skills
        )
        
        # Date filter
        st.markdown("### Date Range")
        valid_dates = []
        for r in reports:
            try:
                ts = r.get('timestamp', '')
                if not ts:
                    continue
                    
                if 'Z' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(ts)
                valid_dates.append(dt)
            except Exception:
                continue
        
        if valid_dates:
            min_date = min(valid_dates).date()
            max_date = max(valid_dates).date()
            
            if min_date == max_date:
                selected_date = st.date_input(
                    "Select Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date
                )
                date_range = [selected_date, selected_date]
            else:
                date_range = st.date_input(
                    "Select Date Range",
                    value=[min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
        else:
            date_range = None
        
        st.markdown("---")
        st.markdown(f"**Total Reports:** {len(reports)}")
    
    # Filter reports based on all criteria
    filtered_reports = []
    for report in reports:
        # Status filter
        if selected_status != 'All':
            if report.get('status', '') != selected_status:
                continue
        
        # Experience filter
        exp_level = report['candidate_profile'].get('experience_level', 'N/A')
        if exp_level not in selected_experience:
            continue
        
        # Score filter
        overall_score = report.get('overall_score', 0)
        if not (score_range[0] <= overall_score <= score_range[1]):
            continue
        
        # Skill filter
        skill = report['candidate_profile'].get('primary_skill', 'N/A')
        if skill not in selected_skills:
            continue
        
        # Date filter
        date_match = True
        if date_range and len(date_range) == 2:
            try:
                ts = report.get('timestamp', '')
                if not ts:
                    date_match = True
                else:
                    if 'Z' in ts:
                        report_date = datetime.fromisoformat(ts.replace('Z', '+00:00')).date()
                    else:
                        report_date = datetime.fromisoformat(ts).date()
                    
                    date_match = date_range[0] <= report_date <= date_range[1]
            except:
                date_match = True
        
        if date_match:
            filtered_reports.append(report)
    
    # Display summary metrics
    st.markdown("##Dashboard Overview")
    
    # Calculate status counts
    status_counts = {
        'Selected': len([r for r in filtered_reports if r.get('status') == 'Selected']),
        'Conditional': len([r for r in filtered_reports if r.get('status') == 'Conditional']),
        'Rejected': len([r for r in filtered_reports if r.get('status') == 'Rejected'])
    }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reports", len(reports))
    with col2:
        st.metric("Filtered Reports", status_counts['Selected'])
    with col3:
        if filtered_reports:
            avg_score = sum([r.get('overall_score', 0) for r in filtered_reports]) / len(filtered_reports)
            st.metric("Average Score", f"{avg_score:.2f}/10")
    with col4:
        if filtered_reports:
            avg_questions = sum([len(r.get('question_evaluations', [])) for r in filtered_reports]) / len(filtered_reports)
            st.metric("Avg Questions", f"{avg_questions:.1f}")
    
    # Status distribution
    st.markdown("### Status Distribution")
    status_cols = st.columns(3)
    with status_cols[0]:
        st.markdown(f"""
        <div class='custom-card' style='border-left: 4px solid #10b981;'>
            <h3 style='color: #10b981; margin: 0;'>{status_counts['Selected']}</h3>
            <p style='color: #64748b; margin: 0;'>Selected</p>
        </div>
        """, unsafe_allow_html=True)
    with status_cols[1]:
        st.markdown(f"""
        <div class='custom-card' style='border-left: 4px solid #f59e0b;'>
            <h3 style='color: #f59e0b; margin: 0;'>{status_counts['Conditional']}</h3>
            <p style='color: #64748b; margin: 0;'>Conditional</p>
        </div>
        """, unsafe_allow_html=True)
    with status_cols[2]:
        st.markdown(f"""
        <div class='custom-card' style='border-left: 4px solid #ef4444;'>
            <h3 style='color: #ef4444; margin: 0;'>{status_counts['Rejected']}</h3>
            <p style='color: #64748b; margin: 0;'>Rejected</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display filtered reports
    st.markdown("---")
    st.markdown(f"## 📋 Detailed Reports ({len(filtered_reports)} found)")
    
    if not filtered_reports:
        st.info("No reports match the selected filters.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["🔍 Detailed View", "Summary Analytics"])
    
    with tab1:
        # Display each report in an expander
        for i, report in enumerate(filtered_reports):
            status = report.get('status', 'Unknown')
            status_color = report.get('status_color', 'default')
            
            with st.expander(
                f"{report.get('display_date_short', 'N/A')} | "
                f"Score: {report.get('overall_score', 0):.1f}/10 | "
                f"Status: {status} | "
                f"Exp: {report['candidate_profile'].get('experience_level', 'N/A')}",
                expanded=False
            ):
                
                # Basic info in columns with status badge
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    profile = report['candidate_profile']
                    st.metric("Experience", profile.get('experience_level', 'N/A').title())
                    st.metric("Confidence", profile.get('confidence', 'N/A').title())
                with col2:
                    st.metric("Primary Skill", profile.get('primary_skill', 'N/A').title())
                    st.metric("Communication", profile.get('communication', 'N/A').title())
                with col3:
                    st.metric("Intro Score", f"{profile.get('intro_score', 0)}/10")
                    st.metric("Questions", len(report['question_evaluations']))
                with col4:
                    st.metric("Overall Score", f"{report.get('overall_score', 0):.2f}/10")
                    st.metric("Final Score", f"{report.get('final_score', 0):.2f}/10")
                
                # Status badge
                status_colors = {
                    'Selected': '#10b981',
                    'Conditional': '#f59e0b',
                    'Rejected': '#ef4444'
                }
                status_color = status_colors.get(status, '#64748b')
                st.markdown(f"""
                <div style='background: {status_color}15; border: 1px solid {status_color}; 
                          border-radius: 8px; padding: 0.5rem 1rem; margin: 1rem 0;'>
                    <strong style='color: {status_color};'>Status:</strong> {status}
                </div>
                """, unsafe_allow_html=True)
                
                # Skills
                skills = profile.get("skills", [])
                if skills:
                    st.write("**Skills:**")
                    skill_chips = " ".join([f"<span style='background: #e2e8f0; padding: 4px 12px; border-radius: 16px; margin: 2px; display: inline-block;'>{skill}</span>" 
                                           for skill in skills])
                    st.markdown(skill_chips, unsafe_allow_html=True)
                
                # Charts
                st.markdown("---")
                st.subheader("📈 Performance Visualization")
                fig = create_score_chart(report, chart_id=f"report_{i+1}")
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_main_{i}")
                else:
                    st.info("No question data available for visualization.")
                
                # Detailed question analysis
                st.markdown("---")
                st.subheader("📝 Question Analysis")
                evaluations = report.get('question_evaluations', [])
                for j, eval_data in enumerate(evaluations):
                    with st.expander(f"Question {j+1}: {eval_data['question'][:50]}...", expanded=False):
                        evaluation = eval_data['evaluation']
                        
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**Question:** {eval_data['question']}")
                            st.write(f"**Answer:** {eval_data['answer']}")
                        with col_b:
                            score = evaluation.get('overall', 0)
                            st.metric("Score", f"{score}/10")
                        
                        # Category scores
                        st.write("**Category Scores:**")
                        categories = [
                            ("Technical Accuracy", "technical_accuracy"),
                            ("Completeness", "completeness"),
                            ("Clarity", "clarity"),
                            ("Depth", "depth"),
                            ("Practicality", "practicality")
                        ]
                        
                        cat_cols = st.columns(5)
                        for idx, (label, key) in enumerate(categories):
                            with cat_cols[idx]:
                                cat_score = evaluation.get(key, 0)
                                st.metric(label, f"{cat_score}/10")
                        
                        # Strengths and weaknesses
                        col_x, col_y = st.columns(2)
                        with col_x:
                            if evaluation.get('strengths'):
                                st.write("**Strengths:**")
                                for strength in evaluation['strengths']:
                                    st.success(f"✓ {strength}")
                        
                        with col_y:
                            if evaluation.get('weaknesses'):
                                st.write("**Areas for Improvement:**")
                                for weakness in evaluation['weaknesses']:
                                    st.error(f"✗ {weakness}")
                
                # Download buttons
                st.markdown("---")
                st.write("**Download Reports:**")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    # JSON download
                    json_str = json.dumps(report, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=report['filename'],
                        mime="application/json",
                        key=f"json_{i}"
                    )
                
                with col_d2:
                    # Generate text report on the fly
                    text_report = generate_readable_report_locally(report)
                    txt_filename = report['filename'].replace('.json', '.txt')
                    st.download_button(
                        label="📥 Generate Text Report",
                        data=text_report,
                        file_name=txt_filename,
                        mime="text/plain",
                        key=f"text_{i}"
                    )
    
    with tab2:
        # Summary statistics across all filtered reports
        st.subheader("Summary Analytics")
        
        if filtered_reports:
            # Create summary DataFrame
            summary_data = []
            for report in filtered_reports:
                profile = report['candidate_profile']
                overall_score = report.get('overall_score', 0)
                
                summary_data.append({
                    'Date': report.get('display_date_short', 'N/A'),
                    'Status': report.get('status', 'Unknown'),
                    'Experience': profile.get('experience_level', 'N/A'),
                    'Primary Skill': profile.get('primary_skill', 'N/A'),
                    'Overall Score': report.get('overall_score', 0),
                    'Intro Score': profile.get('intro_score', 0),
                    'Questions': len(report.get('question_evaluations', [])),
                })
            
            df = pd.DataFrame(summary_data)
            
            # Display DataFrame with styling
            st.dataframe(
                df.style.applymap(
                    lambda x: 'color: #10b981' if x == 'Selected' else 
                             ('color: #f59e0b' if x == 'Conditional' else 
                             ('color: #ef4444' if x == 'Rejected' else 'color: #64748b')),
                    subset=['Status']
                ),
                use_container_width=True
            )
            
            # Statistics in columns
            st.subheader("📈 Key Statistics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                # Score statistics
                scores = df['Overall Score'].tolist()
                if scores:
                    st.markdown("**Score Analysis**")
                    st.metric("Average Score", f"{np.mean(scores):.2f}/10")
                    st.metric("Median Score", f"{np.median(scores):.2f}/10")
                    st.metric("Score Range", f"{max(scores) - min(scores):.2f}")
            
            with col2:
                # Status distribution
                st.markdown("**Status Distribution**")
                status_counts = df['Status'].value_counts()
                for status, count in status_counts.items():
                    color = "#10b981" if status == "Selected" else "#f59e0b" if status == "Conditional" else "#ef4444"
                    st.markdown(f"<div style='color: {color}; font-weight: 500;'>{status}: {count}</div>", 
                               unsafe_allow_html=True)
            
            with col3:
                # Experience distribution
                st.markdown("**Experience Distribution**")
                exp_counts = df['Experience'].value_counts()
                for exp, count in exp_counts.items():
                    st.write(f"**{exp}:** {count}")
            
            # Score distribution chart
            st.subheader("📊 Score Distribution")
            if scores:
                fig = go.Figure(data=[go.Histogram(
                    x=scores, 
                    nbinsx=20, 
                    marker_color='#4f46e5',
                    opacity=0.7
                )])
                fig.update_layout(
                    title="Overall Score Distribution",
                    xaxis_title="Score",
                    yaxis_title="Number of Candidates",
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(color='#334155'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True, key="histogram_chart")
            
            # Status vs Experience heatmap
            st.subheader("Status by Experience Level")
            if not df.empty and 'Experience' in df.columns and 'Status' in df.columns:
                pivot_table = pd.crosstab(df['Experience'], df['Status'])
                if not pivot_table.empty:
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_table.values,
                        x=pivot_table.columns,
                        y=pivot_table.index,
                        colorscale='Viridis',
                        text=pivot_table.values,
                        texttemplate="%{text}",
                        textfont={"size": 14}
                    ))
                    fig.update_layout(
                        title="Candidate Status by Experience Level",
                        xaxis_title="Status",
                        yaxis_title="Experience Level",
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()