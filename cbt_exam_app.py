import streamlit as st
import json, os, time

HERE = os.path.dirname(__file__)

# 🔑 Add your question sets here
QUESTION_FILES = {
    "Set 1": "questions.json",
    "Set 2": "questions_set2.json",
    "Set 6": "questions_set6.json"
}

# --- Sidebar select which set ---
st.sidebar.title("IIM Indore Mock CBT")
selected_set = st.sidebar.selectbox("Choose Question Set", list(QUESTION_FILES.keys()))

# Load questions
with open(os.path.join(HERE, QUESTION_FILES[selected_set]), "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

TOTAL_TIME_MIN = 60
st.set_page_config(page_title="IIM Indore Mock CBT", layout="wide")

def sidebar_controls():
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

section_choice, timer_on, show_answers_after = sidebar_controls()
questions = get_questions(section_choice)

st.title(f"IIM Indore — 60-question Mock CBT ({selected_set})")
st.write("Format: 60 questions (20 Quant, 20 Analytical, 20 Verbal). 60 minutes recommended. Navigate with Previous/Next. Submit when done.")

# --- Timer ---
if timer_on:
    if 'end_time' not in st.session_state or st.session_state.get('set_name') != selected_set:
        st.session_state['end_time'] = time.time() + TOTAL_TIME_MIN*60
        st.session_state['set_name'] = selected_set
    remaining = int(st.session_state['end_time'] - time.time())
    if remaining < 0:
        st.error("Time is up! Please submit your test.")
    else:
        mins = remaining // 60
        secs = remaining % 60
        st.sidebar.markdown(f"**Time remaining:** {mins:02d}:{secs:02d}")

# --- Navigation states ---
if 'index' not in st.session_state or st.session_state.get('set_name') != selected_set:
    st.session_state.index = 0
    st.session_state.answers = {str(q['qnum']): None for q in QUESTIONS}
    st.session_state.submitted = False
    st.session_state['set_name'] = selected_set

cols = st.columns([1,6,1])
with cols[0]:
    if st.button("Previous"):
        st.session_state.index = max(0, st.session_state.index - 1)
with cols[2]:
    if st.button("Next"):
        st.session_state.index = min(len(questions)-1, st.session_state.index + 1)

current_q = questions[st.session_state.index]
st.markdown(f"### {format_question(current_q)}")

options = current_q['options']
key = f"q_{current_q['qnum']}_{selected_set}"
default_index = 0 if st.session_state['answers'].get(str(current_q['qnum'])) is None else st.session_state['answers'][str(current_q['qnum'])]
choice = st.radio("Select an option", options, index=default_index, key=key)
selected_index = options.index(choice)
st.session_state['answers'][str(current_q['qnum'])] = selected_index

st.progress((st.session_state.index+1)/len(questions))

# --- Question palette ---
if st.checkbox("Show question palette"):
    cols = st.columns(10)
    for i, q in enumerate(questions):
        btn = cols[i%10].button(str(q['qnum']))
        if btn:
            st.session_state.index = i

# --- Submit ---
if st.button("Complete and Submit Test"):
    st.session_state.submitted = True

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

# --- Download responses ---
if st.button('Download Responses (JSON)'):
    import io, json
    buf = io.StringIO()
    json.dump(st.session_state['answers'], buf)
    st.download_button('Click to download responses JSON', buf.getvalue(), file_name=f'responses_{selected_set}.json')
