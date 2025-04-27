import streamlit as st
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Helper Functions
def query_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1500
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error from Groq API: {e}"

def query_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"Error from Gemini API: {e}"

def generate_pdf(content, filename="diet_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    return filename

# Streamlit Frontend
st.set_page_config(page_title="Smart AI Diet Planner", page_icon="🥑", layout="centered")
st.title("🥑 Smart AI Diet Planner")
st.write("Generate a customized diet plan using cutting-edge AI models!")

with st.form("user_form"):
    age = st.number_input("Age", 5, 100, 25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 120, 220, 170)
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Healthy Eating", "Maintain Weight"])
    submit = st.form_submit_button("Generate Plan")

if submit:
    with st.spinner("AI is crafting your diet plan... 🍽️"):
        prompt = (
            f"You are a certified nutritionist.\n\n"
            f"Create a detailed daily diet plan for a {age} year old {gender.lower()} who weighs {weight}kg "
            f"and is {height}cm tall. Their goal is {goal.lower()}.\n\n"
            f"Please include:\n"
            f"- Breakfast\n- Mid-morning Snack\n- Lunch\n- Evening Snack\n- Dinner\n- Hydration Tips\n"
            f"Make it easy to follow and balanced."
        )

        groq_diet = query_groq(prompt)
        gemini_diet = query_gemini(prompt)

        final_output = f"""---
### 🍏 Diet Plan Option 1:
{groq_diet}

---
### 🥗 Diet Plan Option 2:
{gemini_diet}
"""

        st.markdown(final_output)

        pdf_filename = generate_pdf(final_output)

        with open(pdf_filename, "rb") as file:
            st.download_button(
                label="📥 Download Diet Plan (PDF)",
                data=file,
                file_name="diet_plan.pdf",
                mime="application/pdf"
            )
