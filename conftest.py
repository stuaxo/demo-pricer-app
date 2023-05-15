import json

import pytest
from fastapi.testclient import TestClient

from pricer_app.database import create_db_and_tables
from pricer_app.main import app

from pricer_app.market_data.tests.factories import MarketDataCreateFactory


@pytest.fixture(scope="session")
def client():
    create_db_and_tables()
    yield TestClient(app)


@pytest.fixture
def raw_market_data():
    """
    Base data fixture, returns a list of tuples: [(option_code, market_data_dict), ...]
    suitable for creating OptionMarketData objects with OptionCreate(**market_data_dict)

    Market data contains information such as the future price, time to expiration, risk-free rate, and volatility.

    Example of an option:
    BRN Jan24 Call Strike 100 USD/BBL (Brent Crude Oil option for January 2024 with a call option at a strike price of $100 per barrel)

    This enables assert_market_data_valid.

    Caveats: option_code must be unique, all data is stored in memory - but it's not enough to matter.
    """
    valid_market_data = [
        ("NYMEX", "BRN Jan24 Call Strike 100 USD/BBL",
         {"forward_price": 95.0, "time_to_expiration": 0.5, "risk_free_interest_rate": 0.03, "volatility": 0.25,
          "strike_price": 100.0}),
        ("ICE", "HH Mar24 Put Strike 10 USD/MMBTu",
         {"forward_price": 10.0, "time_to_expiration": 0.7, "risk_free_interest_rate": 0.02, "volatility": 0.3,
          "strike_price": 10.0}),
    ]

    return valid_market_data


@pytest.fixture
def market_data_models(raw_market_data):
    """
    Returns a list of MarketDataCreate models containing data from raw_market_data.
    """
    models = []
    for exchange_code, contract, market_data in raw_market_data:
        model_data = {
            'exchange_code': exchange_code,
            'contract': contract,
            'market_data': market_data
        }
        import ipdb
        with ipdb.launch_ipdb_on_exception():
            model = MarketDataCreateFactory(**model_data)
        models.append(model)
    return models
