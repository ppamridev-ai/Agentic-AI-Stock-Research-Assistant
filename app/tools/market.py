import yfinance as yf
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import requests
from langsmith import traceable

load_dotenv()

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

@traceable(name="fetch_fundamental_data", run_type="tool")
def fetch_fundamental_data(ticker: str) -> dict:
    """Fetch structured fundamental metrics from Yahoo Finance."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "revenue_growth": info.get("revenueGrowth"),
        "free_cash_flow": info.get("freeCashflow"),
        "summary": f"Company operating in {info.get('sector', 'N/A')} sector with market cap of {info.get('marketCap', 'N/A')}."
    }

@traceable(name="calculate_technical_indicators", run_type="tool")
def calculate_technical_indicators(ticker: str) -> dict:
    """Calculate RSI and Moving Averages deterministically using pandas."""
    df = yf.download(ticker, period="1y", interval="1d", progress=False)
    if df.empty:
        return {"error": "No price data found"}
    
    close = df['Close'].squeeze()
    
    # Calculate 50 and 200 SMA
    sma_50 = float(close.rolling(window=50).mean().iloc[-1])
    sma_200 = float(close.rolling(window=200).mean().iloc[-1])
    
    # Calculate 14-day RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_14 = float(100 - (100 / (1 + rs)).iloc[-1])
    
    latest_close = float(close.iloc[-1])
    trend = "Bullish" if latest_close > sma_200 else "Bearish"
    
    return {
        "rsi_14": round(rsi_14, 2),
        "sma_50": round(sma_50, 2),
        "sma_200": round(sma_200, 2),
        "trend": trend,
        "summary": f"Latest close: ${latest_close:.2f}. RSI: {rsi_14:.1f}. Trend is {trend} relative to 200 SMA."
    }

@traceable(name="fetch_news_sentiment", run_type="tool")
def fetch_news_sentiment(ticker: str) -> dict:
    """Fetch news sentiment from Alpha Vantage and map it to the app schema."""
    url = (
        "https://www.alphavantage.co/query"
        f"?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHAVANTAGE_API_KEY}"
    )
    response = requests.get(url, timeout=20)
    data = response.json()
    feed = data.get("feed") or []

    headlines = []
    scores = []
    ticker_upper = ticker.upper()
    for item in feed[:8]:
        title = item.get("title")
        if title:
            headlines.append(title)
        ticker_score = next(
            (
                ts.get("ticker_sentiment_score")
                for ts in (item.get("ticker_sentiment") or [])
                if ts.get("ticker") == ticker_upper
            ),
            item.get("overall_sentiment_score"),
        )
        if ticker_score is not None:
            try:
                scores.append(float(ticker_score))
            except (TypeError, ValueError):
                pass

    avg_score = round(sum(scores) / len(scores), 3) if scores else None
    if avg_score is None:
        label = "unavailable"
    elif avg_score >= 0.15:
        label = "bullish"
    elif avg_score <= -0.15:
        label = "bearish"
    else:
        label = "neutral"

    return {
        "sentiment_score": avg_score,
        "key_headlines": headlines,
        "summary": (
            f"Average news sentiment for {ticker_upper} is {label}"
            + (f" ({avg_score})." if avg_score is not None else ".")
        ),
    }