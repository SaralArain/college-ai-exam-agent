from crewai import Task


def create_exam_task(agent, question, student_answer, max_marks):

    task = Task(
        description=f"""
        Check the student's answer for the following college exam question.

        QUESTION:
        {question}

        STUDENT ANSWER:
        {student_answer}

        MAXIMUM MARKS:
        {max_marks}

        Evaluate the answer using these criteria:
        1. Correctness
        2. Understanding of the main concept
        3. Relevance to the question
        4. Completeness
        5. Important missing information

        Give a fair mark between 0 and {max_marks}.

        Return the result in this format:

        Marks: X/{max_marks}

        Feedback:
        Explain briefly why these marks were given.

        Missing Points:
        List important points missing from the answer, if any.
        """,

        expected_output=f"""
        Marks: X/{max_marks}

        Feedback:
        A short explanation of the marking.

        Missing Points:
        Important missing points or "None".
        """,

        agent=agent
    )

    return task
