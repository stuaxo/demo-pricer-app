import factory

from ..business_rules import Exchange, ContractNotationParser
from ..schemas import MarketDataCreate
from ..schemas import Contract


class ContractFactory(factory.Factory):
    class Meta:
        model = Contract

    # get_valid_exchange_code_for_commodity ensures valid combinations of exchange_code and asset
    exchange_code = factory.SelfAttribute('original_contract.exchange_code')
    exchange_code = factory.LazyAttribute(
       lambda o: get_valid_exchange_code_for_commodity(o.asset)
    )
    asset = factory.Faker("random_element", elements=["BRN", "HH"])

    # expiration_month is first 3 characters of month name:
    expiration_month = factory.Faker("date", pattern="%b")

    # expiration_year is a 2 digit year
    expiration_year = factory.Faker("date", pattern="%y")
    option_type = factory.Faker("random_element", elements=["Call", "Put"])

    # strike_price is a positive number with 4 digits before decimal, 2 digits after
    strike_price = factory.Faker("pyfloat", left_digits=4, right_digits=2, positive=True)
    unit = factory.Faker("random_element", elements=["USD/BBL", "USD/MMBtu"])


class ContractNotationFactory(factory.Factory):
    """
    Generate valid contract notation strings,
    delegates to ContractFactory for the underlying data.
    """
    class Meta:
        model = str

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        contract = ContractFactory()
        return contract.to_notation_data()


class MarketDataCreateFactory(factory.Factory):
    class Meta:
        model = MarketDataCreate

    class Params:
        # This contract is a contract instance, not a contract notation string.
        # We use it to get the exchange_code, which we need to create a valid contract notation string.
        original_contract = factory.SubFactory(ContractFactory)

    # Once contract is created, we can use it to get the exchange_code
    exchange_code = factory.SelfAttribute('original_contract.exchange_code')

    # contract is stored in contract notation format, e.g. "BRN Jun21 Call Strike 50.0 USD"
    contract = factory.LazyAttribute(
        lambda o: o.original_contract.to_notation_data()  # noqa:
    )

    pricing_model = "Black76"
    market_data = factory.Dict(
        {
            "forward_price": factory.Faker("pyfloat", left_digits=4, right_digits=2),
            "strike_price": factory.Faker("pyfloat", left_digits=4, right_digits=2),
            "time_to_expiration": factory.Faker(
                "pyfloat", left_digits=1, right_digits=2
            ),
            "volatility": factory.Faker("pyfloat", left_digits=1, right_digits=2),
            "risk_free_interest_rate": factory.Faker(
                "pyfloat", left_digits=1, right_digits=2
            ),
        }
    )


def get_valid_exchange_code_for_commodity(commodity: str) -> str:
    """
    Get a valid exchange code for a given commodity.

    This is a helper function for the ContractFactory
    It is used to ensure valid combinations of exchange_code and asset.
    """
    for exchange in Exchange.__subclasses__():
        if commodity in exchange.expiry_rules:
            return exchange.name
