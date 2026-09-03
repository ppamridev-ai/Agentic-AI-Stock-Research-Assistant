from typing import Any

from langsmith import traceable

from app.evaluation import evaluate_result
from app.graph import app_graph
from app.observability import configure_observability, current_trace_url, project_name, tracing_enabled
from app.state import InvestmentState

configure_observability()


def initial_state(ticker: str) -> InvestmentState:
    return {
        "ticker": ticker.strip().upper(),
        "fundamental_data": None,
        "technical_data": None,
        "news_data": None,
        "risk_assessment": None,
        "final_recommendation": None,
        "errors": [],
        "run_trace": [],
    }


@traceable(name="stock_research", run_type="chain")
def run_research(ticker: str, graph=None) -> dict[str, Any]:
    """Run the research graph and send the full trace to LangSmith when enabled."""
    graph = graph or app_graph
    state = initial_state(ticker)
    if not state["ticker"]:
        empty = {
            **state,
            "errors": ["No ticker provided."],
            "run_trace": [{"node": "harness", "status": "error", "elapsed_ms": 0, "error": "empty ticker"}],
        }
        return {**empty, "eval_report": evaluate_result(empty), "langsmith_url": None}

    result = graph.invoke(
        state,
        config={
            "run_name": f"research-{state['ticker']}",
            "tags": ["stock-research", state["ticker"]],
            "metadata": {
                "ticker": state["ticker"],
                "project": project_name(),
            },
        },
    )
    result["eval_report"] = evaluate_result(result)
    result["langsmith_url"] = current_trace_url()
    return result
