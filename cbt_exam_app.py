import streamlit as st
import json
import os
import time

# ---------- Utility Functions ----------
def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_progress(progress_file, state):
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(state, f)

def load_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# ---------- Main App ----------
QUESTION_DIR = "./question_sets"
PROGRESS_FILE = "progress.json"

st.title("📘 EAT Practice CBT")

# Sidebar: choose question set
question_files = [f for f in os.listdir(QUESTION_DIR) if f.endswith(".json")]
selected_file = st.sidebar.selectbox("Select Question Set", question_files)

# Load selected question set
questions = load_questions(os.path.join(QUESTION_DIR, selected_file))

# Session state initialization
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_qnum" not in st.session_state:
    st.session_state.current_qnum = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "time_limit" not in st.session_state:
    st.session_state.time_limit = 60 * 60  # 60 minutes
if "time_up" not in st.session_state:
    st.session_state.time_up = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Resume last session button
progress = load_progress(PROGRESS_FILE)
if progress and st.button("Resume Last Session"):
    st.session_state.current_qnum = progress.get("current_qnum", 0)
    st.session_state.responses = progress.get("responses", {})
    st.session_state.start_time = time.time() - progress.get("elapsed", 0)

# Start button
if st.session_state.start_time is None and not st.session_state.submitted:
    if st.button("Start Test"):
        st.session_state.start_time = time.time()
else:
    if not st.session_state.submitted:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = st.session_state.time_limit - elapsed
        if remaining <= 0:
            st.session_state.time_up = True
            st.warning(f"⏰ Time is up! You were on Question {st.session_state.current_qnum + 1}.")
        else:
            mins, secs = divmod(remaining, 60)
            st.sidebar.write(f"Time Left: {mins:02d}:{secs:02d}")

    # Show current question if test ongoing
    if not st.session_state.time_up and not st.session_state.submitted:
        qnum = st.session_state.current_qnum
        if 0 <= qnum < len(questions):
            q = questions[qnum]

            st.subheader(f"Question {qnum+1}: ({q['section']})")
            st.write(q.get("prompt", q.get("question", "")))

            options = q["options"]
            saved_response = st.session_state.responses.get(qnum)

            try:
                default_index = options.index(saved_response) if saved_response else 0
            except ValueError:
                default_index = 0

            selected = st.radio("Select an option", options, index=default_index, key=f"q_{qnum}")
            st.session_state.responses[qnum] = selected

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Previous", disabled=qnum == 0):
                    st.session_state.current_qnum -= 1
            with col2:
                if st.button("Save & Next", disabled=qnum == len(questions)-1):
                    st.session_state.current_qnum += 1
            with col3:
                if st.button("Submit Test"):
                    st.session_state.submitted = True
                    st.success("✅ Test Submitted!")

            # Save progress continuously
            progress_state = {
                "current_qnum": st.session_state.current_qnum,
                "responses": st.session_state.responses,
                "elapsed": elapsed
            }
            save_progress(PROGRESS_FILE, progress_state)
        else:
            st.error("Invalid question number.")

# If submitted, show summary instead of questions
if st.session_state.submitted:
    st.header("📊 Test Summary")
    st.write("Your Responses:", st.session_state.responses)
