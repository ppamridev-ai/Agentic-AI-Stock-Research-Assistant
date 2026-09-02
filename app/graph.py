import os
import dotenv
dotenv.load_dotenv()
from langgraph.graph import StateGraph, START,END
from langchain_openai import ChatOpenAI
from app.state import InvestmentState
from app.tools.market import fetch_fundamental_data, calculate_technical_indicators, fetch_news_sentiment

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


# --- Agent Nodes ---


def fundamental_agent(state: InvestmentState) -> InvestmentState:
    ticker = state["ticker"]
    data = fetch_fundamental_data(ticker)
    return {"fundamental_data": data}

def technical_agent(state: InvestmentState) -> InvestmentState:
    ticker = state["ticker"]
    data = calculate_technical_indicators(ticker)
    return {"technical_data": data}

def news_agent(state: InvestmentState) -> InvestmentState:
    ticker = state["ticker"]
    data = fetch_news_sentiment(ticker)
    return {"news_data": data}

def risk_manager_agent(state: InvestmentState) -> InvestmentState:
    """Devil's Advocate Node: Evaluates risks and potential pitfalls."""
    ticker = state["ticker"]
    fund = state.get("fundamental_data", {})
    tech = state.get("technical_data", {})
    
    prompt = f"""You are a Senior Risk Manager evaluating {ticker}.
    Review these fundamental and technical findings:
    Fundamentals: {fund}
    Technicals: {tech}
    
    Provide a rigorous "Devil's Advocate" risk assessment. What could go wrong with an investment here?"""
    
    response = llm.invoke(prompt)
    return {"risk_assessment": response.content}

def final_synthesizer_agent(state: InvestmentState) -> InvestmentState:
    ticker = state["ticker"]
    prompt = f"""You are the Chief Investment Officer. Synthesize the research for {ticker}:
    Fundamentals: {state.get('fundamental_data')}
    Technicals: {state.get('technical_data')}
    Risk Analysis: {state.get('risk_assessment')}
    
    Provide a clear, structured Investment Thesis with Bull Case, Bear Case, and Final Actionable Rating (Buy, Hold, or Sell)."""
    
    response = llm.invoke(prompt)
    return {"final_recommendation": response.content}

# --- Graph Assembly ---

workflow = StateGraph(InvestmentState)

# Add Nodes
workflow.add_node("fundamental", fundamental_agent)
workflow.add_node("technical", technical_agent)
workflow.add_node("news", news_agent)
workflow.add_node("risk_manager", risk_manager_agent)
workflow.add_node("synthesizer", final_synthesizer_agent)

# Set Parallel Execution for Data Gathering
workflow.add_edge(START, "fundamental")
workflow.add_edge(START, "technical")
workflow.add_edge(START, "news")
workflow.add_edge(["fundamental", "technical", "news"], "risk_manager")
workflow.add_edge("risk_manager", "synthesizer")
workflow.add_edge("synthesizer", END)

app_graph = workflow.compile()