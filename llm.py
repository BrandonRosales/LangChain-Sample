"""
Shared LangChain LLM instance + a small retry helper.

Every agent imports get_llm() instead of constructing its own
ChatGoogleGenerativeAI, so the model/temp/key settings live in one place.
"""

import time

from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY, MODEL_NAME, TEMPERATURE

MAX_RETRIES = 5
RETRY_DELAY = 15  # seconds between retries on rate-limit errors

_RETRYABLE = ("resource_exhausted", "429", "quota", "rate", "503", "unavailable")


def get_llm(**overrides) -> ChatGoogleGenerativeAI:
    """Return a ready-to-use ChatGoogleGenerativeAI instance."""
    opts = dict(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        google_api_key=GEMINI_API_KEY,
        timeout=60,
    )
    opts.update(overrides)
    return ChatGoogleGenerativeAI(**opts)


def invoke_with_retry(chain, inputs: dict) -> str:
    """Invoke a LangChain chain, retrying on transient rate-limit errors.

    Returns the string content of the AIMessage.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke(inputs)
            return result.content
        except Exception as exc:
            msg = str(exc).lower()
            if any(tok in msg for tok in _RETRYABLE) and attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(f"    Rate limited, waiting {wait}s ({attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                continue
            raise
