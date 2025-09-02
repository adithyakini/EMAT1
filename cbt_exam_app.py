import streamlit as st
import json, os, time, io

# ---------- Load Questions ----------
HERE = os.path.dirname(__file__)
with open(os.path.join(HERE, "questions.json"), "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

TOTAL_TIME_MIN = 60

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="IIM Indore Mock CBT", layout="wide")

# ---------- Sidebar Controls ----------
def sidebar_controls():
    st.sidebar.title("IIM Indore Mock CBT")
    sections = sorted(list(set(q['section'] for q in QUESTIONS)))
    choice = st.sidebar.selectbox("Jump to section", ["All"] + sections)
    timer_on = st.sidebar.checkbox("Enable 60-min timer", value=True)
    show_answers_after = st.sidebar.checkbox("Show answers after submission", value=True)
    return choice, timer_on, show_answers_after

def get_questions(filtered_section):
    if filtered_section == "All":
        return QUESTIONS
    return [q for q in QUESTIONS if q['section'] == filtered_section]

def format_question(q):
    prompt = f"Q{q['qnum']}. ({q['section']}) {q['question']}"
    return prompt

# ---------- Main App ----------
section_choice, timer_on, show_answers_after = sidebar_controls()
questions = get_questions(section_choice)

st.title("IIM Indore — 60-question Mock CBT")
st.write("Format: 60 questions (20 Quant, 20 Analytical, 20 Verbal). 60 minutes recommended. Navigate with Previous/Next. Submit when done.")

# Timer
if timer_on:
    if 'end_time' not in st.session_state:
        st.session_state['end_time'] = time.time() + TOTAL_TIME_MIN*60
    remaining = int(st.session_state['end_time'] - time.time())
    if remaining < 0:
        st.error("Time is up! Please submit your test.")
    else:
        mins = remaining // 60
        secs = remaining % 60
        st.sidebar.markdown(f"**Time remaining:** {mins:02d}:{secs:02d}")

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {str(q['qnum']): None for q in QUESTIONS}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Navigation buttons
cols = st.columns([1,6,1])
with cols[0]:
    if st.button("Previous"):
        st.session_state.index = max(0, st.session_state.index - 1)
with cols[2]:
    if st.button("Next"):
        st.session_state.index = min(len(questions)-1, st.session_state.index + 1)

# Current question
current_q = questions[st.session_state.index]

# Show passage if provided
if "passage" in current_q and current_q["passage"]:
    st.markdown("#### Passage")
    st.info(current_q["passage"])

st.markdown(f"### {format_question(current_q)}")

options = current_q['options']
key = f"q_{current_q['qnum']}"
saved_ans = st.session_state['answers'].get(str(current_q['qnum']))
default_index = options.index(options[saved_ans]) if saved_ans is not None else 0
choice = st.radio("Select an option", options, index=default_index, key=key)
selected_index = options.index(choice)
st.session_state['answers'][str(current_q['qnum'])] = selected_index

# Progress bar
st.progress((st.session_state.index+1)/len(questions))

# Question palette
if st.checkbox("Show question palette"):
    cols = st.columns(10)
    for i, q in enumerate(questions):
        btn = cols[i%10].button(str(q['qnum']))
        if btn:
            st.session_state.index = i

# Submit button
if st.button("Complete and Submit Test"):
    st.session_state.submitted = True

# Results
if st.session_state.submitted:
    total = 0
    attempted = 0
    wrong = 0
    explanations = []
    for q in QUESTIONS:
        ans = st.session_state['answers'].get(str(q['qnum']))
        if ans is not None:
            attempted += 1
            if q['answer'] is not None and ans == q['answer']:
                total += 1
            else:
                wrong += 1
        explanations.append((q, ans, q['answer']))
    st.success(f"Score: {total} / {len(QUESTIONS)} | Attempted: {attempted} | Wrong: {wrong}")

    if show_answers_after:
        st.markdown("---")
        st.markdown("## Answer key & Explanations")
        for q, user_ans, correct_ans in explanations:
            st.markdown(f"**Q{q['qnum']}. {q['question']}**")
            for idx, opt in enumerate(q['options']):
                prefix = '✅' if correct_ans is not None and idx == correct_ans else ('➡️' if user_ans==idx and user_ans!=correct_ans else '  ')
                st.write(f"{prefix} {chr(65+idx)}. {opt}")
            st.write(f"**Explanation:** {q.get('explanation','-')}")
            st.markdown("---")

# Download responses
if st.button('Download Responses (JSON)'):
    buf = io.StringIO()
    json.dump(st.session_state['answers'], buf)
    st.download_button('Click to download responses JSON', buf.getvalue(), file_name='responses.json')
