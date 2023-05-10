from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


class MarketData(Model):
    """
    Model for storing option market data in the database.
    """
    # requirement: Upload and store market data in the database
    id = fields.IntField(pk=True)
    # contract is stored using contract notation.
    contract = fields.CharField(255)
    market_data = fields.JSONField()
    upload_timestamp = fields.DatetimeField(auto_now_add=True)


MarketData_Pydantic = pydantic_model_creator(MarketData, name="MarketData")  # noqa
