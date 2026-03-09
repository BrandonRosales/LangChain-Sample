# Deep Research & Newsletter Agent

A LangChain-powered multi-agent pipeline that searches the web, summarises articles, critiques the results, and writes a personalised newsletter that connects today's news to your own projects.
**Powered by Google Gemini** — uses Gemini 1.5 Flash for fast, cost-effective AI processing (free tier available!).
## How it works

| Step | Agent | What it does |
|------|-------|--------------|
| **1** | **Smart Search** | Queries Tavily for the latest news on your chosen topic |
| **2** | **Summariser** (sub-agent per article) | Extracts key insights and runs a hallucination self-check |
| **3** | **Editor / Critic** | Reviews each summary; rejects vague ones and loops back to Step 1 with a pointed follow-up question |
| **4** | **Synthesiser** | Uses your long-term memory (past projects & interests) to write a personalised newsletter |

```
 ┌──────────┐     ┌──────────────┐     ┌────────┐     ┌──────────────┐
 │  Search  │────▶│  Summarise   │────▶│ Editor │────▶│  Synthesise  │
 │ (Tavily) │◀────│  (per link)  │◀────│(Critic)│     │ (Newsletter) │
 └──────────┘ loop└──────────────┘ loop└────────┘     └──────────────┘
```

## Quick start

```bash
# 1 — Clone & install
cd LangChain-Sample
pip install -r requirements.txt

# 2 — Add your API keys
cp .env.example .env
#    then edit .env with your GEMINI_API_KEY and TAVILY_API_KEY

# 3 — Run it
python main.py              # defaults to "Tech"
python main.py "AI agents"  # pick any topic
```

> **No API keys?** The project ships with mock search results so you can explore the pipeline structure without spending credits. You still need a Gemini key for Steps 2-4.

> **⚠️ Free tier exhausted?** If you get a quota error, the agents will automatically fall back to mock mode. You can also force mock mode by setting `MOCK_MODE=true` in your `.env` file. This lets you see the full 4-step pipeline in action without API credits!

## Adding memories

The agent gets better when it knows about your projects:

```bash
python main.py --add-memory "Started a LoRa mesh network for wildfire detection"
```

Memories are stored in `memory_store/user_memory.json` and persist across runs. A few example memories are seeded automatically on first run.

## Project structure

```
LangChain-Sample/
├── main.py              # CLI entry-point
├── pipeline.py          # 4-step orchestrator with editor loop-back
├── config.py            # .env loader & shared settings
├── memory.py            # File-backed long-term memory
├── agents/
│   ├── searcher.py      # Step 1 — Tavily search (+ mock fallback)
│   ├── summariser.py    # Step 2 — Article summarisation sub-agent
│   ├── editor.py        # Step 3 — Critic / quality gate
│   └── synthesiser.py   # Step 4 — Personalised newsletter writer
├── requirements.txt
├── .env.example
└── .gitignore
```

## Configuration

All settings live in `.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `GEMINI_API_KEY` | — | Required for all LLM calls (or use mock mode) |
| `TAVILY_API_KEY` | — | Required for live web search (falls back to mocks) |
| `MODEL_NAME` | `gemini-flash-latest` | Gemini model (free tier: `gemini-flash-latest`, `gemini-2.0-flash`, `gemini-2.5-flash`) |
| `TEMPERATURE` | `0.3` | Lower = more factual, higher = more creative |
| `MOCK_MODE` | `auto` | `auto` = use mocks if no key, `true` = always mock, `false` = never mock |
