import streamlit as st
import json
import os
import time
import io

# ---------- Utility Functions ----------
def load_questions(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_progress(progress_file, state):
    with open(progress_file, 'w') as f:
        json.dump(state, f)

def load_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {}

# ---------- App ----------
st.set_page_config(page_title="EAT Mock Test", layout="wide")

# File paths
questions_file = "eat_questions.json"
progress_file = "progress.json"

# Load questions
questions = load_questions(questions_file)

# Sections
sections = sorted(set(q['section'] for q in questions))
section_map = {sec: [q for q in questions if q['section'] == sec] for sec in sections}

# Initialize session state
if "current_section" not in st.session_state:
    st.session_state.current_section = sections[0]
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Timer (60 mins = 3600s)
time_limit = 3600
elapsed = int(time.time() - st.session_state.start_time)
remaining = time_limit - elapsed

if remaining <= 0 and not st.session_state.submitted:
    st.session_state.submitted = True
    st.warning("⏰ Time is up! Your test has been auto-submitted.")

mins, secs = divmod(max(0, remaining), 60)
st.sidebar.metric("Time Left", f"{mins:02d}:{secs:02d}")

# Sidebar - Section navigation
st.sidebar.title("Sections")
for sec in sections:
    if st.sidebar.button(sec):
        st.session_state.current_section = sec
        st.session_state.current_q_index = 0

# Sidebar - Question palette
st.sidebar.title("Question Palette")
for idx, q in enumerate(section_map[st.session_state.current_section]):
    qnum = q['qnum']
    answered = str(qnum) in st.session_state.answers
    color = "🟢" if answered else "⚪"
    if st.sidebar.button(f"{color} Q{qnum}"):
        st.session_state.current_q_index = idx

# Main area
st.title("EAT Mock Test – IIM Indore")

if not st.session_state.submitted:
    current_q = section_map[st.session_state.current_section][st.session_state.current_q_index]
    st.subheader(f"Q{current_q['qnum']} ({current_q['section']})")

    # Show passage if present
    if "passage" in current_q and current_q["passage"]:
        st.markdown(f"**Passage:**\n\n{current_q['passage']}")

    # Show question
    st.write(current_q["question"])
    options = current_q["options"]

    # Preserve answers
    saved_answer = st.session_state.answers.get(str(current_q["qnum"]))
    choice = st.radio(
        "Select an option:",
        options,
        index=saved_answer if saved_answer is not None else -1,
        key=f"q_{current_q['qnum']}"
    )

    if choice:
        st.session_state.answers[str(current_q["qnum"])] = options.index(choice)

    # Navigation
    cols = st.columns(3)
    if cols[0].button("⬅ Prev"):
        if st.session_state.current_q_index > 0:
            st.session_state.current_q_index -= 1
    if cols[1].button("➡ Next"):
        if st.session_state.current_q_index < len(section_map[st.session_state.current_section]) - 1:
            st.session_state.current_q_index += 1
    if cols[2].button("Submit Test"):
        st.session_state.submitted = True

else:
    # Results
    st.success("✅ Test Submitted")
    score = 0
    total = len(questions)
    results = []

    for q in questions:
        qnum = str(q['qnum'])
        ans = st.session_state.answers.get(qnum, None)
        correct = q['answer']
        explanation = q.get('explanation', '')

        if ans == correct:
            score += 1

        results.append({
            "qnum": q['qnum'],
            "question": q['question'],
            "your_answer": options[ans] if ans is not None else None,
            "correct_answer": options[correct],
            "explanation": explanation
        })

    st.metric("Final Score", f"{score}/{total}")

    # Show answers
    for r in results:
        st.markdown(f"**Q{r['qnum']}: {r['question']}**")
        st.write(f"Your Answer: {r['your_answer']}")
        st.write(f"Correct Answer: {r['correct_answer']}")
        st.info(f"Explanation: {r['explanation']}")

    # Download responses
    buf = io.StringIO()
    json.dump(st.session_state.answers, buf)
    st.download_button(
        "⬇ Download Responses (JSON)",
        buf.getvalue(),
        file_name="responses.json",
        mime="application/json"
    )
