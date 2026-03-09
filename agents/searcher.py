"""
Step 1 - search for recent news using Tavily.
Returns a list of {title, url, snippet} dicts.
Falls back to hard-coded mock results if no API key is set.
"""

from langchain_community.tools.tavily_search import TavilySearchResults

from config import TAVILY_API_KEY


def search_recent_news(topic: str, max_results: int = 6) -> list[dict]:
    """Search the web for news from the last 24 hours on *topic*."""

    if not TAVILY_API_KEY:
        return _mock_results(topic)

    tool = TavilySearchResults(
        max_results=max_results,
        search_depth="advanced",
        include_answer=False,
    )
    raw = tool.invoke({"query": f"latest news {topic} today"})

    results = []
    for item in raw:
        results.append(
            {
                "title": item.get("title", item.get("url", "")),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
            }
        )
    return results


def _mock_results(topic: str) -> list[dict]:
    return [
        {
            "title": f"New Ultra-Low-Power {topic} Chip Announced",
            "url": "https://example.com/article-1",
            "snippet": (
                f"A startup has unveiled a new {topic} chip that uses 40%% less power "
                "than its predecessor, targeting battery-operated sensor deployments."
            ),
        },
        {
            "title": f"Open-Source {topic} Library Hits 1.0",
            "url": "https://example.com/article-2",
            "snippet": (
                f"The popular open-source {topic} library released version 1.0 today, "
                "adding TLS 1.3 support and over-the-air update capabilities."
            ),
        },
        {
            "title": f"Major Cloud Provider Launches {topic} Edge Service",
            "url": "https://example.com/article-3",
            "snippet": (
                f"A hyperscaler announced a managed {topic} edge-compute service that "
                "allows deploying ML inference models directly to constrained devices."
            ),
        },
    ]
