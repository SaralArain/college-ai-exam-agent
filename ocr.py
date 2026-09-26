import os
from google import genai
from google.genai import types


def extract_answers_from_image(image_bytes, mime_type="image/jpeg"):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Streamlit secrets are not environment variables by default.
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(api_key=api_key)

    prompt = """
Read this student answer-sheet image carefully.

Transcribe the answers in order, one answer per line.
Do not solve or correct the answers.
Preserve mathematical expressions as accurately as possible.
If handwriting is unclear, write [UNCLEAR].
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
    )

    text = (response.text or "").strip()
    if not text:
        raise ValueError(
            "Gemini returned no text for this image. The image may be unreadable, "
            "blank, or blocked by safety filtering."
        )
    return text


def extract_questions_from_image(image_bytes, mime_type="image/jpeg"):
    """Transcribe a photographed/scanned question paper, keeping question
    numbers and any printed marks (e.g. "[2]") exactly as they appear, so the
    same numbered-grouping and marks-detection logic used for text PDFs can
    run on the result."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(api_key=api_key)

    prompt = """
Read this question paper image carefully.

Transcribe every question in order, keeping its original question number
(e.g. "1.", "2.") at the start of each line exactly as printed.
If a mark value is printed next to a question (e.g. "[2]", "(5 marks)"),
keep it attached at the end of that question's line exactly as printed.
Do not answer or solve the questions — only transcribe them.
If handwriting or print is unclear, write [UNCLEAR] in place of that word.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
    )

    text = (response.text or "").strip()
    if not text:
        raise ValueError(
            "Gemini returned no text for this image. The image may be unreadable, "
            "blank, or blocked by safety filtering."
        )
    return text
