from unittest.mock import patch

from app.graph import build_graph
from app.harness import run_research


class FakeLLM:
    def invoke(self, prompt: str):
        class _Response:
            def __init__(self, content: str):
                self.content = content

        if "Risk Manager" in prompt:
            return _Response("Valuation and concentration are the main risks.")
        return _Response(
            "Bull case: demand. Bear case: multiples. Final Actionable Rating: Hold"
        )


def test_empty_ticker_is_rejected_without_running_graph():
    result = run_research("  ")
    assert result["errors"] == ["No ticker provided."]
    assert result["eval_report"]["passed"] is False


@patch("app.graph.fetch_news_sentiment", return_value={"sentiment_score": 0.2, "key_headlines": ["Beat"], "summary": "bullish"})
@patch("app.graph.calculate_technical_indicators", return_value={"rsi_14": 55.0, "sma_50": 100.0, "sma_200": 90.0, "trend": "Bullish"})
@patch("app.graph.fetch_fundamental_data", return_value={"pe_ratio": 28.4, "market_cap": 2.0e12, "summary": "Tech"})
def test_parallel_graph_completes_and_passes_eval(_fund, _tech, _news):
    graph = build_graph(FakeLLM())
    result = run_research("nvda", graph=graph)

    assert result["ticker"] == "NVDA"
    assert result["fundamental_data"]["pe_ratio"] == 28.4
    assert result["technical_data"]["trend"] == "Bullish"
    assert result["news_data"]["sentiment_score"] == 0.2
    assert "risks" in result["risk_assessment"].lower()
    assert result["eval_report"]["rating"] == "Hold"
    assert result["eval_report"]["passed"] is True
    traced_nodes = {event["node"] for event in result["run_trace"]}
    assert {"fundamental", "technical", "news", "risk_manager", "synthesizer"} <= traced_nodes
