import os
from crewai import Agent, LLM


def create_exam_checker():

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY")
    )

    exam_checker = Agent(
        role="College Exam Examiner",

        goal=(
            "Check a student's answer fairly according to the question "
            "and maximum marks, then provide marks and clear feedback."
        ),

        backstory=(
            "You are an experienced college examiner. "
            "You evaluate answers objectively and award marks based on "
            "correct concepts, relevance, completeness and accuracy. "
            "You never give marks simply because an answer is long."
        ),

        llm=llm,

        verbose=True
    )

    return exam_checker
