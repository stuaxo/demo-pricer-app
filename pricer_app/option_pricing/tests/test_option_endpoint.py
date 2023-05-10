import pytest

from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "option_index, option_type, K, expected_status_code, expected_error_message",
    [
        (0, "call", 100.0, 200, None),
        (1, "put", 10.0, 200, None),
        (2, "call", 50.0, 200, None),
        (0, "invalid", 100.0, 422, "Invalid option type"),
        (1, "put", -10.0, 400, "Strike price (K) must be non-negative."),
    ],
)
@pytest.mark.asyncio
async def test_calculate_option_pv(
    client: TestClient,
    market_data_models,
    option_index,
    option_type,
    K,
    expected_status_code,
    expected_error_message,
):
    option_id = option_index + 1

    response = client.post(
        f"/option_pricing/{option_id}", json={"option_type": option_type, "K": K}
    )
    assert response.status_code == expected_status_code
    data = response.json()

    if response.status_code == 200:
        assert "pv" in data
        assert data["pv"] > 0
    elif response.status_code == 400:
        assert "detail" in data
        assert expected_error_message == data["detail"]
