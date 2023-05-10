import factory as fb
from functools import partial
from typing import Optional, Any, Type

from pricer_app.market_data.business_rules import Exchange


def get_valid_exchange_code_for_commodity(commodity: str) -> str:
    """
    Get a valid exchange code for a given commodity.

    This is a helper function for the ContractFactory. It is used to ensure that
    the exchange_code and asset are valid for each other.
    """
    for exchange in Exchange.__subclasses__():
        if commodity in exchange.expiry_rules:
            return exchange.name
