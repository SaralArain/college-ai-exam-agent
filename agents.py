import streamlit as st
from crewai import Agent, LLM


def create_exam_checker():

    llm = LLM(
        model="gemini/gemini-3.6-flash",
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    exam_checker = Agent(
        role="College Exam Examiner",

        goal=(
            "Check a student's answer fairly according to the question "
            "and maximum marks, then provide marks and clear feedback."
        ),

        backstory=(
            "You are an experienced college examiner. "
            "You evaluate answers objectively based on correctness, "
            "understanding, relevance, completeness and accuracy."
        ),

        llm=llm,
        verbose=True
    )

    return exam_checker
