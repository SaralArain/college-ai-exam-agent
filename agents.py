import streamlit as st
from crewai import Agent, LLM


def get_llm():
    return LLM(
        model="gemini/gemini-3.5-flash-lite",
        api_key=st.secrets["GEMINI_API_KEY"],
    )


def create_exam_checker():
    return Agent(
        role="College Exam Examiner",
        goal=(
            "Check college exam answers fairly and consistently using the "
            "provided questions, student answers, subject, and marking scheme."
        ),
        backstory=(
            "You are an experienced examiner. You check numerical work step by "
            "step and theory answers for correctness, relevance, completeness, "
            "and important missing points. You never exceed maximum marks."
        ),
        llm=get_llm(),
        verbose=True,
    )


def create_question_analyzer():
    return Agent(
        role="Exam Question Analyzer",
        goal="Analyze exam questions and identify what a correct answer should contain.",
        backstory=(
            "You are an academic question analyst. You identify concepts, "
            "steps, formulas, and expected points needed for fair marking."
        ),
        llm=get_llm(),
        verbose=False,
    )


def create_review_agent():
    return Agent(
        role="Teacher Review Assistant",
        goal="Summarize the reviewed exam result and identify answers that deserve teacher attention.",
        backstory=(
            "You assist teachers after AI grading. You do not change marks. "
            "You summarize strengths, weaknesses, and review flags."
        ),
        llm=get_llm(),
        verbose=False,
    )
