import json
from sqlmodel import select

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

from pricer_app.database import get_session
from pricer_app.main import app
from pricer_app.settings import settings
from pricer_app.market_data.models import MarketData

from pricer_app.market_data.tests.factories import MarketDataCreateFactory


@pytest.fixture(scope="function")
def session():
    engine = create_engine(settings.test_database_url, echo=True)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create a new session
    with Session(engine) as session:
        yield session  # The test will run here with the session

        session.rollback()

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(session: Session):
    # The app dependency overrides go here.

    # This is just an example, actual implementation might differ
    app.dependency_overrides[get_session] = lambda: session

    # Create a TestClient using the FastAPI app
    with TestClient(app) as test_client:
        yield test_client

    # Clean up / remove overrides after tests are done
    app.dependency_overrides.clear()


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
        (
            "NYMEX",
            "BRN Jan24 Call Strike 100 USD/BBL",
            {
                "forward_price": 95.0,
                "time_to_expiration": 0.5,
                "risk_free_interest_rate": 0.03,
                "volatility": 0.25,
                "strike_price": 100.0,
            },
        ),
        (
            "ICE",
            "HH Mar24 Put Strike 10 USD/MMBTu",
            {
                "forward_price": 10.0,
                "time_to_expiration": 0.7,
                "risk_free_interest_rate": 0.02,
                "volatility": 0.3,
                "strike_price": 10.0,
            },
        ),
    ]

    return valid_market_data


@pytest.fixture(scope="function")
def market_data_models(raw_market_data, session):
    for exchange_code, contract, market_data in raw_market_data:
        model_data = {
            "exchange_code": exchange_code,
            "contract": contract,
            "market_data": json.dumps(market_data),
        }
        model = MarketDataCreateFactory(**model_data)
        db_model = MarketData(**model.dict())
        session.add(db_model)
    session.commit()

    # Re-fetch models to get IDs
    models = session.exec(select(MarketData)).all()
    return models
