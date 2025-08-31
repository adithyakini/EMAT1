IIM Indore Mock CBT (Streamlit app)

Files:
- cbt_app.py : Streamlit single-file application
- questions.json : Questions & answers JSON

To run locally:
1. Install streamlit: pip install streamlit
2. Navigate to the folder and run: streamlit run cbt_app.py
3. The app launches in your browser. The app has a 60-minute timer (toggleable). Submit to see score and explanations.

Notes:
- Some original questions had mismatched MCQ options; in such cases the answer is provided as None and explanation explains the correct value.
- The app stores responses in session; you can download them as JSON.
