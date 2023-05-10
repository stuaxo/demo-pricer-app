import logging
import pytest
from fastapi import HTTPException

from httpx import AsyncClient
from starlette.responses import JSONResponse
from tortoise import Tortoise
from tortoise.queryset import QuerySet

from pricer_app.main import app

from tortoise.contrib.test import finalizer, initializer
from pricer_app.market_data.models import MarketData
from pricer_app.market_data.schemas import MarketDataCreate


logger = logging.getLogger(__name__)

DB_URL = "sqlite://:memory:"


async def init_db(db_url, create_db: bool = False, schemas: bool = False) -> None:
    """Initial database connection"""
    await Tortoise.init(
        db_url=db_url,
        config={
            'apps': "pricer_app.market_data.models",
            'default_connection': "default",
        },
        modules={"models": ["pricer_app.market_data.models"]},
        _create_db=create_db,
    )
    if create_db:
        logger.debug(f"Database created! {db_url = }")
    if schemas:
        await Tortoise.generate_schemas()
        logger.debug("Success to generate schemas")


async def init(db_url: str = DB_URL):
    await init_db(db_url, True, True)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://localhost/test-app") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await init()
    yield
    await Tortoise._drop_databases()
    logger.info("Database dropped!")


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
        ("BRN_Jan24_Call_100", {"F": 95.0, "T": 0.5, "r": 0.03, "sigma": 0.25}),
        ("HH_Mar24_Put_10", {"F": 10.0, "T": 0.7, "r": 0.02, "sigma": 0.3}),
    ]

    return {option_code: market_data for option_code, market_data in valid_market_data}


def assert_valid_market_data(option, raw_market_data):
    """
    This slightly cheats:  it can only validate data known in raw_market_data.
    """
    # Lookup the option code in the raw_market_data fixture
    assert (
        option.code in raw_market_data
    ), f"Option code {option.code} not found in raw_market_data"
    # All the fields should match
    assert option.market_data == raw_market_data[option.code][1]

    # Validate the actual data:


# Fixture to hold plain data


@pytest.fixture
def market_data_schemas(raw_market_data):
    """
    Return a list of plain option market data using the OptionCreate schema
    (ensuring that the correct fields are present).

    Data is sourced from the `raw_market_data fixture`, see `raw_market_data` for information on options data.
    """

    return [
        MarketDataCreate(code=option_code, market_data=market_data)
        for option_code, market_data in raw_market_data.items()
    ]


# Fixture to hold Tortoise model instances
@pytest.fixture
async def market_data_models(initialize_tests, market_data_schemas):
    """
    Ensures test data is populated with data specified in the `market_data_schemas` fixture and returns it.

    See `market_data_schemas` for information on options data.
    """
    # initializer(["pricer_app.market_data.models"])

    all_options = [
        await MarketData.create(**option.dict()) for option in market_data_schemas
    ]
    yield all_options

    QuerySet(MarketData).filter(
        code__in=[option.code for option in market_data_schemas]
    ).delete()
    # finalizer()
