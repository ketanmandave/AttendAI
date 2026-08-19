# ON GIT BASH
python -m venv venv
source venv/Scripts/activate

# TO Run sreamlit 
streamlit run app.py

## Rendering:
Use st.markdown() for Markdown/text and very small inline HTML.
Use st.html() when you are writing proper HTML components with <div>, <h1>, <p>, custom layout, etc.
Keep CSS in <style>...</style> and render it with st.html() too if you want to avoid Markdown parsing issues.
If Streamlit suddenly displays your HTML tags as text, suspect the renderer, not your CSS first.