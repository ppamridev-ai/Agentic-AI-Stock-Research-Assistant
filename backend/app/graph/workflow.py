from langgraph.graph import StateGraph, END
from backend.app.state.state import StockState
from backend.app.agents.market_agent import market_agent

workflow = StateGraph(StockState)
workflow.add_node("market_agent", market_agent)
workflow.set_entry_point("market_agent")
workflow.add_edge("market_agent", END)
graph = workflow.compile()