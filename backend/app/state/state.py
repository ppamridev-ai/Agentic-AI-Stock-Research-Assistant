from typing import TypedDict

# LangGraph passes a state object between nodes
class StockState(TypedDict):
    ticker: str
    stock_data: dict
