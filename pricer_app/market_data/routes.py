import os

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, delete
from .models import MarketData
from .schemas import MarketDataCreate
from ..database import get_session

router = APIRouter()


@router.post("/market_data")
async def upload_market_data(option: MarketDataCreate, session: Session = Depends(get_session)):
    MarketDataCreate.validate(option.dict())
    MarketData.validate(option.dict())
    market_data = MarketData(market_data=option.market_data, contract=option.contract, exchange_code=option.exchange_code)

    # First, remove existing data:
    delete_query = delete(MarketData).where(
        (MarketData.exchange_code == market_data.exchange_code) &
        (MarketData.contract == market_data.contract)
    )
    session.exec(delete_query)

    session.add(market_data)
    session.commit()
    session.refresh(market_data)
    return market_data


@router.get("/market_data")
async def get_all_market_data(session: Session = Depends(get_session)):
    market_data = [*session.exec(select(MarketData)).all()]
    return market_data


@router.get("/market_data/{option_id}")
async def get_market_data(option_id: int, session: Session = Depends(get_session)):
    market_data = session.get(MarketData, option_id)
    if not market_data:
        raise HTTPException(status_code=404, detail="Option not found")
    return market_data
