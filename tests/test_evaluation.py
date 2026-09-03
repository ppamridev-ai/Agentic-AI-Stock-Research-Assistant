from app.evaluation import evaluate_result, extract_rating, run_fixture_evals


def test_extract_rating_uses_last_match():
    text = "Some say Buy. Final Actionable Rating: Hold"
    assert extract_rating(text) == "Hold"


def test_fixture_evals_match_expectations():
    rows = run_fixture_evals()
    assert rows
    assert all(row["matched_expectation"] for row in rows)


def test_empty_thesis_fails_rating_check():
    report = evaluate_result(
        {
            "ticker": "MSFT",
            "fundamental_data": {"pe_ratio": 30.0},
            "technical_data": {"rsi_14": 50.0},
            "news_data": {"sentiment_score": 0.0, "key_headlines": []},
            "risk_assessment": "Competition risk.",
            "final_recommendation": "",
            "errors": [],
            "run_trace": [],
        }
    )
    assert report["checks"]["rating_valid"] is False
    assert report["passed"] is False
