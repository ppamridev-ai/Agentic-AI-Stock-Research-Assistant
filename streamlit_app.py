import streamlit as st
from app.graph import app_graph


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
        initial_state = {
            "ticker": ticker,
            "fundamental_data": None,
            "technical_data": None,
            "news_data": None,
            "risk_assessment": None,
            "final_recommendation": None,
            "errors": []
        }
        
        # Execute Graph
        result = app_graph.invoke(initial_state)
        
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