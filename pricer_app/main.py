from contextlib import asynccontextmanager

from fastapi import FastAPI

from pricer_app.database import create_db_and_tables

from pricer_app.market_data.routes import router as market_data_router
from pricer_app.market_data.models import (
    MarketData,
)  # noqa - this is used in the create_db_and_tables function
from pricer_app.option_pricing.routes import router as option_router
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "").split(",")

app = FastAPI()

app.include_router(market_data_router, tags=["market_data"])
app.include_router(option_router, tags=["option_pricing"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
