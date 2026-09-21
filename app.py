import streamlit as st
from agents import create_exam_checker
from tasks import create_exam_task
from crewai import Crew


st.set_page_config(
    page_title="College AI Exam Checker",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 College AI Exam Checker")
st.write("AI-powered exam checking and result system")

st.divider()

st.subheader("📝 Exam Information")

student_name = st.text_input("Student Name")
subject = st.text_input("Subject")

question = st.text_area(
    "Question",
    placeholder="Enter the exam question..."
)

student_answer = st.text_area(
    "Student Answer",
    placeholder="Enter the student's answer..."
)

marks = st.number_input(
    "Maximum Marks",
    min_value=1,
    max_value=100,
    value=5
)

if st.button("🤖 Check Answer"):

    if not question or not student_answer:
        st.warning("Please enter both the question and student answer.")

    else:

        with st.spinner("AI Examiner is checking the answer..."):

            try:
                examiner = create_exam_checker()

                exam_task = create_exam_task(
                    examiner,
                    question,
                    student_answer,
                    marks
                )

                crew = Crew(
                    agents=[examiner],
                    tasks=[exam_task],
                    verbose=False
                )

                result = crew.kickoff()

                st.success("✅ Answer checked!")

                st.subheader("📊 AI Exam Result")
                st.write(result.raw)

            except Exception as e:
                st.error(f"Error: {e}")
