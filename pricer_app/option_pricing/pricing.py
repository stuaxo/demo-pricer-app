from math import exp, log, sqrt
from scipy.stats import norm

from .enums import OptionType


def black76(
    option_type: OptionType, F: float, K: float, r: float, sigma: float, T: float
):
    """
    Calculate the present value of an option using the Black76 formula.

    Args:
    option_type (OptionType): Type of the option (Call or Put)
    F (float): Forward price of the underlying asset
    K (float): Option strike price
    r (float): Risk-free interest rate
    sigma (float): Volatility of the underlying asset
    T (float): Time to maturity in years

    Returns:
    float: Present value of the option
    """

    if F < 0:
        raise ValueError("Forward price (F) must be non-negative.")
    if K < 0:
        raise ValueError("Strike price (K) must be non-negative.")
    if r < 0:
        raise ValueError("Risk-free interest rate (r) must be non-negative.")
    if sigma < 0:
        raise ValueError("Volatility (sigma) must be non-negative.")
    if T < 0:
        raise ValueError("Time to maturity (T) must be non-negative.")

    d1 = (log(F / K) + 0.5 * sigma**2 * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == OptionType.call:
        return exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        return exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
