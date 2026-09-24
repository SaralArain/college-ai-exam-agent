import io
import re
import json
import pandas as pd
import streamlit as st
from pypdf import PdfReader
from agents import create_exam_checker, create_question_analyzer, create_review_agent
from tasks import create_exam_task, create_question_analysis_task, create_review_task
from result_engine import calculate_result, parse_ai_results
from exports import make_excel, make_pdf

st.set_page_config(page_title="AI Agent Exam Checker", page_icon="🎓", layout="wide")

st.title("🎓 AI Agent Exam Checker")
st.caption("AI-assisted college exam checking with teacher-controlled final marks.")
st.info("AI marks are recommendations. The teacher should review and approve final marks.")

def extract_numbered_items(text: str) -> list[str]:
    """Group extracted PDF text into one item per numbered question/answer.

    Text-based PDF extraction returns one line per visual line, so a single
    question with multiple answer options (or a title/subtitle line) would
    otherwise be miscounted as several separate items. This groups every
    line under the numbered marker it belongs to (e.g. "1.", "2)") until the
    next numbered marker appears, so options/wrapped lines stay attached to
    their question. Lines before the first numbered marker (titles,
    instructions, student name/ID headers) are dropped.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    marker = re.compile(r"^(\d{1,3})[\.\)]\s+")

    items = []
    current = []
    for line in lines:
        if marker.match(line):
            if current:
                items.append(" ".join(current).strip())
            current = [line]
        elif current:
            current.append(line)
        # else: header/title text before the first numbered item — discard
    if current:
        items.append(" ".join(current).strip())
    return items


if "exam_result" not in st.session_state:
    st.session_state.exam_result = None
if "final_marks" not in st.session_state:
    st.session_state.final_marks = {}

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Exam Settings")
    student_name = st.text_input("Student Name")
    subject = st.selectbox(
        "Subject",
        ["Mathematics", "Physics", "Chemistry", "Biology",
         "Computer Science", "English", "Other"]
    )
    pass_percentage = st.number_input(
        "Pass Percentage", min_value=0, max_value=100, value=50
    )
    use_web_research = st.checkbox(
        "Use Tavily research when needed",
        value=False,
        help="Optional. Ordinary grading should primarily use the teacher's material."
    )

# ---------- Input mode ----------
st.subheader("1️⃣ Exam Input")
input_mode = st.radio(
    "Choose input method",
    ["Manual Questions", "Upload Question Paper PDF"],
    horizontal=True
)

questions = []
marks = []

if input_mode == "Manual Questions":
    questions_text = st.text_area(
        "Questions (one per line)",
        placeholder="1. What is photosynthesis?\n2. Explain respiration.",
        height=180
    )
    marks_text = st.text_area(
        "Maximum marks (one per line, same order)",
        placeholder="5\n10",
        height=120
    )

    questions = [x.strip() for x in questions_text.splitlines() if x.strip()]
    try:
        marks = [float(x.strip()) for x in marks_text.splitlines() if x.strip()]
    except ValueError:
        marks = []

else:
    uploaded_pdf = st.file_uploader("Upload Question Paper PDF", type=["pdf"])
    if uploaded_pdf:
        try:
            reader = PdfReader(uploaded_pdf)
            pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            st.text_area("Extracted Question Paper Text", pdf_text, height=250)

            st.warning(
                "PDF extraction works for text-based PDFs. Scanned/handwritten PDFs "
                "need the OCR/image mode below."
            )

            # Group lines by numbered question marker (1., 2., ...) so a
            # question's options / wrapped lines aren't counted separately.
            questions = extract_numbered_items(pdf_text)

            marks_text = st.text_area(
                "Maximum marks (one per extracted question)",
                placeholder="5\n5\n10",
                height=120
            )
            try:
                marks = [float(x.strip()) for x in marks_text.splitlines() if x.strip()]
            except ValueError:
                marks = []

        except Exception as e:
            st.error(f"Could not read PDF: {e}")

# ---------- Student answer sheet ----------
st.subheader("2️⃣ Student Answer Sheet")
answer_mode = st.radio(
    "Choose answer input",
    ["Paste/Type Answers", "Upload Answer Sheet PDF", "Upload Answer Sheet Image"],
    horizontal=True
)

answers = []

if answer_mode == "Paste/Type Answers":
    answers_text = st.text_area(
        "Student answers (one answer per line, same order as questions)",
        placeholder="Photosynthesis is...\nRespiration is...",
        height=240
    )
    answers = [x.strip() for x in answers_text.splitlines() if x.strip()]

elif answer_mode == "Upload Answer Sheet PDF":
    answer_pdf = st.file_uploader("Upload Student Answer Sheet PDF", type=["pdf"], key="answer_pdf")
    if answer_pdf:
        try:
            reader = PdfReader(answer_pdf)
            extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
            st.text_area("Extracted Answer Sheet Text", extracted, height=250)
            # Group lines by numbered marker so each answer sheet item lines
            # up 1:1 with the corresponding numbered question.
            answers = extract_numbered_items(extracted)
            st.warning(
                "Text extraction is available for text PDFs. For handwriting, use the image "
                "OCR option or provide a typed answer."
            )
        except Exception as e:
            st.error(f"Could not read answer PDF: {e}")

else:
    answer_image = st.file_uploader(
        "Upload answer-sheet image",
        type=["png", "jpg", "jpeg"],
        key="answer_image"
    )
    if answer_image:
        st.image(answer_image, caption="Uploaded answer sheet", use_container_width=True)
        st.warning(
            "Image OCR uses Gemini vision. If your current Gemini account/model does not "
            "support image input, type/paste the answers instead."
        )
        if st.button("🔎 Extract Answers with AI OCR"):
            from ocr import extract_answers_from_image
            with st.spinner("Reading the answer sheet..."):
                try:
                    extracted = extract_answers_from_image(answer_image.getvalue())
                    st.session_state.ocr_text = extracted
                    st.success("OCR extraction completed.")
                except Exception as e:
                    st.error(f"OCR error: {e}")

        ocr_text = st.text_area(
            "OCR text / corrected answers",
            value=st.session_state.get("ocr_text", ""),
            height=220
        )
        answers = [x.strip() for x in ocr_text.splitlines() if x.strip()]

# ---------- Build exam ----------
st.subheader("3️⃣ Check Exam")

if st.button("🤖 Check Complete Exam", type="primary"):
    if not student_name.strip():
        st.warning("Enter the student name.")
    elif not questions:
        st.warning("Add or upload questions.")
    elif len(questions) != len(answers):
        st.error(
            f"Questions = {len(questions)}, Answers = {len(answers)}. "
            "They must match in this version."
        )
    elif len(questions) != len(marks):
        st.error(
            f"Questions = {len(questions)}, Mark values = {len(marks)}. "
            "They must match."
        )
    else:
        exam_data = [
            {
                "number": i + 1,
                "question": q,
                "answer": a,
                "max_marks": m,
            }
            for i, (q, a, m) in enumerate(zip(questions, answers, marks))
        ]

        with st.spinner("CrewAI examiner is checking the exam..."):
            try:
                examiner = create_exam_checker()
                task = create_exam_task(
                    examiner,
                    subject,
                    exam_data,
                    use_web_research=use_web_research
                )

                from crewai import Crew
                crew = Crew(agents=[examiner], tasks=[task], verbose=False)
                result = crew.kickoff()

                st.session_state.exam_result = {
                    "raw": result.raw,
                    "exam_data": exam_data,
                    "student": student_name,
                    "subject": subject,
                    "pass_percentage": pass_percentage,
                }

                st.success("✅ Exam checked.")
            except Exception as e:
                st.error(f"Exam checking error: {e}")

# ---------- Results ----------
data = st.session_state.exam_result
if data:
    st.divider()
    st.subheader("4️⃣ AI Question-by-Question Result")
    st.write(data["raw"])

    parsed = parse_ai_results(data["raw"], data["exam_data"])

    st.subheader("5️⃣ Teacher Review / Final Marks")
    st.caption("Edit any AI mark below. The final result uses these teacher-approved marks.")

    final_rows = []
    for item in parsed:
        qn = item["number"]
        ai_mark = item["earned"]
        max_mark = item["max_marks"]

        default = st.session_state.final_marks.get(qn, ai_mark)
        final = st.number_input(
            f"Question {qn} — Final Marks (max {max_mark:g})",
            min_value=0.0,
            max_value=float(max_mark),
            value=min(float(default), float(max_mark)),
            step=0.5,
            key=f"final_mark_{qn}"
        )
        st.session_state.final_marks[qn] = final
        final_rows.append({
            "Question": qn,
            "AI Marks": ai_mark,
            "Final Marks": final,
            "Maximum": max_mark,
            "Feedback": item["feedback"],
            "Missing Points": item["missing"],
        })

    final_earned = sum(r["Final Marks"] for r in final_rows)
    maximum = sum(r["Maximum"] for r in final_rows)
    percentage, grade, passed = calculate_result(final_earned, maximum, data["pass_percentage"])

    st.subheader("📊 Final Result")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Marks", f"{final_earned:g}/{maximum:g}")
    c2.metric("Percentage", f"{percentage:.2f}%")
    c3.metric("Grade", grade)
    c4.metric("Status", "PASS" if passed else "FAIL")

    df = pd.DataFrame(final_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Review agent is optional and only used for final review summary.
    if st.button("🧑‍🏫 Generate Teacher Review Summary"):
        with st.spinner("Generating review summary..."):
            try:
                reviewer = create_review_agent()
                review_task = create_review_task(
                    reviewer,
                    data["student"],
                    data["subject"],
                    final_rows,
                    final_earned,
                    maximum,
                    percentage,
                    grade,
                    passed,
                )
                from crewai import Crew
                review_crew = Crew(
                    agents=[reviewer],
                    tasks=[review_task],
                    verbose=False
                )
                review = review_crew.kickoff()
                st.session_state.review_summary = review.raw
            except Exception as e:
                st.error(f"Review error: {e}")

    if st.session_state.get("review_summary"):
        st.subheader("🧑‍🏫 Teacher Review Summary")
        st.write(st.session_state.review_summary)

    st.subheader("6️⃣ Export")
    col1, col2 = st.columns(2)

    excel_bytes = make_excel(
        student=data["student"],
        subject=data["subject"],
        rows=final_rows,
        earned=final_earned,
        maximum=maximum,
        percentage=percentage,
        grade=grade,
        passed=passed,
    )

    pdf_bytes = make_pdf(
        student=data["student"],
        subject=data["subject"],
        rows=final_rows,
        earned=final_earned,
        maximum=maximum,
        percentage=percentage,
        grade=grade,
        passed=passed,
    )

    with col1:
        st.download_button(
            "📊 Download Excel Result",
            data=excel_bytes,
            file_name=f"{student_name}_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        st.download_button(
            "📄 Download PDF Result",
            data=pdf_bytes,
            file_name=f"{student_name}_result.pdf",
            mime="application/pdf"
        )

    st.divider()
    st.caption(
        "Tavily is optional and should be used for reference research, not as the sole "
        "source for grading. Final marks remain under teacher control."
    )
