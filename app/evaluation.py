"""Deterministic evaluators for a completed research run."""

from __future__ import annotations

import re
from typing import Any

VALID_RATINGS = ("Buy", "Hold", "Sell")
RATING_RE = re.compile(r"\b(Buy|Hold|Sell)\b", re.IGNORECASE)


def extract_rating(text: str | None) -> str | None:
    if not text:
        return None
    matches = RATING_RE.findall(text)
    return matches[-1].title() if matches else None


def _has_number(data: dict | None, key: str) -> bool:
    if not isinstance(data, dict):
        return False
    value = data.get(key)
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def evaluate_result(result: dict[str, Any]) -> dict[str, Any]:
    """Score a pipeline result with pass/fail checks (no LLM judge)."""
    fund = result.get("fundamental_data") or {}
    tech = result.get("technical_data") or {}
    news = result.get("news_data") or {}
    rating = extract_rating(result.get("final_recommendation"))
    errors = result.get("errors") or []
    node_errors = [e for e in (result.get("run_trace") or []) if e.get("status") == "error"]

    checks = {
        "has_ticker": bool(result.get("ticker")),
        "fundamentals_present": isinstance(fund, dict) and "error" not in fund,
        "fundamentals_numeric": _has_number(fund, "pe_ratio") or _has_number(fund, "market_cap"),
        "technicals_present": isinstance(tech, dict) and "error" not in tech,
        "technicals_numeric": _has_number(tech, "rsi_14") or _has_number(tech, "sma_50"),
        "news_present": isinstance(news, dict) and "error" not in news,
        "risk_present": bool(result.get("risk_assessment")),
        "thesis_present": bool(result.get("final_recommendation")),
        "rating_valid": rating in VALID_RATINGS,
        "no_node_errors": len(errors) == 0 and len(node_errors) == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not failed,
        "score": round(sum(checks.values()) / len(checks), 2),
        "rating": rating,
        "failed": failed,
        "checks": checks,
    }


SAMPLE_CASES = [
    {
        "id": "healthy_nvda",
        "result": {
            "ticker": "NVDA",
            "fundamental_data": {"pe_ratio": 45.2, "market_cap": 3.1e12, "summary": "Semiconductors"},
            "technical_data": {"rsi_14": 62.1, "sma_50": 120.0, "trend": "Bullish"},
            "news_data": {"sentiment_score": 0.22, "key_headlines": ["Earnings beat"]},
            "risk_assessment": "Valuation and concentration risk remain elevated.",
            "final_recommendation": "Bull case: AI demand. Bear case: multiples. Final Actionable Rating: Hold",
            "errors": [],
            "run_trace": [{"node": "synthesizer", "status": "ok", "elapsed_ms": 12.0}],
        },
        "expect_pass": True,
    },
    {
        "id": "missing_rating",
        "result": {
            "ticker": "AAPL",
            "fundamental_data": {"pe_ratio": 28.0, "market_cap": 3.0e12},
            "technical_data": {"rsi_14": 55.0},
            "news_data": {"sentiment_score": 0.05, "key_headlines": []},
            "risk_assessment": "Regulatory risk.",
            "final_recommendation": "The setup is mixed with no clear action.",
            "errors": [],
            "run_trace": [],
        },
        "expect_pass": False,
    },
    {
        "id": "tool_failure",
        "result": {
            "ticker": "BAD",
            "fundamental_data": {"error": "No data"},
            "technical_data": {"error": "No price data found"},
            "news_data": {"error": "rate limit"},
            "risk_assessment": None,
            "final_recommendation": None,
            "errors": ["fundamental: No data"],
            "run_trace": [{"node": "fundamental", "status": "error", "elapsed_ms": 1.0}],
        },
        "expect_pass": False,
    },
]


def run_fixture_evals() -> list[dict[str, Any]]:
    reports = []
    for case in SAMPLE_CASES:
        report = evaluate_result(case["result"])
        reports.append(
            {
                "id": case["id"],
                "expect_pass": case["expect_pass"],
                "matched_expectation": report["passed"] == case["expect_pass"],
                **report,
            }
        )
    return reports


if __name__ == "__main__":
    rows = run_fixture_evals()
    failed = [row for row in rows if not row["matched_expectation"]]
    for row in rows:
        status = "OK" if row["matched_expectation"] else "FAIL"
        print(f"{status}  {row['id']}: score={row['score']} failed={row['failed']}")
    if failed:
        raise SystemExit(1)
    print(f"Passed {len(rows)} fixture evals.")
