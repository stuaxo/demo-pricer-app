from typing import Dict

from sqlmodel import SQLModel, Field
from datetime import datetime


class MarketData(SQLModel, table=True):
    """
    Model for storing option market data in the database.
    """
    # requirement: Upload and store market data in the database
    id: int = Field(default=None, primary_key=True)
    # contract is stored using contract notation.
    contract: str
    # market_data is stored as a JSON string.
    market_data: str
    exchange_code: str
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())