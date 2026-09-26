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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --neon: #00e5ff;
    --neon2: #7c5cff;
    --neon-soft: #38bdf8;
    --neon-glow: rgba(0, 229, 255, 0.35);
    --bg-deep: #060b16;
    --bg-panel: #0d1524;
    --bg-card: rgba(255, 255, 255, 0.04);
    --border-glow: rgba(255, 255, 255, 0.09);
    --text-main: #e8f4ff;
    --text-dim: #8fa4c0;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, .stMarkdown h3 { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 10% -10%, rgba(0, 229, 255, 0.12), transparent 40%),
        radial-gradient(circle at 100% 0%, rgba(124, 92, 255, 0.12), transparent 40%),
        var(--bg-deep);
    color: var(--text-main);
}

/* Title */
.stApp h1 {
    background: linear-gradient(90deg, #00e5ff 0%, #7c5cff 35%, #ff5cf0 65%, #00e5ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-shadow: 0 0 30px var(--neon-glow);
}

.stCaption, .stApp p, .stMarkdown, label { color: var(--text-dim) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1220 0%, #060b16 100%);
    border-right: 1px solid var(--border-glow);
}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h1 {
    color: var(--neon) !important;
    text-shadow: 0 0 12px var(--neon-glow);
}

/* Glass cards: bordered containers used to group each step */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 18px !important;
    padding: 6px 6px 14px 6px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    margin-bottom: 22px;
}

/* Step header: gradient number badge + title, built via markdown */
.step-header { display: flex; align-items: center; gap: 10px; margin: 4px 0 14px; }
.step-header .step-num {
    width: 26px; height: 26px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, var(--neon), var(--neon2));
    color: #04101f; font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
}
.step-header h3 {
    margin: 0 !important; border-left: none !important; padding-left: 0 !important;
    font-size: 1.05rem !important;
}

/* Plain subheaders elsewhere keep the glow-bar look */
.stApp h3 {
    color: var(--text-main);
    border-left: 3px solid var(--neon);
    padding-left: 12px;
    text-shadow: 0 0 10px rgba(0,229,255,0.15);
}

/* Inputs */
.stTextArea textarea, .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    background-color: var(--bg-panel) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 10px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus, .stNumberInput input:focus {
    box-shadow: 0 0 0 2px var(--neon) !important;
    border-color: var(--neon) !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1.5px dashed var(--border-glow) !important;
    border-radius: 14px !important;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    background: linear-gradient(135deg, #00c2ff 0%, #6a5cff 100%) !important;
    color: #ffffff !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.35);
    font-weight: 600 !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 0 18px rgba(0, 194, 255, 0.35);
    opacity: 1 !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton button *, .stDownloadButton button *,
.stButton button p, .stDownloadButton button p,
.stButton button span, .stDownloadButton button span,
.stButton button div, .stDownloadButton button div {
    color: #ffffff !important;
    opacity: 1 !important;
}
.stButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 26px rgba(0, 229, 255, 0.55);
}

/* Radio groups rendered as pill toggles (Manual Questions / Upload PDF, etc.) */
div[role="radiogroup"] { gap: 10px !important; }
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 999px !important;
    padding: 8px 16px !important;
    margin-right: 0 !important;
    transition: box-shadow 0.15s ease, background 0.15s ease;
}
/* Hide the native circle indicator to get a clean pill look */
div[role="radiogroup"] label > div:first-child { display: none !important; }
div[role="radiogroup"] label p { color: var(--text-dim) !important; font-size: 0.85rem !important; margin: 0 !important; }

div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, var(--neon), var(--neon2)) !important;
    border-color: transparent !important;
    box-shadow: 0 0 18px rgba(0, 229, 255, 0.45);
}
div[role="radiogroup"] label:has(input:checked) p {
    color: #04101f !important;
    font-weight: 600 !important;
}

/* Checkbox accent color */
input[type="checkbox"] { accent-color: var(--neon) !important; }
div[data-baseweb="checkbox"] > div:first-child { border-color: var(--neon-soft) !important; }

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-glow);
    border-radius: 14px;
    padding: 14px 10px;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.08);
}
[data-testid="stMetricValue"] { color: var(--neon) !important; text-shadow: 0 0 10px var(--neon-glow); }
[data-testid="stMetricLabel"] { color: var(--text-dim) !important; }

/* Result cards: color-coded by meaning (pass/fail/grade) instead of one flat blue */
.metric-card {
    background: rgba(255,255,255,0.03); border: 1px solid var(--border-glow);
    border-radius: 14px; padding: 14px 10px; text-align: center;
}
.metric-card .val { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; }
.metric-card .lab { font-size: 0.75rem; color: var(--text-dim); margin-top: 4px; }
.metric-card.blue .val { color: var(--neon); text-shadow: 0 0 10px var(--neon-glow); }
.metric-card.gold { border-color: rgba(255, 196, 0, 0.45); box-shadow: 0 0 20px rgba(255, 196, 0, 0.22); }
.metric-card.gold .val { color: #ffc400; text-shadow: 0 0 10px rgba(255, 196, 0, 0.4); }
.metric-card.pass { border-color: rgba(0, 230, 150, 0.5); box-shadow: 0 0 20px rgba(0, 230, 150, 0.25); }
.metric-card.pass .val { color: #00e696; text-shadow: 0 0 10px rgba(0, 230, 150, 0.4); }
.metric-card.fail { border-color: rgba(255, 64, 129, 0.5); box-shadow: 0 0 20px rgba(255, 64, 129, 0.25); }
.metric-card.fail .val { color: #ff4081; text-shadow: 0 0 10px rgba(255, 64, 129, 0.4); }

/* Alerts: distinct, high-contrast colors per type instead of default olive/beige */
.stAlert { border-radius: 12px !important; }
div[data-testid*="Warning"] {
    background: rgba(255, 176, 32, 0.14) !important;
    border-left: 4px solid #ffb020 !important;
}
div[data-testid*="Error"] {
    background: rgba(255, 64, 129, 0.14) !important;
    border-left: 4px solid #ff4081 !important;
}
div[data-testid*="Success"] {
    background: rgba(0, 230, 150, 0.14) !important;
    border-left: 4px solid #00e696 !important;
}
div[data-testid*="Info"] {
    background: rgba(0, 229, 255, 0.14) !important;
    border-left: 4px solid var(--neon) !important;
}
.stAlert, .stAlert p, .stAlert span { color: var(--text-main) !important; opacity: 1 !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid var(--border-glow); border-radius: 12px; overflow: hidden; }

/* Question result cards (Step 4) */
.qcard {
    background: rgba(255,255,255,0.03); border: 1px solid var(--border-glow);
    border-radius: 14px; padding: 14px 16px; margin-bottom: 12px;
}
.qcard .qhead { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.qcard .qtitle { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.95rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; }
.qcard .marks { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--text-main); }
.qbadge { font-size: 0.75rem; padding: 3px 10px; border-radius: 999px; font-weight: 600; }
.qbadge.full { background: rgba(0, 230, 150, 0.15); color: #00e696; }
.qbadge.partial { background: rgba(255, 176, 32, 0.15); color: #ffb020; }
.qbadge.zero { background: rgba(255, 64, 129, 0.15); color: #ff4081; }
.qcard .qfeedback { font-size: 0.85rem; color: var(--text-dim); margin-top: 4px; line-height: 1.5; }

/* Divider */
hr { border-color: var(--border-glow) !important; }
</style>
""", unsafe_allow_html=True)


def step_header(number: str, title: str, gradient: str = "linear-gradient(135deg, var(--neon), var(--neon2))") -> None:
    """Render a gradient number badge + title, matching the approved mockup."""
    st.markdown(
        f'<div class="step-header"><div class="step-num" style="background:{gradient}">{number}</div><h3>{title}</h3></div>',
        unsafe_allow_html=True,
    )


# Distinct accent gradients per section, so each step reads as its own zone
GRAD_BLUE = "linear-gradient(135deg, #00e5ff, #7c5cff)"       # Exam Input
GRAD_PURPLE = "linear-gradient(135deg, #7c5cff, #ff5cf0)"     # Answer Sheet
GRAD_PINK = "linear-gradient(135deg, #ff5cf0, #ff8a65)"       # Check Exam
GRAD_CYAN = "linear-gradient(135deg, #00e5ff, #00e696)"       # AI Result
GRAD_VIOLET = "linear-gradient(135deg, #7c5cff, #00e5ff)"     # Teacher Review
GRAD_TEAL = "linear-gradient(135deg, #00e696, #00c2ff)"       # Export


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

questions = []
marks = []
answers = []

# ---------- Input mode ----------
with st.container(border=True):
    step_header("1", "Exam Input", GRAD_BLUE)
    input_mode = st.radio(
        "Choose input method",
        ["Manual Questions", "Upload Question Paper PDF"],
        horizontal=True
    )

    if input_mode == "Manual Questions":
        questions_text = st.text_area(
            "Questions (one per line)",
            placeholder="1. What is photosynthesis?\n2. Explain respiration.",
            height=180
        )
        questions = [x.strip() for x in questions_text.splitlines() if x.strip()]

        st.caption("Maximum marks")
        marks_method = st.radio(
            "Marks entry method",
            ["Same for all", "Total ÷ split", "Table"],
            horizontal=True,
            key="manual_marks_method",
            label_visibility="collapsed"
        )

        marks = []
        if not questions:
            st.caption("Add questions above to set their marks.")
        elif marks_method == "Same for all":
            same_val = st.number_input(
                "Marks per question", min_value=0.0, value=2.0, step=0.5,
                key="manual_same_marks"
            )
            marks = [same_val] * len(questions)
        elif marks_method == "Total ÷ split":
            total_val = st.number_input(
                "Total marks for this paper", min_value=0.0,
                value=float(len(questions) * 2), step=0.5, key="manual_total_marks"
            )
            per_q = total_val / len(questions) if questions else 0
            marks = [round(per_q, 2)] * len(questions)
            st.caption(f"{total_val:g} ÷ {len(questions)} questions ≈ {per_q:.2f} each.")
        else:  # Table
            for i, q in enumerate(questions):
                preview = q[:60] + ("…" if len(q) > 60 else "")
                val = st.number_input(
                    f"Q{i + 1}: {preview}", min_value=0.0, value=2.0, step=0.5,
                    key=f"manual_table_mark_{i}"
                )
                marks.append(val)

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

                # --- Auto-detect max marks instead of requiring manual entry ---
                # 1) Look for a trailing bracket on the question itself, e.g. "...[2]" or "...[2.5]"
                bracket_re = re.compile(r"\[\s*([\d.]+)\s*\]\s*$")
                # 2) Fallback: a single document-wide "each question carries X marks" statement
                rate_matches = re.findall(
                    r"each question carries\s*([\d.]+)", pdf_text, flags=re.IGNORECASE
                )
                fallback_rate = float(rate_matches[0]) if len(set(rate_matches)) == 1 else None

                detected_marks: list = []
                undetected_idx = []
                for i, q in enumerate(questions):
                    m = bracket_re.search(q)
                    if m:
                        detected_marks.append(float(m.group(1)))
                    elif fallback_rate is not None:
                        detected_marks.append(fallback_rate)
                    else:
                        detected_marks.append(None)
                        undetected_idx.append(i)

                if questions and not undetected_idx:
                    st.success(f"Auto-detected marks for all {len(questions)} questions from the PDF.")
                elif undetected_idx:
                    st.warning(
                        f"Auto-detected marks for {len(questions) - len(undetected_idx)} / "
                        f"{len(questions)} questions. Choose how to fill in the rest below."
                    )
                    leftover_method = st.radio(
                        "Leftover marks method",
                        ["Table", "Same for all remaining", "Split a total"],
                        horizontal=True,
                        key="pdf_leftover_method",
                        label_visibility="collapsed"
                    )
                    if leftover_method == "Table":
                        for i in undetected_idx:
                            preview = questions[i][:70] + ("…" if len(questions[i]) > 70 else "")
                            detected_marks[i] = st.number_input(
                                f"Max marks — Q{i + 1}: {preview}",
                                min_value=0.0, value=1.0, step=0.5, key=f"manual_mark_{i}"
                            )
                    elif leftover_method == "Same for all remaining":
                        same_val = st.number_input(
                            f"Marks for each of these {len(undetected_idx)} remaining questions",
                            min_value=0.0, value=2.0, step=0.5, key="pdf_leftover_same"
                        )
                        for i in undetected_idx:
                            detected_marks[i] = same_val
                    else:  # Split a total
                        total_val = st.number_input(
                            f"Total marks to split across these {len(undetected_idx)} questions",
                            min_value=0.0, value=float(len(undetected_idx) * 2), step=0.5,
                            key="pdf_leftover_total"
                        )
                        per_q = total_val / len(undetected_idx) if undetected_idx else 0
                        for i in undetected_idx:
                            detected_marks[i] = round(per_q, 2)
                        st.caption(f"{total_val:g} ÷ {len(undetected_idx)} ≈ {per_q:.2f} each.")

                marks = detected_marks

                # Sanity-check extracted total against a stated "Total Marks: N" if present
                total_match = re.search(
                    r"total\s*marks\s*[:\-]?\s*([\d.]+)", pdf_text, flags=re.IGNORECASE
                )
                if total_match and marks and all(v is not None for v in marks):
                    stated_total = float(total_match.group(1))
                    extracted_total = sum(marks)
                    if abs(stated_total - extracted_total) < 0.01:
                        st.success(
                            f"Extracted total = {extracted_total:g} — matches the paper's "
                            f"stated Total Marks: {stated_total:g}."
                        )
                    else:
                        st.error(
                            f"Extracted total = {extracted_total:g}, but the paper states "
                            f"Total Marks: {stated_total:g}. Please check the questions above."
                        )

                with st.expander("Manually override marks (optional)"):
                    marks_text = st.text_area(
                        "Maximum marks (one per extracted question) — leave blank to keep "
                        "the auto-detected values above",
                        placeholder="Leave empty to use auto-detected marks",
                        height=100
                    )
                    if marks_text.strip():
                        try:
                            manual_marks = [
                                float(x.strip()) for x in marks_text.splitlines() if x.strip()
                            ]
                            if len(manual_marks) == len(questions):
                                marks = manual_marks
                            else:
                                st.warning(
                                    f"Manual list has {len(manual_marks)} values but there are "
                                    f"{len(questions)} questions — auto-detected values kept instead."
                                )
                        except ValueError:
                            st.warning("Could not parse manual marks — auto-detected values kept instead.")

            except Exception as e:
                st.error(f"Could not read PDF: {e}")

# ---------- Student answer sheet ----------
with st.container(border=True):
    step_header("2", "Student Answer Sheet", GRAD_PURPLE)
    answer_mode = st.radio(
        "Choose answer input",
        ["Paste/Type Answers", "Upload Answer Sheet PDF", "Upload Answer Sheet Image"],
        horizontal=True
    )

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
                        extracted = extract_answers_from_image(
                            answer_image.getvalue(),
                            mime_type=answer_image.type or "image/jpeg",
                        )
                        st.session_state.ocr_text = extracted
                        st.success("OCR extraction completed.")
                    except Exception as e:
                        st.error(f"OCR error: {e}")

            ocr_text = st.text_area(
                "OCR text / corrected answers",
                value=st.session_state.get("ocr_text", ""),
                height=220
            )
            # Group by numbered marker, same as the PDF paths, so a multi-line
            # handwritten answer under "5." stays one answer instead of splitting.
            answers = extract_numbered_items(ocr_text)

# ---------- Build exam ----------
with st.container(border=True):
    step_header("3", "Check Exam", GRAD_PINK)

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

    parsed = parse_ai_results(data["raw"], data["exam_data"])
    exam_by_number = {item["number"]: item for item in data["exam_data"]}

    with st.container(border=True):
        step_header("4", "AI Question-by-Question Result", GRAD_CYAN)

        for item in parsed:
            qn = item["number"]
            earned = item["earned"]
            max_marks = item["max_marks"]
            feedback = item["feedback"] or "—"
            missing = item["missing"] or "None"

            if earned <= 0:
                status_cls, status_label = "zero", "Zero"
            elif earned >= max_marks - 1e-9:
                status_cls, status_label = "full", "Full marks"
            else:
                status_cls, status_label = "partial", "Partial"

            st.markdown(
                f'<div class="qcard">'
                f'<div class="qhead">'
                f'<div class="qtitle">Q{qn} <span class="qbadge {status_cls}">{status_label}</span></div>'
                f'<div class="marks">{earned:g} / {max_marks:g}</div>'
                f'</div>'
                f'<div class="qfeedback"><b>Feedback:</b> {feedback}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander(f"Show answer details — Q{qn}"):
                student_answer = exam_by_number.get(qn, {}).get("answer", "—")
                st.markdown(f"**Student's Answer:** {student_answer}")
                st.markdown(f"**Missing Points:** {missing}")

        with st.expander("Show raw AI response (full text)"):
            st.text(data["raw"])

    with st.container(border=True):
        step_header("5", "Teacher Review / Final Marks", GRAD_VIOLET)
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

    with st.container(border=True):
        step_header("📊", "Final Result", GRAD_CYAN)
        c1, c2, c3, c4 = st.columns(4)
        status_class = "pass" if passed else "fail"
        status_text = "PASS" if passed else "FAIL"
        cards = [
            (c1, "blue", f"{final_earned:g}/{maximum:g}", "Marks"),
            (c2, "blue", f"{percentage:.2f}%", "Percentage"),
            (c3, "gold", grade, "Grade"),
            (c4, status_class, status_text, "Status"),
        ]
        for col, cls, val, lab in cards:
            with col:
                st.markdown(
                    f'<div class="metric-card {cls}"><div class="val">{val}</div>'
                    f'<div class="lab">{lab}</div></div>',
                    unsafe_allow_html=True,
                )

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

    with st.container(border=True):
        step_header("6", "Export", GRAD_TEAL)
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
