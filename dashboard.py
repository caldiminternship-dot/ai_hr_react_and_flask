# dashboard.py - For HR/Reviewer to view interview reports
import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="HR Interview Dashboard",
    layout="wide"
)

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
                    
                    # Parse timestamp for display
                    timestamp_str = report_data.get('timestamp', '')
                    if timestamp_str:
                        try:
                            if 'Z' in timestamp_str:
                                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            else:
                                dt = datetime.fromisoformat(timestamp_str)
                            report_data['display_date'] = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            report_data['display_date'] = timestamp_str
                    
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
    
    # 1. Pie chart for score distribution
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
               marker_colors=['#00cc96', '#ffa15a', '#ef553b', '#636efa'],
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
            go.Bar(x=categories, y=category_scores, marker_color='#636efa',
                   text=[f'{score:.1f}' for score in category_scores],
                   textposition='auto',
                   name=f"bar_{chart_id}"),
            row=1, col=2
        )
    
    # 3. Line chart for score trend
    question_numbers = list(range(1, len(question_scores) + 1))
    fig.add_trace(
        go.Scatter(x=question_numbers, y=question_scores, mode='lines+markers',
                   name=f'line_{chart_id}', line=dict(color='#ff7f0e', width=3)),
        row=2, col=1
    )
    
    # Add average line
    if question_scores:
        avg_line = [sum(question_scores)/len(question_scores)] * len(question_numbers)
        fig.add_trace(
            go.Scatter(x=question_numbers, y=avg_line, mode='lines',
                       name=f'avg_{chart_id}', line=dict(color='#2ca02c', width=2, dash='dash')),
            row=2, col=1
        )
    
    # 4. Box plot for score distribution
    if question_scores:
        fig.add_trace(
            go.Box(y=question_scores, name=f'box_{chart_id}', 
                   marker_color='#2ca02c', boxmean=True),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800, 
        showlegend=False, 
        title_text=f"Candidate Performance Analysis - {chart_id}",
        title_x=0.5
    )
    return fig

def generate_readable_report_locally(report_data: dict) -> str:
    """Generate a human-readable text report locally (without importing from app.py)"""
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

def main():
    st.title("HR Interview Dashboard")
    st.markdown("Analyze candidate interview results")
    
    # Load reports
    reports = load_reports()
    
    if not reports:
        st.info("No interview reports found. Run some interviews first.")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Experience filter
        experience_levels = list(set([r['candidate_profile'].get('experience_level', 'N/A') 
                                    for r in reports]))
        selected_experience = st.multiselect(
            "Experience Level", 
            experience_levels, 
            default=experience_levels
        )
        
        # Score range filter - FIXED VERSION
        scores = [r.get('overall_score', 0) for r in reports]
 
        # Always use 0-10 range for consistency
        score_range = st.slider(
            "Overall Score Range",
            0.0,  # Min value
            10.0, # Max value
            (6.5, 10.0),  # CHANGED: Set default to >= 6.5
            0.1   # Step
        )

        show_rejected = st.checkbox("Include rejected candidates", value=False)
        
        # Date filter with better error handling
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
            except Exception as e:
                # Skip reports with invalid timestamps
                continue
        
        if valid_dates:
            min_date = min(valid_dates).date()
            max_date = max(valid_dates).date()
            
            # Check if dates are the same
            if min_date == max_date:
                # If only one date, show a date picker instead of range
                selected_date = st.date_input(
                    "Select Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date
                )
                date_range = [selected_date, selected_date]
            else:
                date_range = st.date_input(
                    "Date Range",
                    value=[min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
        else:
            date_range = None
    
    # Filter reports
    filtered_reports = []
    for report in reports:
        # Experience filter
        exp_level = report['candidate_profile'].get('experience_level', 'N/A')
        
        # Score filter
        overall_score = report.get('overall_score', 0)
        
        # NEW LOGIC: Apply show_rejected setting
        if not show_rejected:
            # When checkbox is unchecked, enforce minimum 6.5 threshold
            if overall_score < 6.5:
                continue  # Skip this report
        
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
        
        # Apply all filters
        if (exp_level in selected_experience and
            score_range[0] <= overall_score <= score_range[1] and
            date_match):
            filtered_reports.append(report)
    
    # Display summary
    st.subheader(f"📈 Interview Reports Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reports", len(reports))
    with col2:
        st.metric("Filtered Reports", len(filtered_reports))
    with col3:
        if reports:
            avg_all = sum([r.get('overall_score', 0) for r in reports]) / len(reports)
            st.metric("Avg Score (All)", f"{avg_all:.2f}/10")
    with col4:
        if filtered_reports:
            avg_filtered = sum([r.get('overall_score', 0) for r in filtered_reports]) / len(filtered_reports)
            st.metric("Avg Score (Filtered)", f"{avg_filtered:.2f}/10")
    
    # Display filtered reports
    st.subheader(f"Detailed Reports ({len(filtered_reports)} found)")
    
    if not filtered_reports:
        st.info("No reports match the selected filters.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Detailed View", "📈 Summary View"])
    
    with tab1:
        # Display each report in an expander
        for i, report in enumerate(filtered_reports):
            with st.expander(
                f"Report {i+1}: {report.get('display_date', report.get('timestamp', 'N/A'))} | "
                f"Score: {report.get('overall_score', 0):.1f}/10 | "
                f"Exp: {report['candidate_profile'].get('experience_level', 'N/A')}",
                expanded=False
            ):
                
                # Basic info in columns
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
                
                # Skills
                skills = profile.get("skills", [])
                if skills:
                    st.write(f"**Skills:** {', '.join(skills)}")
                
                # Charts
                st.subheader("Performance Visualization")
                fig = create_score_chart(report, chart_id=f"report_{i+1}")

                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_main_{i}")
                else:
                    st.info("No question data available for visualization.")
                
                # Detailed question analysis
                st.subheader("Question Analysis")
                evaluations = report.get('question_evaluations', [])
                for j, eval_data in enumerate(evaluations):
                    with st.expander(f"Q{j+1}: {eval_data['question'][:50]}...", expanded=False):
                        evaluation = eval_data['evaluation']
                        
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**Question:** {eval_data['question']}")
                            st.write(f"**Answer:** {eval_data['answer'][:300]}...")
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
                    # Check if text report exists
                    txt_filename = report['filename'].replace('.json', '.txt')
                    txt_path = os.path.join("interview_reports", txt_filename)
                    if os.path.exists(txt_path):
                        with open(txt_path, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                        st.download_button(
                            label="📥 Download Text Report",
                            data=text_content,
                            file_name=txt_filename,
                            mime="text/plain",
                            key=f"text_{i}"
                        )
                    else:
                        # Generate text report on the fly
                        text_report = generate_readable_report_locally(report)
                        st.download_button(
                            label="📥 Generate & Download Text Report",
                            data=text_report,
                            file_name=txt_filename,
                            mime="text/plain",
                            key=f"text_gen_{i}"
                        )
    
    with tab2:
        # Summary statistics across all filtered reports
        st.subheader("Summary Statistics")
        
        if filtered_reports:
            # Create summary DataFrame
            summary_data = []
            # In the summary_data creation loop, ADD a 'Status' column:
            for report in filtered_reports:
                profile = report['candidate_profile']
                overall_score = report.get('overall_score', 0)
                
                summary_data.append({
                    'Date': report.get('display_date', 'N/A'),
                    'Experience': profile.get('experience_level', 'N/A'),
                    'Primary Skill': profile.get('primary_skill', 'N/A'),
                    'Overall Score': report.get('overall_score', 0),
                    'Status': 'Selected' if overall_score >= 6.5 else 'Rejected',  # NEW COLUMN
                    'Intro Score': profile.get('intro_score', 0),
                    'Questions': len(report.get('question_evaluations', [])),
                    'Confidence': profile.get('confidence', 'N/A'),
                    'Communication': profile.get('communication', 'N/A')
                })
            
            df = pd.DataFrame(summary_data)
            
            # Display DataFrame
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            st.subheader("Key Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # Score distribution
                scores = df['Overall Score'].tolist()
                if scores:
                    st.metric("Average Score", f"{np.mean(scores):.2f}/10")
                    st.metric("Median Score", f"{np.median(scores):.2f}/10")
            
            with col2:
                # Experience distribution
                exp_counts = df['Experience'].value_counts()
                st.write("**Experience Distribution:**")
                for exp, count in exp_counts.items():
                    st.write(f"{exp}: {count}")
            
            with col3:
                # Skill distribution
                skill_counts = df['Primary Skill'].value_counts()
                st.write("**Primary Skill Distribution:**")
                for skill, count in skill_counts.items():
                    st.write(f"{skill}: {count}")

            with col4:  # Or create a new column
                # Status distribution
                status_counts = df['Status'].value_counts()
                st.write("**Selection Status:**")
                for status, count in status_counts.items():
                    color = "green" if "Selected" in status else "red" # type: ignore
                    st.markdown(f"<span style='color:{color}; font-weight:bold'>{status}: {count}</span>", unsafe_allow_html=True)
            
            # Score distribution chart
            st.subheader("Score Distribution Chart")
            if scores:
                fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=20, name=f"histogram_summary")])
                fig.update_layout(
                    title="Overall Score Distribution",
                    xaxis_title="Score",
                    yaxis_title="Count",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, key="histogram_chart")
            else:
                st.info("No score data available for chart.")

if __name__ == "__main__":
    main()

