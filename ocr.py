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
