from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..market_data.models import MarketData

from .schemas import OptionPricingData
from .pricing import black76
from ..market_data.schemas import MarketDataRetrieve

router = APIRouter()


@router.post("/option_pricing/{option_id}")
async def calculate_option_pv(
    option_id: int,
    option_data: OptionPricingData,
    session: Session = Depends(get_session),
) -> dict:
    """
    Endpoint for calculating the present value (PV) of an option.

    Returns a dictionary containing the present value of the option.

    Raises a 404 error if the option market data object does not exist.
    Raises a 400 error if the option pricing data is invalid (see `pricer_app.pricing.black76`).

    :option_id: int: The ID of the option market data object.
    :option_data: OptionPricingData: The option pricing data, containing the option type [Call/Put] and strike price [K}.

    :return: dict: A dictionary containing the present value of the option as calculated by the Black-76 model.
    """
    option_market_data_instance = session.exec(
        select(MarketData).where(MarketData.id == option_id)
    ).first()

    if option_market_data_instance is None:
        raise HTTPException(status_code=404, detail="Option market data not found.")

    market_data = MarketDataRetrieve.convert_market_data_from_json(
        option_market_data_instance.market_data
    )

    F = market_data["forward_price"]
    r = market_data["risk_free_interest_rate"]
    sigma = market_data["volatility"]
    T = market_data["time_to_expiration"]

    try:
        pv = black76(option_data.option_type, F, option_data.K, r, sigma, T)
        return {"pv": pv}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e.args[0]))
