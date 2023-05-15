from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..market_data.models import MarketData, MarketData_Pydantic

from .schemas import OptionPricingData
from .pricing import black76

router = APIRouter()


@router.post("/option_pricing/{option_id}")
async def calculate_option_pv(option_id: int, option_data: OptionPricingData) -> dict:
    """
    Endpoint for calculating the present value (PV) of an option.

    Returns a dictionary containing the present value of the option.

    Raises a 404 error if the option market data object does not exist.
    Raises a 400 error if the option pricing data is invalid (see `pricer_app.pricing.black76`).
    """
    option_market_data = Session.exec(select(MarketData).where(MarketData.id == option_id)).first()

    if option_market_data is None:
        raise HTTPException(status_code=404, detail="Option market data not found.")

    F = option_market_data.market_data["F"]
    r = option_market_data.market_data["r"]
    sigma = option_market_data.market_data["sigma"]
    T = option_market_data.market_data["T"]

    try:
        pv = black76(option_data.option_type, F, option_data.K, r, sigma, T)
        return {"pv": pv}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e.args[0]))
