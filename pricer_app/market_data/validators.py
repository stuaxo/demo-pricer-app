from pricer_app.market_data.business_rules import ContractNotationParser, Exchange


def validate_exchange_code(exchange_code: str) -> bool:
    """
    :raise: a ValueError if the exchange_code is not valid implementation of Exchange with a matching exchange_code
    """
    if not Exchange.get_exchange(exchange_code):
        raise ValueError(f"No exchange found with exchange_code: {exchange_code}")


validate_contract_notation = ContractNotationParser.validate
