import streamlit as st
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Helper Functions
def query_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
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

# Custom UTF-8 Supported PDF
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        self.set_font('DejaVu', '', 12)

    def header(self):
        self.set_font('DejaVu', 'B', 16)
        self.cell(0, 10, 'AI-Generated Diet Plan', 0, 1, 'C')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 12)
        self.multi_cell(0, 10, body)

def generate_pdf(content, filename="diet_plan.pdf"):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_body(content)
    pdf.output(filename)
    return filename

# Streamlit Frontend
st.set_page_config(page_title="Smart AI Diet Planner", page_icon="🥑", layout="centered")
st.title("🥑 Smart AI Diet Planner")

st.write("Generate a customized diet plan with AI 🤖!")

with st.form("user_form"):
    age = st.number_input("Age", 5, 100, 25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 120, 220, 170)
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Healthy Eating", "Maintain Weight"])
    diet_type = st.radio("Choose your diet type:", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    submit = st.form_submit_button("Generate Plan")

if submit:
    with st.spinner("AI is crafting your diet plan... 🍽️"):
        prompt = (
            f"You are an expert nutritionist.\n"
            f"Create a detailed daily {diet_type} diet plan for a {age} year old {gender.lower()} "
            f"who weighs {weight}kg and is {height}cm tall. Their goal is {goal.lower()}.\n\n"
            f"Structure:\n"
            f"- Breakfast\n- Mid-morning Snack\n- Lunch\n- Evening Snack\n- Dinner\n- Hydration Tips\n\n"
            f"Make it simple, practical, and balanced."
        )

        gemini_diet = query_gemini(prompt)

        if "Error" in gemini_diet:
            st.error(gemini_diet)
        else:
            st.markdown("## 🥗 Your AI-Generated Diet Plan:")
            st.markdown(gemini_diet)

            pdf_filename = generate_pdf(gemini_diet)

            with open(pdf_filename, "rb") as file:
                st.download_button(
                    label="📥 Download Diet Plan (PDF)",
                    data=file,
                    file_name="diet_plan.pdf",
                    mime="application/pdf"
                )
