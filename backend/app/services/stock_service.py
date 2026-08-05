import yfinance as yf

def get_stock_data(ticker: str) -> dict:
    """
    Fetch stock information using Yahoo Finance.
    """

    stock = yf.Ticker(ticker)

    info = stock.info

    return {
        "ticker": ticker.upper(),
        "company": info.get("longName"),
        "sector": info.get("sector"),
        "current_price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow"),
        "currency": info.get("currency")
    }