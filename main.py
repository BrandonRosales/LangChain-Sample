#!/usr/bin/env python3
"""
Entry point. Run from the terminal:

    python main.py                    (defaults to "Tech")
    python main.py "AI agents"
    python main.py --add-memory "Built a Raspberry Pi cluster for edge inference"
"""

import sys

from memory import seed_example_memories, add_memory
from pipeline import run_pipeline


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--add-memory":
        text = " ".join(sys.argv[2:])
        add_memory(text)
        print(f"Memory saved: {text}")
        return

    # First run seeds a few example memories so the output isn't totally bare.
    seed_example_memories()

    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Tech"

    print(f"\nDeep Research & Newsletter Agent")
    print(f"Topic: {topic}")
    print(f"{'─'*40}\n")

    newsletter = run_pipeline(topic, verbose=True)

    print("\n" + "=" * 60)
    print("  YOUR NEWSLETTER")
    print("=" * 60)
    print(newsletter)
    print()


if __name__ == "__main__":
    main()
