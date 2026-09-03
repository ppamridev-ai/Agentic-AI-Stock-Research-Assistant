from app.observability import configure_observability, instrumented

configure_observability()

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from app.state import InvestmentState
from app.tools.market import fetch_fundamental_data, calculate_technical_indicators, fetch_news_sentiment


@instrumented("fundamental", output_key="fundamental_data")
def fundamental_agent(state: InvestmentState) -> dict:
    ticker = state["ticker"]
    return {"fundamental_data": fetch_fundamental_data(ticker)}


@instrumented("technical", output_key="technical_data")
def technical_agent(state: InvestmentState) -> dict:
    ticker = state["ticker"]
    return {"technical_data": calculate_technical_indicators(ticker)}


@instrumented("news", output_key="news_data")
def news_agent(state: InvestmentState) -> dict:
    ticker = state["ticker"]
    return {"news_data": fetch_news_sentiment(ticker)}


def risk_manager_agent(llm: ChatOpenAI):
    @instrumented("risk_manager")
    def _risk_manager_agent(state: InvestmentState) -> dict:
        ticker = state["ticker"]
        prompt = f"""You are a Senior Risk Manager evaluating {ticker}.
        Review these findings:
        Fundamentals: {state.get("fundamental_data", {})}
        Technicals: {state.get("technical_data", {})}
        News: {state.get("news_data", {})}

        Provide a rigorous "Devil's Advocate" risk assessment. What could go wrong with an investment here?
        Use only the data above. Do not invent metrics."""
        response = llm.invoke(prompt)
        return {"risk_assessment": response.content}

    return _risk_manager_agent


def final_synthesizer_agent(llm: ChatOpenAI):
    @instrumented("synthesizer")
    def _final_synthesizer_agent(state: InvestmentState) -> dict:
        ticker = state["ticker"]
        prompt = f"""You are the Chief Investment Officer. Synthesize the research for {ticker}:
        Fundamentals: {state.get("fundamental_data")}
        Technicals: {state.get("technical_data")}
        News: {state.get("news_data")}
        Risk Analysis: {state.get("risk_assessment")}

        Provide a clear, structured Investment Thesis with Bull Case, Bear Case, and Final Actionable Rating (Buy, Hold, or Sell).
        The rating line must include exactly one of: Buy, Hold, or Sell.
        Use only the data above. Do not invent metrics."""
        response = llm.invoke(prompt)
        return {"final_recommendation": response.content}

    return _final_synthesizer_agent


def build_graph(llm: ChatOpenAI | None = None):
    llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    workflow = StateGraph(InvestmentState)
    workflow.add_node("fundamental", fundamental_agent)
    workflow.add_node("technical", technical_agent)
    workflow.add_node("news", news_agent)
    workflow.add_node("risk_manager", risk_manager_agent(llm))
    workflow.add_node("synthesizer", final_synthesizer_agent(llm))
    workflow.add_edge(START, "fundamental")
    workflow.add_edge(START, "technical")
    workflow.add_edge(START, "news")
    workflow.add_edge(["fundamental", "technical", "news"], "risk_manager")
    workflow.add_edge("risk_manager", "synthesizer")
    workflow.add_edge("synthesizer", END)
    return workflow.compile()


app_graph = build_graph()
