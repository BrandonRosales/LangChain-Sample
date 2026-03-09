"""
Loads settings from .env and exposes them as module-level constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# MOCK_MODE can be "true", "false", or "auto".
# "auto" uses mocks only when there's no API key present.
MOCK_MODE = os.getenv("MOCK_MODE", "auto").lower()
USE_MOCKS = MOCK_MODE == "true" or (MOCK_MODE == "auto" and not GEMINI_API_KEY)

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory_store")
os.makedirs(MEMORY_DIR, exist_ok=True)
