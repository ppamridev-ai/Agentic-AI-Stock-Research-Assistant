import streamlit as st
from app.harness import run_research
from app.observability import project_name, tracing_enabled


def _fmt_number(value, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def _fmt_compact_usd(value) -> str:
    if value is None:
        return "N/A"
    abs_value = abs(value)
    if abs_value >= 1e12:
        return f"${value / 1e12:.2f}T"
    if abs_value >= 1e9:
        return f"${value / 1e9:.2f}B"
    if abs_value >= 1e6:
        return f"${value / 1e6:.2f}M"
    return f"${value:,.0f}"


def _fmt_percent(value) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def _sentiment_label(score) -> str:
    if score is None:
        return "N/A"
    if score >= 0.15:
        return "Bullish"
    if score <= -0.15:
        return "Bearish"
    return "Neutral"

st.set_page_config(page_title="Multi-Agent Stock Research Assistant", layout="wide")

st.title("Enterprise Multi-Agent Stock Analysis Platform")
st.caption("Powered by LangGraph, Deterministic Financial Tools, & Multi-Agent Orchestration")

ticker = st.text_input("Enter Stock Ticker Symbol (e.g. AAPL, NVDA, MSFT):", "NVDA").upper()

if st.button("Run Research Pipeline", type="primary"):
    with st.spinner(f"Orchestrating agents to evaluate {ticker}..."):
        result = run_research(ticker)
        
        # UI Display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Fundamental Data")
            fund = result.get("fundamental_data") or {}
            f1, f2 = st.columns(2)
            f1.metric("P/E Ratio", _fmt_number(fund.get("pe_ratio")))
            f2.metric("Market Cap", _fmt_compact_usd(fund.get("market_cap")))
            f3, f4 = st.columns(2)
            f3.metric("Revenue Growth", _fmt_percent(fund.get("revenue_growth")))
            f4.metric("Free Cash Flow", _fmt_compact_usd(fund.get("free_cash_flow")))
            if fund.get("summary"):
                st.caption(fund["summary"])

        with col2:
            st.subheader("Technical Indicators")
            tech = result.get("technical_data") or {}
            t1, t2 = st.columns(2)
            t1.metric("RSI (14)", _fmt_number(tech.get("rsi_14")))
            t2.metric("Trend", tech.get("trend") or "N/A")
            t3, t4 = st.columns(2)
            t3.metric("50-day SMA", _fmt_number(tech.get("sma_50")))
            t4.metric("200-day SMA", _fmt_number(tech.get("sma_200")))
            if tech.get("summary"):
                st.caption(tech["summary"])

        st.divider()

        st.subheader("News Sentiment")
        news = result.get("news_data") or {}
        score = news.get("sentiment_score")
        n1, n2 = st.columns([1, 3])
        with n1:
            st.metric(
                "Sentiment Score",
                _fmt_number(score, 3),
                _sentiment_label(score),
                delta_color="off",
            )
        with n2:
            if news.get("summary"):
                st.caption(news["summary"])
            headlines = news.get("key_headlines") or []
            if isinstance(headlines, str):
                headlines = [headlines]
            if headlines:
                for headline in headlines[:8]:
                    st.markdown(f"- {headline}")
            else:
                st.caption("No headlines available.")
            
        st.divider()
        
        st.subheader("Risk Manager (Devil's Advocate)")
        if result.get("risk_assessment"):
            st.warning(result["risk_assessment"])
        else:
            st.info("No risk assessment available.")
        
        st.divider()
        
        st.subheader("Final CIO Investment Thesis")
        if result.get("final_recommendation"):
            st.markdown(result["final_recommendation"])
        else:
            st.info("No final recommendation available.")

        st.divider()
        report = result.get("eval_report") or {}
        with st.expander("Observability & evaluation", expanded=bool(result.get("errors"))):
            st.caption(
                f"LangSmith: {'on' if tracing_enabled() else 'off'} · "
                f"project `{project_name()}` · "
                f"Eval score: {report.get('score', 'n/a')} · "
                f"Rating: {report.get('rating') or 'n/a'}"
            )
            if result.get("langsmith_url"):
                st.link_button("Open LangSmith trace", result["langsmith_url"])
            elif not tracing_enabled():
                st.info(
                    "Add `LANGSMITH_API_KEY` to `.env` (and set `LANGSMITH_TRACING=true`) "
                    "to send this run to LangSmith."
                )
            if result.get("errors"):
                for error in result["errors"]:
                    st.error(error)
            if report.get("failed"):
                st.warning("Failed checks: " + ", ".join(report["failed"]))
            elif report.get("passed"):
                st.success("All evaluation checks passed.")
            if result.get("run_trace"):
                st.dataframe(result["run_trace"], hide_index=True)