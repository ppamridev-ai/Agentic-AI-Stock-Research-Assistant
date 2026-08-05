from fastapi import APIRouter, HTTPException
from backend.app.graph.workflow import graph

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)


@router.post("/analyze")
def analyze_stock(ticker: str):
    try:
        result = graph.invoke(
            {
                "ticker": ticker,
                "stock_data":{}
            }
        )
        return result["stock_data"]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )