# Agentic AI Stock Research Assistant

Multi-agent stock research app built with LangGraph and Streamlit. Enter a ticker and the graph runs **fundamental**, **technical**, and **news** agents in parallel, then a risk manager and a final investment thesis.

This is a research demo, not financial advice.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your keys to `.env`:

- `OPENAI_API_KEY` — used by the risk and synthesizer agents
- `ALPHAVANTAGE_API_KEY` — used for news sentiment
- `LANGSMITH_TRACING` / `LANGSMITH_ENDPOINT` / `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` — [LangSmith](https://smith.langchain.com) traces (project: `Agentic Stock Assistant`)

## Run

```bash
streamlit run streamlit_app.py
```

## Observability and evaluation

Each pipeline run is a LangSmith trace named `research-{TICKER}` when `LANGSMITH_API_KEY` is set. Child spans include the graph nodes, market tools, and LLM calls. Open the link from the Streamlit **Observability & evaluation** panel, or filter project `Agentic Stock Assistant` in [LangSmith](https://smith.langchain.com).

1. Create an API key at [smith.langchain.com](https://smith.langchain.com)
2. Set `LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_API_KEY`, and `LANGSMITH_PROJECT` in `.env`
3. Restart Streamlit so it reloads the env

The harness scores the output with deterministic checks (metrics present, rating is Buy/Hold/Sell, no node errors). Fixture evals need no API keys:

```bash
python -m app.evaluation
python -m pytest tests/ -q
```

## Project layout

```text
streamlit_app.py      # UI
app/graph.py          # LangGraph workflow
app/harness.py        # Run entrypoint, tags, eval report
app/observability.py  # Node timing + LangSmith config
app/evaluation.py     # Deterministic graders
app/state.py          # Shared state
app/tools/market.py   # Yahoo Finance + Alpha Vantage tools
```

Do not commit `.env`. Keep secrets in the local file only.
