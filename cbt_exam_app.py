import streamlit as st
import json
import os
import time

st.set_page_config(page_title="CBT Practice App", layout="wide")

# --- Timer settings ---
TOTAL_TIME = 60 * 60  # 60 minutes

# --- Load available JSON files ---
json_files = [f for f in os.listdir() if f.endswith(".json")]

# --- Sidebar selection ---
selected_file = st.sidebar.selectbox("📂 Select Question Set", json_files)

# --- Reset session state if file changes ---
if "selected_file" not in st.session_state or st.session_state.selected_file != selected_file:
    st.session_state.selected_file = selected_file
    if "responses" in st.session_state: del st.session_state["responses"]
    if "start_time" in st.session_state: del st.session_state["start_time"]
    if "current_q" in st.session_state: del st.session_state["current_q"]
    if "time_up_q" in st.session_state: del st.session_state["time_up_q"]

# --- Load questions from JSON ---
with open(selected_file, "r", encoding="utf-8") as f:
    questions = json.load(f)

# --- Initialize state ---
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "time_up_q" not in st.session_state:
    st.session_state.time_up_q = None

# --- Timer ---
elapsed = time.time() - st.session_state.start_time
remaining = TOTAL_TIME - elapsed
mins, secs = divmod(int(remaining), 60)
st.sidebar.write(f"⏳ Time Left: {mins:02d}:{secs:02d}")

# If time is up, mark the current question
if remaining <= 0 and st.session_state.time_up_q is None:
    st.session_state.time_up_q = st.session_state.current_q

# --- Display question ---
q = questions[st.session_state.current_q]
st.write(f"**Q{q['qnum']} ({q['section']})** {q['question']}")

# Paragraph (if present)
if "paragraph" in q and q["paragraph"]:
    with st.expander("📖 Reference Passage", expanded=True):
        st.write(q["paragraph"])

# Options
options = q.get("options", [])
current_answer = st.session_state.responses.get(q["qnum"], None)

choice = st.radio(
    "Select an option:",
    options,
    index=options.index(current_answer) if current_answer in options else None,
    key=f"q_{q['qnum']}"
)

if choice:
    st.session_state.responses[q["qnum"]] = choice

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.session_state.current_q > 0 and st.button("⬅️ Previous"):
        st.session_state.current_q -= 1
with col2:
    if st.session_state.current_q < len(questions) - 1 and st.button("Next ➡️"):
        st.session_state.current_q += 1

# Submit
if st.button("✅ END and Submit Test"):
    st.write("### 📊 Your Responses")
    st.json(st.session_state.responses)

    if st.session_state.time_up_q is not None:
        st.warning(f"⏰ Time ran out while you were on Question {st.session_state.time_up_q + 1}")
