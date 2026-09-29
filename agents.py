import streamlit as st
from crewai import Agent, LLM


def get_llm():
    return LLM(
        model="gemini/gemini-3.5-flash-lite",
        api_key=st.secrets["GEMINI_API_KEY"],
    )


def create_exam_checker(use_web_research: bool = False):
    tools = []
    if use_web_research:
        try:
            from crewai_tools import TavilySearchTool
            import os
            api_key = st.secrets.get("TAVILY_API_KEY")
            if api_key:
                os.environ["TAVILY_API_KEY"] = api_key
                tools = [TavilySearchTool()]
            else:
                st.warning(
                    "\"Use Tavily research\" was checked, but no TAVILY_API_KEY is set "
                    "in Streamlit secrets — grading will continue without web search."
                )
        except Exception as e:
            st.warning(f"Could not enable Tavily search ({e}) — continuing without it.")

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
        tools=tools,
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
