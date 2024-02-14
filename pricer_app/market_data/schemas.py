import json
from typing import Dict, Union, Optional, Any
from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    parse_obj_as,
    ValidationError,
)

from .business_rules import ContractNotationParser
from .validators import validate_exchange_code


class Contract(BaseModel):
    exchange_code: str
    asset: str
    expiration_month: str
    expiration_year: str
    option_type: str
    strike_price: float
    unit: str

    @staticmethod
    def from_contract_notation(
        exchange_code: str, contract_string: str
    ) -> Optional["Contract"]:
        """
        Create a Contract object from an exchange code and contract notation string.

        >>> Contract.from_contract_notation("NYMEX", "BRN JAN 21 Call Strike 50 USD/BBL")
        Contract(exchange_code='NYMEX', asset='BRN', expiration_month='JAN', expiration_year='21', option_type='Call', strike_price=50.0, unit='USD/BBL')

        :param exchange_code: valid exchange code (see `business_rules.py`)
        :param contract_string: valid contract notation string (see `business_rules.py`)
        :raises: ValueError if exchange_code or contract_string is not valid.
        :return: instance of Contract.
        """
        validate_exchange_code(exchange_code)

        # ContractNotationParser also validates: it raises a ValueError if the contract_string is not valid.
        parsed_data = ContractNotationParser.parse(contract_string)
        return Contract(exchange_code=exchange_code, **parsed_data)

    def to_notation_data(self):
        """
        :return: a string in contract notation format, e.g. "BRN Jun21 Call Strike 50.0 USD"
        """
        return f"{self.asset} {self.expiration_month}{self.expiration_year} {self.option_type} Strike {self.strike_price} {self.unit}"


class PricingModel(BaseModel):
    pass


class Black76PricingModel(PricingModel):
    forward_price: float
    strike_price: float
    time_to_expiration: float
    volatility: float
    risk_free_interest_rate: float


class MarketDataCreate(BaseModel):
    """
    MarketDataCreate is the input data for creating a MarketData object in the database.
    """

    exchange_code: str

    # contract is stored in contract notation format, e.g. "BRN Jun21 Call Strike 50.0 USD"
    contract: str
    pricing_model: str
    market_data: str

    @field_validator("exchange_code")
    def validate_exchange_code(cls, exchange_code):  # noqa:
        validate_exchange_code(exchange_code)
        return exchange_code

    @field_validator("contract")
    def validate_contract(cls, contract, values, **kwargs):  # noqa:
        """
        Validate the contract notation string and exchange code.
        """
        ContractNotationParser.validate(contract)
        return contract

    @field_validator("pricing_model")
    def only_allow_supported_pricing_models(cls, pricing_model):  # noqa:
        supported_models = ["Black76"]
        if pricing_model not in supported_models:
            raise ValueError(
                f"Unsupported pricing model. Supported models: {', '.join(supported_models)}"
            )
        return pricing_model

    @model_validator(mode="after")
    def validate_market_data(cls, values):  # noqa:
        market_data = values.market_data
        pricing_model = values.pricing_model

        # Convert market_data to a dictionary if it is a JSON string
        if isinstance(market_data, str):
            market_data = json.loads(market_data)

        if pricing_model == "Black76":
            try:
                market_data_validated = parse_obj_as(Black76PricingModel, market_data)
                values[
                    "market_data"
                ] = (
                    market_data_validated.json()
                )  # Convert back to JSON string if needed
            except ValidationError as e:
                raise ValueError(f"Validation error for Black76 model: {e}")

            required_fields = {
                "forward_price",
                "strike_price",
                "time_to_expiration",
                "volatility",
                "risk_free_interest_rate",
            }
            missing_fields = required_fields - market_data.keys()
            if missing_fields:
                raise ValueError(
                    f"Missing required fields for {pricing_model} model: {', '.join(missing_fields)}"
                )

        # Modify values directly if needed
        values.market_data = json.dumps(market_data)
        return values

    @model_validator(mode="before")
    def convert_market_data_to_json(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert the market_data dictionary to a JSON string before storing in the database
        (sqlite does not have json fields at the time of writing.)
        """
        market_data = values.get("market_data")
        if isinstance(market_data, dict):
            values["market_data"] = json.dumps(market_data)
        return values


class MarketDataRetrieve(MarketDataCreate):
    """
    MarketDataRetrieve is the output data for retrieving a MarketData object from the database.
    """

    id: int
    contract: Contract
    market_data: PricingModel
    upload_timestamp: str

    @field_validator("contract")
    def validate_contract(cls, contract, values):  # noqa:
        """
        Convert contract notation string to Contract object.
        """
        if isinstance(contract, str):
            exchange_code = values["market_data"]["exchange_code"]
            return Contract.from_contract_notation(exchange_code, contract)
        return contract

    @field_validator("market_data")
    def convert_market_data_from_json(cls, market_data: str) -> Dict[str, Any]:
        """
        Convert the market_data JSON string to a dictionary after retrieving from the database.
        """
        if isinstance(market_data, str):
            return json.loads(market_data)
        return market_data

    class Config:
        from_attributes = True
