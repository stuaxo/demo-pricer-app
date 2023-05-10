import pytest

from ..business_rules import BRNExpiryRule, ExpiryRule, HHExpiryRule


# Parameterized unit test for valid data
@pytest.mark.parametrize(
    "exchange_code,asset_code,expected_type",
    [("ICE", "BRN", BRNExpiryRule), ("NYMEX", "HH", HHExpiryRule)],
)
def test_get_expiry_rule_valid_data(
    exchange_code: str, asset_code: str, expected_type: ExpiryRule
):
    rule = ExpiryRule.get_expiry_rule(exchange_code, asset_code)
    assert isinstance(rule, expected_type)


# Parameterized unit test for invalid data
@pytest.mark.parametrize(
    "exchange_code,asset_code,error_message",
    [
        ("INVALID", "BRN", "No exchange found with exchange_code: INVALID"),
        ("ICE", "INVALID", "No expiry rule found for asset code: INVALID"),
        ("NYMEX", "INVALID", "No expiry rule found for asset code: INVALID"),
        ("INVALID", "INVALID", "No exchange found with exchange_code: INVALID"),
    ],
)
def test_get_expiry_rule_invalid_data(
    exchange_code: str, asset_code: str, error_message: str
):
    with pytest.raises(ValueError) as e:
        ExpiryRule.get_expiry_rule(exchange_code, asset_code)
    assert str(e.value) == error_message


# Run the tests with pytest
if __name__ == "__main__":
    pytest.main([__file__])
