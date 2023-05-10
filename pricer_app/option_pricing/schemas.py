from pydantic import BaseModel
from .enums import OptionType


class OptionPricingData(BaseModel):
    option_type: OptionType
    K: float

    _validate_option_type = OptionType.ensure_valid_option_type
