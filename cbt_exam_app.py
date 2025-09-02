import streamlit as st
import json
import os
import time

st.set_page_config(page_title="CBT Practice Test", layout="wide")

# Paths
QUESTION_FOLDER = "questions"
PROGRESS_FILE = "progress.json"

# Sidebar selection for question set
question_files = [f for f in os.listdir(QUESTION_FOLDER) if f.endswith(".json")]
selected_file = st.sidebar.selectbox("Select Question Set", question_files)

# Load questions
def load_questions(file):
    with open(os.path.join(QUESTION_FOLDER, file), "r", encoding="utf-8") as f:
        return json.load(f)

# Save progress
def save_progress():
    progress = {
        "responses": st.session_state.responses,
        "current_question": st.session_state.current_question,
        "start_time": st.session_state.start_time,
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f)

# Load saved progress
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.responses = {}
    st.session_state.current_question = 0
    st.session_state.start_time = time.time()
    st.session_state.questions = load_questions(selected_file)
    st.session_state.test_submitted = False
    st.session_state.expired_at = None

# Reload questions when file changes
if selected_file != st.session_state.get("loaded_file", None):
    st.session_state.questions = load_questions(selected_file)
    st.session_state.responses = {}
    st.session_state.current_question = 0
    st.session_state.start_time = time.time()
    st.session_state.test_submitted = False
    st.session_state.loaded_file = selected_file

# Resume option
saved_progress = load_progress()
if saved_progress and not st.session_state.test_submitted:
    if st.sidebar.button("Resume Last Session"):
        st.session_state.responses = saved_progress["responses"]
        st.session_state.current_question = saved_progress["current_question"]
        st.session_state.start_time = saved_progress["start_time"]

questions = st.session_state.questions
num_questions = len(questions)

def show_question(qnum, q):
    st.markdown(f"### Q{qnum+1}. ({q['section']}) {q['question']}")
    if q.get("passage"):
        with st.expander("Passage"):
            st.write(q["passage"])
    options = q["options"]
    selected = st.radio("Select an option", options, index=options.index(st.session_state.responses[qnum]) if qnum in st.session_state.responses else None, key=f"q_{qnum}")
    st.session_state.responses[qnum] = selected
    save_progress()

# Timer (60 minutes)
elapsed = time.time() - st.session_state.start_time
remaining = max(0, 60*60 - int(elapsed))
mins, secs = divmod(remaining, 60)
st.sidebar.markdown(f"⏳ Time left: {mins:02d}:{secs:02d}")

if remaining == 0 and not st.session_state.test_submitted:
    st.session_state.expired_at = st.session_state.current_question
    st.warning(f"Time is up! You were on Question {st.session_state.expired_at+1}.")

# Navigation buttons
if not st.session_state.test_submitted:
    qnum = st.session_state.current_question
    if qnum < num_questions:
        show_question(qnum, questions[qnum])
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            if st.button("Previous", disabled=qnum==0):
                st.session_state.current_question -= 1
        with col2:
            if st.button("Next", disabled=qnum==num_questions-1):
                st.session_state.current_question += 1
        with col3:
            if st.button("Submit Test"):
                st.session_state.test_submitted = True
                if os.path.exists(PROGRESS_FILE):
                    os.remove(PROGRESS_FILE)
    else:
        st.session_state.test_submitted = True

# After submission
if st.session_state.test_submitted:
    st.success("✅ Test submitted!")
    if st.session_state.expired_at is not None:
        st.warning(f"Test ended due to time running out at Question {st.session_state.expired_at+1}.")
    st.download_button(
        "Download Responses",
        json.dumps(st.session_state.responses, indent=2),
        file_name="responses.json",
        mime="application/json",
    )
