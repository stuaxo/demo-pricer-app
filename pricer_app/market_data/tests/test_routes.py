import json
from typing import List
from fastapi.testclient import TestClient
from pricer_app.market_data.schemas import MarketDataCreate, MarketDataRetrieve


def test_upload_market_data(client: TestClient):
    market_data = {
        "exchange_code": "NYMEX",
        "contract": "BRN Jan24 Call Strike 100 USD/BBL",
        "pricing_model": "Black76",
        "market_data": {
            "forward_price": 95.0,
            "strike_price": 100.0,
            "time_to_expiration": 0.5,
            "volatility": 0.25,
            "risk_free_interest_rate": 0.03,
        },
    }
    response = client.post("/market_data", json=market_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["exchange_code"] == market_data["exchange_code"]
    assert data["contract"] == market_data["contract"]


def test_get_all_market_data(
    client: TestClient, market_data_models: List[MarketDataCreate], raw_market_data
):
    response = client.get("/market_data")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == len(raw_market_data)


def test_get_market_data(
    client: TestClient, market_data_models: List[MarketDataCreate]
):
    market_data_id = 1
    response = client.get(f"/market_data/{market_data_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == market_data_id
    assert isinstance(data["contract"], str)  # contract notation
    assert isinstance(data["market_data"], str)  # serialized JSON
    json.loads(data["market_data"])  # check that it is valid JSON


def test_get_market_data_not_found(client: TestClient):
    market_data_id = 999
    response = client.get(f"/market_data/{market_data_id}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Option not found"
