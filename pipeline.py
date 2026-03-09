"""
Orchestrates the four steps in order:

    1. searcher.py   - pull recent articles
    2. summariser.py - condense each one
    3. editor.py     - reject weak summaries and loop back if needed
    4. synthesiser.py - write the final newsletter
"""

import time

from agents.searcher import search_recent_news
from agents.summariser import summarise_article
from agents.editor import review_summary
from agents.synthesiser import synthesise_newsletter

MAX_EDITOR_LOOPS = 2  # stop after two search-and-retry cycles per article
API_DELAY = 8  # free tier is strict about requests per minute


def run_pipeline(topic: str, verbose: bool = True) -> str:
    """Execute the full 4-step pipeline and return the newsletter text."""

    _log(verbose, f"\n{'='*60}")
    _log(verbose, f"  STEP 1 — Searching for recent news on: {topic}")
    _log(verbose, f"{'='*60}")

    articles = search_recent_news(topic)
    _log(verbose, f"  Found {len(articles)} articles.")

    _log(verbose, f"\n{'='*60}")
    _log(verbose, "  STEP 2 — Summarising articles")
    _log(verbose, f"{'='*60}")

    summarised = []
    for i, article in enumerate(articles, 1):
        _log(verbose, f"\n  [{i}/{len(articles)}] Summarising: {article['title']}")
        enriched = summarise_article(article)
        summarised.append(enriched)
        _log(verbose, f"    Summary ready ({len(enriched['summary'])} chars)")
        if i < len(articles):
            time.sleep(API_DELAY)

    _log(verbose, f"\n{'='*60}")
    _log(verbose, "  STEP 3 — Editor reviewing summaries")
    _log(verbose, f"{'='*60}")

    approved = []
    for i, article in enumerate(summarised):
        reviewed = _review_with_retry(article, topic, verbose)
        approved.append(reviewed)
        if i < len(summarised) - 1:
            time.sleep(API_DELAY)

    approved = [a for a in approved if a["verdict"] == "APPROVED"]
    _log(verbose, f"\n  Editor approved {len(approved)} / {len(summarised)} articles.")

    if not approved:
        return "The editor rejected all summaries. Try a broader topic or check your API keys."

    _log(verbose, f"\n{'='*60}")
    _log(verbose, "  STEP 4 — Writing your newsletter")
    _log(verbose, f"{'='*60}\n")

    newsletter = synthesise_newsletter(approved)
    return newsletter


def _review_with_retry(article: dict, topic: str, verbose: bool) -> dict:
    reviewed = review_summary(article)
    loops = 0

    while reviewed["verdict"] == "NEEDS_MORE_INFO" and loops < MAX_EDITOR_LOOPS:
        loops += 1
        follow_up = reviewed["follow_up"]
        _log(verbose, f"  Editor wants more info: {follow_up}")
        _log(verbose, f"    Re-searching (attempt {loops}/{MAX_EDITOR_LOOPS})")

        # Run another search using the editor's follow-up question, then re-summarise.
        extra_results = search_recent_news(f"{topic} {follow_up}", max_results=2)
        if extra_results:
            combined_snippet = (
                article["snippet"]
                + "\n\n[Additional context]\n"
                + "\n".join(r["snippet"] for r in extra_results)
            )
            article = {**article, "snippet": combined_snippet}
            article = summarise_article(article)
            reviewed = review_summary(article)
        else:
            break

    status = "APPROVED" if reviewed["verdict"] == "APPROVED" else "REJECTED"
    _log(verbose, f"  {article['title']}  [{status}]")
    return reviewed


def _log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)
