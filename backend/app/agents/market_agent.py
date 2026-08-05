from backend.app.services.stock_service import get_stock_data

def market_agent(state):
    ticker = state["ticker"]
    stock_data = get_stock_data(ticker)
    return {
        "stock_data": stock_data
    }