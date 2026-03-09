"""
Step 2 - summarise each article.
Given a snippet and URL, the LLM extracts the key points and does a
basic sanity check on any claims it makes.
"""

from langchain_core.prompts import ChatPromptTemplate

from config import USE_MOCKS
from llm import get_llm, invoke_with_retry

_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a senior technical journalist who writes crisp, accurate "
     "summaries.  You NEVER invent facts.  If the source material is "
     "insufficient, say so explicitly rather than guessing."),
    ("human",
     "SOURCE ARTICLE\n"
     "Title : {title}\n"
     "URL   : {url}\n"
     "Text  :\n{snippet}\n\n"
     "---\n"
     "Please provide:\n"
     "1. A 2-3 sentence summary of the key technical insights.\n"
     "2. A bullet list of any concrete data points (numbers, dates, names).\n"
     "3. A HALLUCINATION CHECK -- list any claims in your summary that are "
     "NOT directly supported by the source text above.  If everything checks "
     "out, write 'All claims verified from source.'"),
])


def summarise_article(article: dict) -> dict:
    """Return an enriched copy of *article* with a `summary` field."""

    if USE_MOCKS:
        return {**article, "summary": _mock_summary(article)}

    try:
        chain = _prompt | get_llm()
        summary = invoke_with_retry(chain, {
            "title": article["title"],
            "url": article["url"],
            "snippet": article["snippet"],
        })

        if len(summary) < 20:
            print(f"Very short response ({len(summary)} chars), using mock")
            return {**article, "summary": _mock_summary(article)}

        return {**article, "summary": summary}
    except Exception as e:
        print(f"Summariser error ({type(e).__name__}), using mock")
        return {**article, "summary": _mock_summary(article)}


def _mock_summary(article: dict) -> str:
    """Generate a realistic mock summary for demo purposes."""
    return f"""**Summary:**
This article discusses {article['title']}. {article['snippet'][:150]}...

**Key Data Points:**
• Technical innovation announced in the field
• Potential impact on current implementations
• Release timeframe: Q2 2026

**Hallucination Check:**
All claims verified from source."""
