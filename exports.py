import io
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def make_excel(student, subject, rows, earned, maximum, percentage, grade, passed):
    output = io.BytesIO()

    df = pd.DataFrame(rows)

    summary = pd.DataFrame([
        ["Student", student],
        ["Subject", subject],
        ["Total Marks", f"{earned:g}/{maximum:g}"],
        ["Percentage", f"{percentage:.2f}%"],
        ["Grade", grade],
        ["Status", "PASS" if passed else "FAIL"],
    ], columns=["Field", "Value"])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Result")
        df.to_excel(writer, index=False, sheet_name="Question Results")

    output.seek(0)
    return output.getvalue()


def make_pdf(student, subject, rows, earned, maximum, percentage, grade, passed):
    output = io.BytesIO()

    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("College AI Exam Result", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Student: {student}", styles["Normal"]))
    story.append(Paragraph(f"Subject: {subject}", styles["Normal"]))
    story.append(Paragraph(f"Marks: {earned:g}/{maximum:g}", styles["Normal"]))
    story.append(Paragraph(f"Percentage: {percentage:.2f}%", styles["Normal"]))
    story.append(Paragraph(f"Grade: {grade}", styles["Normal"]))
    story.append(Paragraph(f"Status: {'PASS' if passed else 'FAIL'}", styles["Normal"]))
    story.append(Spacer(1, 15))

    table_data = [["Q", "AI/Final Marks", "Maximum", "Feedback"]]
    for row in rows:
        table_data.append([
            str(row["Question"]),
            str(row["Final Marks"]),
            str(row["Maximum"]),
            str(row["Feedback"])[:180],
        ])

    table = Table(table_data, repeatRows=1, colWidths=[30, 75, 60, 350])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        "AI marks are recommendations. Final marks were controlled by the teacher.",
        styles["Italic"]
    ))

    doc.build(story)
    output.seek(0)
    return output.getvalue()
