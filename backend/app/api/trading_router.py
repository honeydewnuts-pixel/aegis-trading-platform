"""

Project : AEGIS
File : trading_router.py
Purpose : FastAPI endpoints for MT5 trading execution

"""

from fastapi import APIRouter, HTTPException, Depends
from app.services.mt5_execution_service import MT5ExecutionService
from app.schemas.trading import MarketOrderRequest, PendingOrderRequest, TradeExecutionResponse
from app.schemas.trading_entities import AccountInfo, Position, PendingOrder

router = APIRouter(prefix="/api/trading", tags=["Trading"])

# Singleton instance
execution_service = MT5ExecutionService()

@router.get("/health")
async def get_health():
    """Health check for MT5 connection"""
    return await execution_service.health_check()

@router.post("/connect")
async def connect(credentials: dict):
    """Connect to MT5 with login, password, server"""
    success = await execution_service.connect(credentials)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to connect to MT5")
    return {"status": "connected"}

@router.post("/market-order", response_model=TradeExecutionResponse)
async def place_market_order(request: MarketOrderRequest):
    """Place market buy/sell order"""
    result = await execution_service.execute_market_order(request)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result

@router.get("/account", response_model=AccountInfo | None)
async def get_account():
    """Get account info"""
    return await execution_service.get_account()

@router.get("/positions", response_model=list[Position])
async def get_positions():
    """Get all open positions"""
    return await execution_service.get_positions()

@router.get("/orders", response_model=list[PendingOrder])
async def get_pending_orders():
    """Get all pending orders"""
    return await execution_service.get_pending_orders()
