"""
File-backed storage for the user's projects and interests.
The synthesiser reads these entries and uses them to personalise the newsletter.
"""

import json
import os
from datetime import datetime

from config import MEMORY_DIR

_MEMORY_FILE = os.path.join(MEMORY_DIR, "user_memory.json")


def _load() -> list[dict]:
    if not os.path.exists(_MEMORY_FILE):
        return []
    with open(_MEMORY_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(entries: list[dict]) -> None:
    with open(_MEMORY_FILE, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2, default=str)


def add_memory(text: str, category: str = "project") -> None:
    """Persist a new memory entry (e.g. a project the user started)."""
    entries = _load()
    entries.append(
        {"text": text, "category": category, "created": datetime.now().isoformat()}
    )
    _save(entries)


def get_memories() -> list[dict]:
    """Return all stored memory entries."""
    return _load()


def seed_example_memories() -> None:
    """Write a few starter entries on first run so the newsletter has something to work with."""
    if _load():
        return
    examples = [
        {
            "text": "Started an ESP32-based soil-moisture sensor project for the backyard garden. Using deep-sleep to save power.",
            "category": "project",
            "created": "2025-12-14T09:30:00",
        },
        {
            "text": "Exploring LoRaWAN gateways for a community air-quality monitoring network.",
            "category": "project",
            "created": "2026-01-22T14:15:00",
        },
        {
            "text": "Interested in on-device ML for anomaly detection on microcontrollers.",
            "category": "interest",
            "created": "2026-02-05T11:00:00",
        },
    ]
    _save(examples)
