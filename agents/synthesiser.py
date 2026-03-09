"""
Step 4 - write the final newsletter.
Combines the approved summaries with the user's stored projects and
interests to produce something actually worth reading.
"""

from langchain_core.prompts import ChatPromptTemplate

from config import USE_MOCKS
from llm import get_llm, invoke_with_retry
from memory import get_memories

_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly, expert newsletter writer.  "
     "You write in a warm but professional tone, like a knowledgeable "
     "colleague sharing links over coffee.\n\n"
     "You have access to the reader's past projects and interests below.  "
     "Your job is to:\n"
     "1. Present today's top stories in a scannable format.\n"
     "2. For EACH story, add a short 'Why this matters to you' note that "
     "connects the news to the reader's own projects or interests.\n"
     "3. End with a single 'Action Item' -- the ONE thing the reader should "
     "look at first."),
    ("human",
     "== READER PROFILE (past projects & interests) ==\n"
     "{memories}\n\n"
     "== TODAY'S APPROVED STORIES ==\n"
     "{stories}\n\n"
     "Please write today's personalised newsletter."),
])


def synthesise_newsletter(approved_articles: list[dict]) -> str:
    """Generate the final personalised newsletter text."""

    memories = get_memories()
    memory_text = "\n".join(
        f"- [{m.get('category', 'note')}] {m['text']}" for m in memories
    ) or "(No past projects recorded yet.)"

    stories_text = ""
    for i, article in enumerate(approved_articles, 1):
        stories_text += (
            f"\n### Story {i}: {article['title']}\n"
            f"URL: {article['url']}\n"
            f"Summary: {article['summary']}\n"
        )

    if USE_MOCKS:
        return _mock_newsletter(memories, approved_articles)

    try:
        chain = _prompt | get_llm()
        return invoke_with_retry(chain, {
            "memories": memory_text,
            "stories": stories_text,
        })
    except Exception as e:
        print(f"Synthesis error ({type(e).__name__}), using mock newsletter")
        return _mock_newsletter(memories, approved_articles)


def _mock_newsletter(memories: list[dict], articles: list[dict]) -> str:
    """Generate a realistic mock newsletter for demo purposes."""
    output = "# 📰 Your Personalised Tech Digest\n\n"
    output += "_Generated in mock mode (no API credits required)_\n\n"
    
    output += "## Today's Top Stories\n\n"
    
    for i, article in enumerate(articles, 1):
        output += f"### {i}. {article['title']}\n\n"
        output += f"**Summary:** {article['snippet'][:200]}...\n\n"
        output += f"🔗 [Read more]({article['url']})\n\n"
        
        # Try to relate to a memory
        if memories:
            mem = memories[i % len(memories)]
            output += f"💡 **Why this matters to you:** This relates to your {mem.get('category', 'interest')} "
            output += f"project: '{mem['text'][:60]}...'. "
            output += "This development could enhance your implementation.\n\n"
        else:
            output += "💡 **Why this matters:** Keep this on your radar for future projects.\n\n"
        
        output += "---\n\n"
    
    output += "## ✨ Action Item\n\n"
    if articles:
        output += f"**Start here:** Check out [{articles[0]['title']}]({articles[0]['url']}) "
        output += "first — it has the most immediate relevance to your work.\n\n"
    
    output += "_Want to add your own projects? Run: `python main.py --add-memory \"Your project here\"`_\n"
    
    return output
