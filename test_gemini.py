#!/usr/bin/env python3
"""
test_gemini.py - Diagnostic script to test Gemini API key and find working models
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    print("❌ No GEMINI_API_KEY found in .env")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
print("\nTesting with langchain-google-genai...\n")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Models to try in order
candidates = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

for model_name in candidates:
    print(f"🧪 Testing {model_name}...", end=" ", flush=True)
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=api_key,
            timeout=15,
            max_retries=1
        )
        response = llm.invoke([HumanMessage(content="Say 'Hello from Gemini!' and nothing else.")])
        text = response.content if response and response.content else ""
        if len(text) > 5:
            print(f"✅ '{text.strip()[:60]}'")
        else:
            print(f"⚠️  Response too short ({len(text)} chars): '{text}'")
    except Exception as e:
        print(f"❌ {type(e).__name__}: {str(e)[:100]}")

print("\nDone! Use the model that shows ✅ in your .env: MODEL_NAME=<model-name>")
