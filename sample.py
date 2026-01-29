import streamlit as st
import os
import json
from datetime import datetime

from response_analyzer import ResponseAnalyzer
from report_manager import ReportManager
from question_generator import QuestionGenerator
from skill_mapper import map_skills_to_category

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Virtual HR Interviewer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS (RESTORED)
# =========================================================

css = """
<style>
.stApp {
    background: #0f172a;
    color: #e5e7eb;
}
.stButton button {
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}
.stButton button:hover {
    opacity: 0.9;
}
.stTextArea textarea {
    background: #020617;
    color: white;
    border-radius: 10px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# =========================================================
# INITIALIZATION
# =========================================================

analyzer = ResponseAnalyzer()
question_generator = QuestionGenerator()
report_manager = ReportManager()

# =========================================================
# SESSION STATE
# =========================================================

def init_session_state():
    defaults = {
        "interview_started": False,
        "interview_active": False,
        "interview_completed": False,

        "current_question_index": 0,
        "questions": [],
        "questions_generated": False,

        "messages": [],
        "candidate_profile": {},
        "question_evaluations": [],

        "overall_score": 0,
        "introduction_analyzed": False,
        "current_response": "",

        "total_questions_to_ask": 5
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# =========================================================
# QUESTION FLOW
# =========================================================

def get_next_question():
    # Q1 always intro
    if not st.session_state.introduction_analyzed:
        return question_generator.generate_general_intro_question()

    idx = st.session_state.current_question_index - 1
    if idx < len(st.session_state.questions):
        return st.session_state.questions[idx]

    return None

# =========================================================
# RESPONSE PROCESSING
# =========================================================

def process_response(response_text: str):

    if not response_text.strip():
        st.warning("Please enter a response.")
        return

    # Save candidate message
    st.session_state.messages.append({
        "role": "candidate",
        "content": response_text,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # -----------------------------------------------------
    # INTRO RESPONSE
    # -----------------------------------------------------
    if st.session_state.current_question_index == 0:

        analysis = analyzer.analyze_introduction(response_text)
        detected_skills = analysis.get("skills", [])

        primary_skill = map_skills_to_category(detected_skills)

        st.session_state.candidate_profile = {
            "skills": detected_skills,
            "experience_level": analysis.get("experience", "mid"),
            "primary_skill": primary_skill,
            "confidence": analysis.get("confidence", "medium"),
            "communication": analysis.get("communication", "adequate"),
            "intro_score": analysis.get("intro_score", 6)
        }

        # Generate questions ONCE
        technical_questions = question_generator.generate_initial_skill_questions(
            skill_category=primary_skill,
            candidate_level=st.session_state.candidate_profile["experience_level"]
        )

        behavioral_question = question_generator.generate_behavioral_question_ai(
            candidate_background=st.session_state.candidate_profile
        )

        st.session_state.questions = (
            technical_questions[:st.session_state.total_questions_to_ask - 1]
            + [behavioral_question]
        )

        st.session_state.introduction_analyzed = True
        st.session_state.questions_generated = True
        st.session_state.current_question_index = 1

        st.session_state.messages.append({
            "role": "system",
            "content": f"✅ Skill identified as **{primary_skill.upper()}**. Interview questions locked.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        st.session_state.current_response = ""
        st.rerun()
        return

    # -----------------------------------------------------
    # TECHNICAL / BEHAVIORAL QUESTIONS
    # -----------------------------------------------------
    current_question = st.session_state.questions[
        st.session_state.current_question_index - 1
    ]

    evaluation = analyzer.evaluate_answer(current_question, response_text)

    st.session_state.question_evaluations.append({
        "question": current_question,
        "answer": response_text,
        "evaluation": evaluation,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    scores = [q["evaluation"]["overall"] for q in st.session_state.question_evaluations]
    st.session_state.overall_score = sum(scores) / len(scores)

    if st.session_state.current_question_index < len(st.session_state.questions):
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

# =========================================================
# UI
# =========================================================

def show_interview():

    if not st.session_state.interview_started:
        st.title("Virtual HR Interviewer")
        st.subheader("AI-powered technical & behavioral screening")
        if st.button("🚀 Start Interview"):
            st.session_state.interview_started = True
            st.session_state.interview_active = True
            st.rerun()
        return

    if st.session_state.interview_completed:
        st.success("Interview completed successfully!")
        st.metric("Overall Score", f"{st.session_state.overall_score:.1f}/10")
        return

    question = get_next_question()
    st.info(f"**Current Question:** {question}")

    response = st.text_area(
        "Your Response",
        value=st.session_state.current_response,
        height=180
    )

    st.session_state.current_response = response

    if st.button("📤 Submit Response"):
        process_response(response)

    # Conversation history
    st.markdown("---")
    st.subheader("Conversation History")

    for msg in st.session_state.messages:
        if msg["role"] == "candidate":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**System:** {msg['content']}")

# =========================================================
# REPORT
# =========================================================

def save_interview_report():
    os.makedirs("interview_reports", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    report = {
        "candidate_profile": st.session_state.candidate_profile,
        "questions": st.session_state.questions,
        "answers": st.session_state.question_evaluations,
        "overall_score": st.session_state.overall_score
    }

    with open(f"interview_reports/report_{ts}.json", "w") as f:
        json.dump(report, f, indent=2)

# =========================================================
# MAIN
# =========================================================

def main():
    show_interview()

if __name__ == "__main__":
    main()
