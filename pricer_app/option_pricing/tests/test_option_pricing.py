import re

import pytest

from pricer_app.option_pricing.enums import OptionType
from pricer_app.option_pricing.pricing import black76


@pytest.mark.parametrize(
    "option_type, F, K, r, sigma, T, expected_error",
    [
        (
            OptionType.call,
            -1,
            50,
            0.04,
            0.2,
            0.75,
            "Forward price (F) must be non-negative.",
        ),
        (
            OptionType.call,
            45,
            -1,
            0.04,
            0.2,
            0.75,
            "Strike price (K) must be non-negative.",
        ),
        (
            OptionType.call,
            45,
            50,
            -0.01,
            0.2,
            0.75,
            "Risk-free interest rate (r) must be non-negative.",
        ),
        (
            OptionType.call,
            45,
            50,
            0.04,
            -0.1,
            0.75,
            "Volatility (sigma) must be non-negative.",
        ),
        (
            OptionType.call,
            45,
            50,
            0.04,
            0.2,
            -0.5,
            "Time to maturity (T) must be non-negative.",
        ),
    ],
)
def test_black76_value_errors(option_type, F, K, r, sigma, T, expected_error):
    """
    Verify that ValueError is raised with the correct explanation for any invalid input.
    """
    with pytest.raises(ValueError, match=re.escape(expected_error)):
        black76(option_type, F, K, r, sigma, T)
