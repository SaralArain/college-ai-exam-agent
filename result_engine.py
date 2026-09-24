import re


def calculate_result(earned, maximum, pass_percentage=50):
    earned = max(0.0, min(float(earned), float(maximum)))
    maximum = float(maximum)
    percentage = (earned / maximum * 100) if maximum else 0.0

    if percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    return percentage, grade, percentage >= pass_percentage


def parse_ai_results(raw, exam_data):
    results = []

    for item in exam_data:
        qn = item["number"]
        max_marks = float(item["max_marks"])

        # Locate the section for this question.
        pattern = (
            rf"Question\s*{qn}\s*:?(.*?)(?=\n\s*Question\s*{qn + 1}\s*:|\n\s*TEACHER REVIEW:|\Z)"
        )
        match = re.search(pattern, raw, flags=re.IGNORECASE | re.DOTALL)

        section = match.group(1) if match else ""

        mark_match = re.search(
            r"Marks\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*([0-9]+(?:\.[0-9]+)?)",
            section,
            flags=re.IGNORECASE,
        )

        earned = float(mark_match.group(1)) if mark_match else 0.0
        denominator = float(mark_match.group(2)) if mark_match else max_marks
        earned = max(0.0, min(earned, max_marks))

        feedback = _field(section, "Feedback")
        missing = _field(section, "Missing Points")

        results.append({
            "number": qn,
            "earned": earned,
            "max_marks": max_marks,
            "feedback": feedback,
            "missing": missing,
            "denominator": denominator,
        })

    return results


def _field(section, name):
    match = re.search(
        rf"{re.escape(name)}\s*:\s*(.*?)(?=\n[A-Za-z][A-Za-z /_-]*\s*:|\Z)",
        section,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""
