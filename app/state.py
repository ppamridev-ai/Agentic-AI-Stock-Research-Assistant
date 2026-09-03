import operator
from typing import Annotated, TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FundamentalMetrics(BaseModel):
    pe_ratio: Optional[float] = Field(description="Price-to-Earnings Ratio")
    market_cap: Optional[float] = Field(description="Market Capitalization")
    revenue_growth: Optional[float] = Field(description="YoY Revenue Growth Rate")
    free_cash_flow: Optional[float] = Field(description="Free Cash Flow in USD")
    summary: str = Field(description="Fundamental assessment summary")

class TechnicalAnalysis(BaseModel):
    rsi_14: Optional[float] = Field(description="Relative Strength Index (14 day)")
    sma_50: Optional[float] = Field(description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(description="200-day Simple Moving Average")
    trend: str = Field(description="Overall technical trend: Bullish, Bearish, or Neutral")
    summary: str = Field(description="Technical analysis summary")

class NewsSentiment(BaseModel):
    sentiment_score: float = Field(description="Score between -1.0 (bearish) and 1.0 (bullish)")
    key_headlines: List[str] = Field(default_factory=list)
    summary: str = Field(description="News sentiment summary")

class InvestmentState(TypedDict):
    ticker: str
    fundamental_data: Optional[Dict[str, Any]]
    technical_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    risk_assessment: Optional[str]
    final_recommendation: Optional[str]
    errors: Annotated[List[str], operator.add]
    run_trace: Annotated[List[Dict[str, Any]], operator.add]