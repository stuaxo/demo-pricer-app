import factory as fb
from functools import partial
from typing import Optional, Any, Type

from ..business_rules import Exchange
from ..schemas import Contract
from ..validators import validate_exchange_code, validate_contract_notation


def get_valid_exchange_code_for_commodity(commodity: str) -> str:
    """
    Get a valid exchange code for a given commodity.

    This is a helper function for the ContractFactory. It is used to ensure that
    the exchange_code and asset are valid for each other.
    """
    for exchange in Exchange.__subclasses__():
        if commodity in exchange.expiry_rules:
            return exchange.name


def assert_valid_contract(contract: Contract):
    """
    Assert that a contract is valid.

    This is a helper function for the ContractFactory. It is used to ensure that
    the exchange_code and asset are valid for each other.
    """
    validate_exchange_code(contract.exchange_code)
    exchange = Exchange.get_exchange(contract.exchange_code)
    assert exchange is not None
    assert contract.asset in exchange.expiry_rules.keys()

    # Contract fields are good for completeness verify round trip to notation
    notation = contract.to_notation_data()
    validate_contract_notation(notation)
