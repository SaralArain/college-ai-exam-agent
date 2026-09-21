import streamlit as st

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
        st.info("AI Agent will check the answer here.")
        st.write("**Question:**", question)
        st.write("**Student Answer:**", student_answer)
        st.write("**Maximum Marks:**", marks)
