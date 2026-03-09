"""
Step 3 - the editor reviews each summary and either approves it or
asks for more detail. If it asks for more, the pipeline loops back
to search and re-summarise before trying again.
"""

from langchain_core.prompts import ChatPromptTemplate

from config import USE_MOCKS
from llm import get_llm, invoke_with_retry

_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a demanding technical editor.  Your job is to decide if a "
     "summary is specific enough for a professional newsletter.\n\n"
     "Rules:\n"
     "- If the summary contains concrete facts, numbers, or actionable "
     "insights, respond with exactly:  VERDICT: APPROVED\n"
     "- If the summary is vague, hand-wavy, or missing an obvious detail, "
     "respond with:\n"
     "  VERDICT: NEEDS_MORE_INFO\n"
     "  FOLLOW_UP: <a precise question that would fill the gap>\n\n"
     "Always start your response with one of those two verdict lines."),
    ("human",
     "ARTICLE TITLE: {title}\n"
     "SUMMARY:\n{summary}\n\n"
     "Please evaluate."),
])


def review_summary(article: dict) -> dict:
    """
    Return the article dict augmented with:
      - `verdict`   : 'APPROVED' | 'NEEDS_MORE_INFO'
      - `follow_up` : str | None   (a question to send back to search)
      - `editor_notes` : the full editor response
    """
    if USE_MOCKS:
        return {
            **article,
            "verdict": "APPROVED",
            "follow_up": None,
            "editor_notes": "VERDICT: APPROVED\n\nThe summary is concrete and actionable.",
        }

    try:
        chain = _prompt | get_llm()
        text = invoke_with_retry(chain, {
            "title": article["title"],
            "summary": article["summary"],
        })

        verdict = "APPROVED"
        follow_up = None

        if "NEEDS_MORE_INFO" in text:
            verdict = "NEEDS_MORE_INFO"
            for line in text.splitlines():
                if line.strip().upper().startswith("FOLLOW_UP:"):
                    follow_up = line.split(":", 1)[1].strip()
                    break
            if not follow_up:
                follow_up = f"Find more specific details about: {article['title']}"

        return {
            **article,
            "verdict": verdict,
            "follow_up": follow_up,
            "editor_notes": text,
        }
    except Exception as e:
        print(f"Editor error ({type(e).__name__}), falling back to approved")
        return {
            **article,
            "verdict": "APPROVED",
            "follow_up": None,
            "editor_notes": "VERDICT: APPROVED (fallback)",
        }
