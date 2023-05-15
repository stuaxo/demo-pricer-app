from fastapi import FastAPI
from pricer_app.database import create_db_and_tables
## from sqlmodel import SQLModel, create_engine
from pricer_app.market_data.routes import router as market_data_router
from pricer_app.market_data.models import MarketData  # noqa - this is used in the create_db_and_tables function
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "").split(",")

app = FastAPI()

app.include_router(market_data_router, tags=["market_data"])


# @app.on_event("startup")
# def create_db_and_tables():
#     print("Creating DB and tables ", DATABASE_URL)
#     engine = create_engine(DATABASE_URL)
#     with engine.begin() as connection:
#         SQLModel.metadata.create_all(connection)


# @app.on_event("startup")
# async def on_startup():
#     with engine.begin() as connection:
#         SQLModel.metadata.create_all(connection)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    create_db_and_tables()
else:
    create_db_and_tables()