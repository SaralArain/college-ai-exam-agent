from crewai import Task


def create_exam_task(agent, question, student_answer, max_marks):

    task = Task(
        description=f"""
You are checking a college student's exam answer.

QUESTION:
{question}

STUDENT ANSWER:
{student_answer}

MAXIMUM MARKS:
{max_marks}

MARKING RUBRIC:

1. Correctness
- Check whether the information in the answer is factually correct.
- Do not give marks for incorrect information.

2. Key Concepts
- Check whether the important concepts required by the question are present.
- Give credit for correct concepts even if the wording is different.

3. Relevance
- The answer must directly answer the question.
- Do not give extra marks for unrelated information.

4. Completeness
- Compare the answer with what would normally be expected for the question.
- Identify important missing points.

5. Understanding
- Check whether the student demonstrates understanding of the topic,
  rather than only using keywords.

MARKING RULES:

- Give a fair score from 0 to {max_marks}.
- NEVER give more than {max_marks}.
- Do not assume information that the student did not write.
- Give partial marks when the answer is partially correct.
- Give 0 marks if the answer is completely incorrect or irrelevant.
- Base the marks on the student's actual answer.
- Explain clearly why the marks were awarded.
- Mention important missing points.
- If the answer is ambiguous or difficult to judge, mention:
  "Teacher Review Recommended."

RETURN THE RESULT EXACTLY IN THIS FORMAT:

Marks: X/{max_marks}

Correctness: [brief evaluation]

Key Concepts: [brief evaluation]

Relevance: [brief evaluation]

Completeness: [brief evaluation]

Feedback:
[Short explanation of why these marks were given.]

Missing Points:
[List important missing points, or write "None"]

Teacher Review:
[Yes or No]

Do not add unnecessary information outside this format.
""",

        expected_output=f"""
Marks: X/{max_marks}

Correctness: Brief evaluation

Key Concepts: Brief evaluation

Relevance: Brief evaluation

Completeness: Brief evaluation

Feedback:
Short explanation of the marks.

Missing Points:
Important missing points or "None"

Teacher Review:
Yes or No
""",

        agent=agent
    )

    return task
