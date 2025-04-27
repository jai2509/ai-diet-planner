import streamlit as st
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Helper functions
def query_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Failed to generate diet plan."

def query_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return "Failed to generate diet plan."

def generate_pdf(content, filename="diet_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    lines = content.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    return filename

# Streamlit App
st.set_page_config(page_title="AI Diet Planner", page_icon="🥑", layout="centered")

st.title("🥑 AI-Based Diet Planner")
st.write("Get your personalized diet plan powered by AI!")

with st.form("diet_form"):
    age = st.number_input("Age", min_value=5, max_value=100, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", min_value=20, max_value=200, value=70)
    height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
    goal = st.selectbox("Health Goal", ["Weight Loss", "Muscle Gain", "Healthy Eating", "Maintain Weight"])
    submit = st.form_submit_button("Generate Diet Plan")

if submit:
    with st.spinner('Generating your personalized diet plan...'):
        user_prompt = f"""
        Create a detailed {goal.lower()} diet plan for a {age}-year-old {gender.lower()}.
        Weight: {weight}kg, Height: {height}cm.
        The plan should include breakfast, lunch, dinner, snacks, and hydration advice.
        """
        groq_response = query_groq(user_prompt)
        gemini_response = query_gemini(user_prompt)
        
        final_plan = f"---\n## Diet Plan from GROQ Model:\n{groq_response}\n\n---\n## Diet Plan from Gemini Model:\n{gemini_response}"
        
        st.markdown(final_plan)

        # Generate PDF
        pdf_filename = generate_pdf(final_plan)
        
        with open(pdf_filename, "rb") as file:
            st.download_button(
                label="📄 Download Diet Plan as PDF",
                data=file,
                file_name="diet_plan.pdf",
                mime="application/pdf"
            )
