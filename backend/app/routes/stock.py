from fastapi import APIRouter, HTTPException
from backend.app.services.stock_service import get_stock_data

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)


@router.post("/analyze")
def analyze_stock(ticker: str):
    try:
        data = get_stock_data(ticker)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )