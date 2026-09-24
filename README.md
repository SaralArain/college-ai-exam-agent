# 🎓 College AI Exam Checker — Full Build

## Architecture

Streamlit → CrewAI → Gemini → Exam Checker → Teacher Review → Final Result

## Included

1. GitHub-ready project structure
2. Streamlit frontend
3. CrewAI configuration
4. Gemini 3.5 Flash-Lite configuration
5. Exam Checker Agent
6. Exam Checking Task
7. One-question and multi-question checking
8. Marking rubric
9. Clean result display
10. Subject selection
11. Multiple questions
12. Per-question marking scheme
13. Question-by-question checking
14. Automatic total and percentage
15. Grade and Pass/Fail
16. Teacher review/edit marks
17. Text-based Question Paper PDF extraction
18. Student Answer Sheet PDF extraction
19. Image OCR using Gemini vision
20. Multiple students can be processed one at a time
21. Result table/dashboard foundation
22. PDF and Excel export
23. Optional Tavily switch (integration point)
24. Multiple CrewAI agents
25. Deployment-ready files

## Important notes

### Gemini
This project uses the model string that was working in the user's existing project:

`gemini/gemini-3.5-flash-lite`

If Google's API later changes model availability, use the model name shown by the user's current API error/documentation.

### Secrets

In Streamlit Cloud, add:

```toml
GEMINI_API_KEY = "your-key"
TAVILY_API_KEY = "your-key"
```

Do not commit real API keys to GitHub.

### OCR

Image OCR uses Gemini's image input. Handwriting quality depends on the image and the model/account's multimodal support. Always review extracted text before grading.

### Tavily

The current full build exposes a Tavily setting but does not make web search a mandatory grading step. This is intentional: exam grading should primarily follow the question paper, marking scheme, and teacher-provided material.

### Multiple students

The current UI can process students one at a time and export each result. A persistent student database/class roster is a later production feature.

### Teacher control

AI-generated marks are recommendations. The teacher's edited final marks are used for the final result.

## Deployment

1. Upload these files to a GitHub repository.
2. Create a Streamlit app from that repository.
3. Add the secrets in Streamlit Settings → Secrets.
4. Set the main file to `app.py`.
5. Deploy.
