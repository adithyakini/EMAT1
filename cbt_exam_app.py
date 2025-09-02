import streamlit as st
import json
import os
import time
import random

# --------------------
# Load available question sets
# --------------------
def list_question_files():
    return [f for f in os.listdir() if f.endswith(".json")]

# --------------------
# Load questions
# --------------------
def load_questions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------
# Timer management
# --------------------
def start_timer():
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

def get_remaining_time(total_minutes=60):
    elapsed = time.time() - st.session_state.start_time
    remaining = total_minutes * 60 - elapsed
    return max(0, int(remaining))

# --------------------
# Initialize
# --------------------
st.title("📘 IIM EAT / EMAT Practice CBT")

# Sidebar to select question set
question_files = list_question_files()
selected_file = st.sidebar.selectbox("📂 Select Question Set JSON", question_files)

if selected_file:
    questions = load_questions(selected_file)

    # Shuffle only once at start
    if "questions" not in st.session_state:
        st.session_state.questions = random.sample(questions, len(questions))
        st.session_state.responses = {}
        st.session_state.current_q = 0
        st.session_state.start_time = time.time()
        st.session_state.timeout_q = None

    remaining_time = get_remaining_time()

    # Timer display
    st.sidebar.markdown(f"⏳ **Time Left:** {remaining_time // 60}m {remaining_time % 60}s")

    if remaining_time <= 0 and st.session_state.timeout_q is None:
        st.session_state.timeout_q = st.session_state.current_q + 1  # human-readable index

    # --------------------
    # Question Display
    # --------------------
    q = st.session_state.questions[st.session_state.current_q]
    st.markdown(f"### Q{st.session_state.current_q + 1}. ({q['section']}) {q['question']}")

    # Passage display if available
    if "passage" in q and q["passage"]:
        with st.expander("📖 Passage"):
            st.write(q["passage"])

    # Options
    user_answer = st.radio(
        "Select your answer:",
        q["options"],
        index=st.session_state.responses.get(st.session_state.current_q, None)
        if st.session_state.current_q in st.session_state.responses
        else None,
        key=f"q_{st.session_state.current_q}"
    )

    if user_answer:
        st.session_state.responses[st.session_state.current_q] = q["options"].index(user_answer)

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_q == 0):
            st.session_state.current_q -= 1
    with col2:
        if st.button("➡️ Next", disabled=st.session_state.current_q == len(st.session_state.questions) - 1):
            st.session_state.current_q += 1
    with col3:
        if st.button("✅ Submit"):
            score = 0
            for i, q in enumerate(st.session_state.questions):
                if i in st.session_state.responses and q["options"][st.session_state.responses[i]] == q["answer"]:
                    score += 1
            st.success(f"Your Score: {score}/{len(st.session_state.questions)}")

            if st.session_state.timeout_q:
                st.warning(f"⏰ Time ran out while on Question {st.session_state.timeout_q}")

            # Show answers
            with st.expander("📊 Review Answers"):
                for i, q in enumerate(st.session_state.questions):
                    user_ans = q["options"][st.session_state.responses[i]] if i in st.session_state.responses else "Not Answered"
                    st.write(f"Q{i+1}: {q['question']}")
                    st.write(f"Your Answer: {user_ans}")
                    st.write(f"Correct Answer: {q['answer']}")
                    st.write("---")

