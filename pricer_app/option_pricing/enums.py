from enum import Enum
from pydantic import validator


class OptionType(str, Enum):
    call = "call"
    put = "put"

    @validator("option_type", pre=True)
    def ensure_valid_option_type(cls, value):
        valid_values = [item.value for item in cls]
        if value not in valid_values:
            raise ValueError(
                f"Invalid option type '{value}'. Must be one of: {', '.join(valid_values)}."
            )
        return value.lower()
