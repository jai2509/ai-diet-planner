import streamlit as st
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Helper Functions
def query_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",  # best available as of now
        "messages": [
            {"role": "system", "content": "You are a professional dietitian."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error from GROQ API: {e}"

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
            f"Make it simple, practical, and easy to follow."
        )

        groq_diet = query_groq(prompt)

        if "Error" in groq_diet:
            st.error(groq_diet)
        else:
            st.markdown("## 🥗 Your AI-Generated Diet Plan:")
            st.markdown(groq_diet)

            pdf_filename = generate_pdf(groq_diet)

            with open(pdf_filename, "rb") as file:
                st.download_button(
                    label="📥 Download Diet Plan (PDF)",
                    data=file,
                    file_name="diet_plan.pdf",
                    mime="application/pdf"
                )
