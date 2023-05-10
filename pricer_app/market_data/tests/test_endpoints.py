import pytest

from fastapi import FastAPI
from httpx import AsyncClient

from pricer_app.market_data.models import MarketData
from pricer_app.market_data.routes import router as market_data_router

app = FastAPI()
app.include_router(market_data_router)


@pytest.mark.anyio
async def test_get_all_market_data_endpoint(client: AsyncClient, market_data_models):
    all_option_market_data = await MarketData.all()
    response = await client.get("/market_data")
    assert response.status_code == 200
    assert len(response.json()) > 0
    for idx, item in enumerate(response.json()):
        assert item["id"] == idx + 1
        assert "underlying_price" in item
        assert "volatility" in item
        assert "expiration_date" in item
        assert "risk_free_rate" in item


# @pytest.mark.anyio
# async def test_get_market_data_by_id_endpoint(client: AsyncClient):
#     # Replace the endpoint and id with your actual values
#     endpoint = "/market_data/"
#     id = 1
#
#     response = await client.get(endpoint + str(id))
#     # Add the rest of your test code


# @pytest.mark.asyncio
# async def test_get_market_data_by_id_endpoint(client, option_market_data):
#     # Replace the endpoint and id with your actual values
#     endpoint = "/market_data/"
#     id = 1
#
#     response = await client.get(endpoint + str(id))
#     assert response.status_code == 200
#     # Additional assertions


@pytest.mark.anyio
async def test_get_market_data_by_id_endpoint(client):
    option_id = 2
    response = await client.get(f"/market_data/{option_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == option_id
    assert "underlying_price" in data
    assert "volatility" in data
    assert "expiration_date" in data
    assert "risk_free_rate" in data


#
#
# @pytest.mark.asyncio
# async def test_get_market_data_invalid_id(option_market_data):
#     """
#     Verify that a 404 is returned when an invalid option id is provided
#     """
#     invalid_option_id = 999
#     async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
#         response = await client.get(f"/market_data/{invalid_option_id}")
#
#     assert response.status_code == 404
