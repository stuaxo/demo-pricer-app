import json

import pytest
from pydantic import ValidationError

from .factories import MarketDataCreateFactory, ContractFactory
from ..schemas import Contract
from .helpers import assert_valid_contract


@pytest.mark.parametrize(
    "exchange_code,contract_string",
    [
        ("NYMEX", "BRN Jan24 Call Strike 100 USD/BBL"),
    ],
)
def test_valid_contract(exchange_code, contract_string):
    contract = ContractFactory()

    assert_valid_contract(contract)


@pytest.mark.parametrize(
    "exchange_code,contract_notation,expected_error_message", [
        ("INVALID", "BRN Jan21 Call Strike 50 USD/BBL", "No exchange found with exchange_code: INVALID"),
        ("NYMEX", "INVALID CONTRACT STRING", "Invalid contract notation: INVALID CONTRACT STRING"),
        ("NYMEX", "BRN Jan21 Call Strike 50", "Invalid contract notation: BRN Jan21 Call Strike 50"),
    ]
)
def test_invalid_contract(exchange_code, contract_notation, expected_error_message):
    with pytest.raises(ValueError) as ex_info:
        Contract.from_contract_notation(exchange_code, contract_notation)
    assert str(ex_info.value) == expected_error_message


@pytest.mark.parametrize(
    "pricing_model",
    [
        "Black76",
    ],
)
def test_valid_pricing_model(pricing_model):
    market_data_create = MarketDataCreateFactory(pricing_model=pricing_model)
    assert market_data_create.pricing_model == pricing_model


@pytest.mark.parametrize(
    "pricing_model",
    [
        "BlackScholes",
        "Binomial",
        "MonteCarlo",
    ],
)
def test_invalid_pricing_model(pricing_model):
    """
    Validate that only Black76 is supported.

    A failure here is a signal that other updates are probably required.
    """
    with pytest.raises(ValueError):
        MarketDataCreateFactory(pricing_model=pricing_model)


@pytest.mark.parametrize(
    "market_data",
    [
        {
            "forward_price": 100.0,
            "strike_price": 110.0,
            "time_to_expiration": 0.5,
            "volatility": 0.2,
            "risk_free_interest_rate": 0.03,
        },
    ],
)
def test_valid_market_data(market_data):
    market_data_create = MarketDataCreateFactory(
        pricing_model="Black76",
        market_data=market_data,
    )
    assert json.dumps(market_data) == market_data_create.market_data

@pytest.mark.parametrize(
    "market_data, expected_message",
    [
        (
            {
                "forward_price": 100.0,
                "strike_price": 110.0,
                "time_to_expiration": 0.5,
                "volatility": 0.2,
            },
            "Missing required fields for Black76 model: risk_free_interest_rate",
        ),
        (
            {
                "strike_price": 110.0,
                "time_to_expiration": 0.5,
                "volatility": 0.2,
                "risk_free_interest_rate": 0.03,
            },
            "Missing required fields for Black76 model: forward_price",
        ),
        (
            {
                "forward_price": 100.0,
                "time_to_expiration": 0.5,
                "volatility": 0.2,
                "risk_free_interest_rate": 0.03,
            },
            "Missing required fields for Black76 model: strike_price",
        ),
        (
            {
                "forward_price": 100.0,
                "strike_price": 110.0,
                "volatility": 0.2,
                "risk_free_interest_rate": 0.03,
            },
            "Missing required fields for Black76 model: time_to_expiration",
        ),
        (
            {
                "forward_price": 100.0,
                "strike_price": 110.0,
                "time_to_expiration": 0.5,
                "risk_free_interest_rate": 0.03,
            },
            "Missing required fields for Black76 model: volatility",
        ),
    ],
)
def test_invalid_market_data(market_data, expected_message):
    try:
        MarketDataCreateFactory(
            pricing_model="Black76",
            market_data=market_data,
        )
    except ValidationError as e:
        error_messages = str(e)
        assert (
            expected_message in error_messages
        ), f"Expected message '{expected_message}' not found in error messages: {error_messages}"
