import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from weasyprint import HTML, CSS
import base64


st.title(" Amri AI-Powered Resume Builder ")
# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- AI Engine setup with LangChain ---
llm = OpenAI(openai_api_key=openai_api_key, temperature=0.7)

prompt_template = """
You are a career coach helping a user build a resume. Given the following information,
generate a professional resume summary and rewrite the work experience using strong, active language.

User's Input:
Name: {full_name}
Job Title: {job_title} at {company} from {start_date} to {end_date}
Responsibilities: {responsibilities}

Instructions:
1. Write a 3-4 sentence professional summary for a resume. Use an implied first person perspective (do not use "I" or "my"), focusing on the candidate’s strengths, achievements, and value to potential employers. Highlight leadership, problem-solving, and industry-specific expertise.
2. Rewrite the responsibilities into 3-5 bullet points using compelling action verbs.
3. Ensure the tone is professional, confident, and tailored to the candidate's role.
4. Avoid generic phrases and focus on specific, impactful language.
5. Do not use numbers or specific metrics.

Generated Content:
"""

prompt = PromptTemplate(
    input_variables=["full_name", "job_title", "company", "start_date", "end_date", "responsibilities"],
    template=prompt_template,
)

chain = LLMChain(llm=llm, prompt=prompt)


template_options = ["Classic", "Modern", "Minimal"]
selected_template = st.selectbox("Choose a Resume Template", template_options)

ats_friendly = st.checkbox("ATS-Friendly Format")

# --- Resume template and PDF generation ---


def generate_resume_html(full_name, email, phone, skills, job_title, company, start_date, end_date, ai_text, selected_template, ats_friendly):
    # Split lines and remove empty lines
    lines = [line.strip() for line in ai_text.strip().splitlines() if line.strip()]
    summary = lines[1] if lines else "Summary not available."
    bullets = lines[3:] if len(lines) > 1 else []

    if ats_friendly:
        style = "body { font-family: Arial, sans-serif; margin: 40px; }"
    else:
        if selected_template == "Modern":
            style = """
           body
        {
           font-family: var(--primary-font);
           background: var(--bg-color);
           color: var(--text-color);
           line-height: 1.6;
           margin: 0;
           padding: 40px; /* Add generous padding around the entire content */
         box-sizing: border-box; /* Modern box model for consistent sizing */
       }
       h1 
       {
          font-weight: 700;
          font-size: clamp(2rem, 5vw, 3rem); /* Responsive font size that scales with viewport */
          color: var(--heading-color);
          margin-bottom: 2rem;
          text-align: center;
       }

            """
        elif selected_template == "Minimal":
            style = """
            body { font-family: 'Courier New', monospace; margin: 40px; }
            h1 { color: #222; }
            """
        else:
            style = """
            body { font-family: sans-serif; margin: 40px; }
            h1, h2 { color: #2c3e50; }
            """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{full_name} - Resume</title>
        <style>{style}</style>
    </head>
    <body>
        <h1>{full_name}</h1>
        <p><strong>Email:</strong> {email} | <strong>Phone:</strong> {phone}</p>
        <h2>Professional Summary</h2>
        <p>{summary}</p>
        <h2>Work Experience</h2>
        <p><strong>{job_title}</strong> at <strong>{company}</strong> ({start_date} - {end_date})</p>
        <ul>
            {''.join(f'<li>{line}</li>' for line in bullets)}
        </ul>
        <h2>Skills</h2>
        <p>{skills}</p>
    </body>
    </html>
    """
    return html_content
def get_pdf_download_link(html_content, filename="resume.pdf"):
    pdf = HTML(string=html_content).write_pdf()
    b64_pdf = base64.b64encode(pdf).decode("utf-8")
    return f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{filename}">Download Resume as PDF</a>'


# --- Streamlit UI ---


with st.expander("Personal Information"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")

with st.expander("Work Experience"):
    job_title = st.text_input("Job Title")
    company = st.text_input("Company")
    start_date = st.text_input("Start Date (e.g., May 2022)")
    end_date = st.text_input("End Date (e.g., Present)")
    responsibilities = st.text_area("Your Key Responsibilities (e.g., Managed a team, Developed software...)")

with st.expander("Skills"):
    skills = st.text_area("List your skills (comma-separated, e.g., Python, SQL, Project Management)")

if st.button("Generate Resume"):
    if not all([full_name, email, job_title, company, responsibilities, skills]):
        st.error("Please fill in all the required fields.")
    else:
        with st.spinner("Generating your resume ..."):
            ai_text = chain.run(
                full_name=full_name,
                job_title=job_title,
                company=company,
                start_date=start_date,
                end_date=end_date,
                responsibilities=responsibilities,
            )
        # Checking to generate Professional Summary
        if isinstance(ai_text, dict):
            ai_text = ai_text.get("text", "")
        else:
            ai_text = str(ai_text)
        st.markdown("---")
        st.subheader("AI-Generated Enhancements")
        st.markdown(ai_text)

        # Generate and display resume preview
        html_output = generate_resume_html(
            full_name, email, phone, skills, job_title, company, start_date, end_date, ai_text, selected_template , ats_friendly )


        st.subheader("Resume Preview")
        st.components.v1.html(html_output, height=600, scrolling=True)

        # Provide PDF download link
        st.markdown(get_pdf_download_link(html_output), unsafe_allow_html=True)
