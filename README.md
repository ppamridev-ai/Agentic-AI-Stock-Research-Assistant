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

## Run

```bash
streamlit run streamlit_app.py
```

## Project layout

```text
streamlit_app.py     # UI
app/graph.py         # LangGraph workflow
app/state.py         # Shared state
app/tools/market.py  # Yahoo Finance + Alpha Vantage tools
```

Do not commit `.env`. Keep secrets in the local file only.
