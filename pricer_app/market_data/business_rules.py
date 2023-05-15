"""
This module contains the business rules for the market data.

Expiry rules:

These are specific to each exchange; as an example these can have not just different
holiday dates between countries but also different rules for when the expiry date is set.

Validators:

Verify data is in the correct format, e.g contract notation (see ContractNotationValidator), also verify
that data is known - e.g. exchange codes and asset codes must be ones that the system knows about,
so that the correct expiry dates can be calculated.
"""
import re

from typing import Dict, Type
from typing_extensions import Self
import pandas_market_calendars as mcal
import pandas as pd
from datetime import date
from abc import ABC, abstractmethod
import pytest


# Expiry rules for particular assets on particular exchanges.
# If there were more than two examples, it may turn out that some rules generalise across more
# than one exchange or asset, in which case some base classes could be implemented.
class ExpiryRule(ABC):
    asset_code: str

    @abstractmethod
    def calculate_expiry(self, delivery_month: date) -> date:
        pass

    @classmethod
    def get_expiry_rule(cls, exchange_code: str, assert_code: str) -> Self:
        """
        Given an exchange code and an asset code, return the expiry rule for that asset on that exchange.

        :param exchange_code:
        :param assert_code:
        :return: instance of the expiry rule.
        :raises: ValueError if the exchange or asset code is not known.
        """
        exchange = Exchange.get_exchange(exchange_code)
        return exchange.get_expiry_rule(assert_code)


class BRNExpiryRule(ExpiryRule):
    # specific to the ICE exchange
    asset_code = "BRN"

    def calculate_expiry(self, delivery_month: date) -> date:
        """
        Get the expiry date for a BRN option contract.

        The expiry date is the last business day of the second month before the delivery month.
        """
        # Get the ICE calendar
        ice_calendar = mcal.get_calendar("ICE")

        # Find the last business day of the second month before the delivery month
        second_month_before = delivery_month - pd.DateOffset(months=2)
        second_month_before_end = second_month_before.replace(day=1) - pd.DateOffset(
            days=1
        )
        schedule = ice_calendar.schedule(
            start_date=second_month_before.replace(day=1),
            end_date=second_month_before_end,
        )
        return schedule.iloc[-1].name.date()


class HHExpiryRule(ExpiryRule):
    # specific to the NYMEX exchange
    asset_code = "HH"

    def calculate_expiry(self, delivery_month: date) -> date:
        """
        Get the expiry date for an HH option contract.

        The expiry date is the last business day of the month before the delivery month.
        """
        # Get the NYMEX calendar
        nymex_calendar = mcal.get_calendar("NYMEX")

        # Find the last business day of the month before the delivery month
        month_before = delivery_month - pd.DateOffset(months=1)
        month_before_end = month_before.replace(day=1) - pd.DateOffset(days=1)
        schedule = nymex_calendar.schedule(
            start_date=month_before.replace(day=1), end_date=month_before_end
        )
        return schedule.iloc[-1].name.date()


# Exchanges - associate an exchange code with a set of expiry rules
class Exchange(ABC):
    # The exchange code, set in the subclass:
    name: str
    # A dictionary of {asset_code: ExpiryRule} pairs, set in the subclass:
    expiry_rules: Dict[str, Type["ExpiryRule"]]

    def get_expiry_rule(self, asset_code: str) -> "ExpiryRule":
        """
        Get the expiry rule for a given asset code, or raise a ValueError if no expiry rule is found.

        :param asset_code:
        :return:
        """
        if asset_code in self.expiry_rules:
            return self.expiry_rules[asset_code]()
        raise ValueError(f"No expiry rule found for asset code: {asset_code}")

    @classmethod
    def get_exchange(cls, exchange_code: str) -> Self:
        """
        Get the exchange object for a given exchange code, or raise a ValueError if no exchange is found.

        :param exchange_code:
        :return: instance of Exchange subclass.
        """
        exchanges = {cls.name: cls for cls in Exchange.__subclasses__()}
        if exchange_code in exchanges:
            return exchanges[exchange_code]()
        raise ValueError(f"No exchange found with exchange_code: {exchange_code}")


class ICEExchange(Exchange):
    name = "ICE"
    expiry_rules = {"BRN": BRNExpiryRule}


class NYMEXExchange(Exchange):
    name = "NYMEX"
    expiry_rules = {"HH": HHExpiryRule}


class ContractNotationParser:
    """
    Contract notation is a string that describes the contract, e.g.
    "BRN Jun21 Call Strike 50.0 USD"

    This class provides parsing to a dictionary as well as validation that the
    expected fields are present.
    """
    NOTATION_FORMAT = (
        r"(?P<asset>\w+)\s+"
        r"(?P<expiration_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?P<expiration_year>\d{2})\s+"
        r"(?P<option_type>Call|Put)\s+"
        r"Strike\s+"
        r"(?P<strike_price>\d+(?:\.\d+)?)\s+(?P<unit>[\w/]+)"
    )

    @classmethod
    def validate(cls, contract_notation: str) -> bool:
        if not re.match(cls.NOTATION_FORMAT, contract_notation):
            raise ValueError(f"Invalid contract notation: {contract_notation}")

    @classmethod
    def parse(cls, contract_notation: str) -> Dict[str, str]:
        """
        Parse a contract notation string into a dictionary.

        If the contract notation is invalid, a ValueError is raised (see `validate`).

        :param contract_notation:
        :return:
        """
        match = re.match(cls.NOTATION_FORMAT, contract_notation)
        cls.validate(contract_notation)
        return match.groupdict()




# Example usage
# ice = get_exchange("ICE")
# brn_rule = ice.get_expiry_rule("BRN")
# brn_expiry = brn_rule.get_expiry(date(2024, 1, 1))
# print(f"BRN Jan-24 expiry date: {brn_expiry}")
#
# nymex = get_exchange("NYMEX")
# hh_rule = nymex.get_expiry_rule("HH")
# hh_expiry = hh_rule.get_expiry(date(2024, 3, 1))
# print(f"HH Mar-24 expiry date: {hh_expiry}")


# Run the tests with pytest
if __name__ == "__main__":
    pytest.main([__file__])
