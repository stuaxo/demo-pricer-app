"""
Test market_data routes.

Unit testing the routes (as opposed to just end-to-end tests with the test-client ensures there is a sane way
of debugging them in isolation.
"""
import pytest
from fastapi import HTTPException

from ..models import MarketData_Pydantic
from ..routes import upload_market_data
from .factories import MarketDataCreateFactory


@pytest.mark.anyio
async def test_upload_market_data_direct_call(initialize_tests):
    market_data_create = MarketDataCreateFactory()

    try:
        result = await upload_market_data(option=market_data_create)
    except HTTPException as e:
        assert False, f"Unexpected HTTPException: {e}"

    assert isinstance(result, MarketData_Pydantic)
    assert result.exchange_code == market_data_create.exchange_code
    assert result.contract == market_data_create.contract
    assert result.pricing_model == market_data_create.pricing_model
    assert result.market_data == market_data_create.market_data
