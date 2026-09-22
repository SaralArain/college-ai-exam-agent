from crewai import Task


def create_exam_task(agent, question, student_answer, max_marks):

    task = Task(
        description=f"""
You are a college mathematics examiner.

Check the student's mathematics answer carefully.

QUESTION:
{question}

STUDENT ANSWER:
{student_answer}

MAXIMUM MARKS:
{max_marks}

IMPORTANT INSTRUCTIONS:

1. Identify each individual math question in the input.

2. Check each question separately.

3. For every question:
   - Determine the correct mathematical answer.
   - Compare it with the student's answer.
   - Check the student's calculation and working steps.
   - Identify calculation mistakes.
   - Give appropriate marks.

4. Give partial marks when:
   - The method is correct but there is a calculation error.
   - Some important steps are correct but the final answer is wrong.

5. Give zero marks when the solution is completely incorrect
   or unrelated.

6. Never give more than the maximum available marks.

7. Do not assume steps that the student did not write.

8. Clearly show the correct answer when the student's answer is wrong.

9. At the end, calculate the total marks.

10. If the student's working is unclear or difficult to judge,
    write "Teacher Review Recommended."

RETURN THE RESULT IN THIS FORMAT:

Question 1:
Student Answer:
Correct Answer:
Marks:
Mistake/Explanation:

Question 2:
Student Answer:
Correct Answer:
Marks:
Mistake/Explanation:

Question 3:
Student Answer:
Correct Answer:
Marks:
Mistake/Explanation:

Continue this format for all questions.

TOTAL:
Total Marks:

OVERALL FEEDBACK:
Brief explanation of the student's performance.

TEACHER REVIEW:
Yes or No
""",

        expected_output="""
Question 1:
Student Answer:
Correct Answer:
Marks:
Mistake/Explanation:

Question 2:
Student Answer:
Correct Answer:
Marks:
Mistake/Explanation:

TOTAL:
Total Marks:

OVERALL FEEDBACK:
Brief explanation.

TEACHER REVIEW:
Yes or No
""",

        agent=agent
    )

    return task
