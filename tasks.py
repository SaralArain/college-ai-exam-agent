from crewai import Task


def create_exam_task(agent, subject, exam_data, use_web_research=False):
    exam_text = "\n\n".join(
        f""" QUESTION {x["number"]}: {x["question"]} STUDENT ANSWER: {x["answer"]} MAXIMUM MARKS: {x["max_marks"]} """
        for x in exam_data
    )

    web_note = ""
    if use_web_research:
        web_note = """ Optional reference research may be used when appropriate, but do not replace the teacher-provided question/marking information with unsupported web claims. """

    return Task(
        description=f""" Check this college exam. SUBJECT: {subject} {exam_text} GENERAL RULES: - Check every question separately. - Never exceed the maximum marks. - Give partial marks when justified. - Base the decision on the student's actual answer. - Do not invent steps. - Explain errors and missing points. - If handwriting/OCR or wording makes an answer uncertain, say Teacher Review Recommended. SUBJECT RULES: Mathematics: Check formulas, calculations, working steps, and final answers. A correct method with an arithmetic error may receive partial credit. Physics/Chemistry: Check formulas, units, equations, calculations, concepts, and final answers. Biology/English: Check correctness, concepts/content, relevance, completeness, explanation, grammar or structure where relevant. Computer Science: Check logic, code, syntax, output, concepts, and explanation. {web_note} OUTPUT FORMAT: Question 1: Student Answer: ... Correct Answer / Expected Answer: ... Marks: X/Y Feedback: ... Missing Points: ... Question 2: Student Answer: ... Correct Answer / Expected Answer: ... Marks: X/Y Feedback: ... Missing Points: ... Continue for every question. TEACHER REVIEW: Yes or No """,
        expected_output=""" Question N: Student Answer: ... Correct Answer / Expected Answer: ... Marks: X/Y Feedback: ... Missing Points: ... TEACHER REVIEW: Yes or No """,
        agent=agent,
    )


def create_question_analysis_task(agent, subject, questions):
    return Task(
        description=f""" Analyze these {subject} exam questions and describe the key concepts, expected answer points, formulas/steps where applicable, and likely marking considerations. Do not assign final student marks. QUESTIONS: {questions} """,
        expected_output="A concise question-by-question marking guide.",
        agent=agent,
    )


def create_review_task( agent, student, subject, rows, earned, maximum, percentage, grade, passed, ):
    return Task(
        description=f""" Prepare a teacher review summary. Student: {student} Subject: {subject} Final marks: {earned}/{maximum} Percentage: {percentage:.2f}% Grade: {grade} Status: {"PASS" if passed else "FAIL"} QUESTION RESULTS: {rows} Summarize: 1. Overall strengths 2. Common mistakes 3. Questions needing attention 4. A short teacher note Do not change or recommend a different final mark. """,
        expected_output="A short teacher-facing review summary.",
        agent=agent,
    )
