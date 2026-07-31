"""
_9_api_call_with_structure.py

File 5's convert_currency function, revisited. Same real API call --
nothing about the API itself changes. What's new: its ARGUMENTS now go
through Pydantic before the function ever runs. This is the moment
"Pydantic" and "API call" stop being two separate lessons.

Run with: uv run _9_api_call_with_structure.py
"""

import requests
from pydantic import BaseModel, Field, field_validator, ValidationError

KNOWN_CURRENCIES = {"USD", "INR", "EUR", "GBP", "JPY"}


class ConvertCurrencyArgs(BaseModel):
    """The trusted shape for this specific function's arguments."""
    amount: float = Field(gt=0)
    from_currency: str
    to_currency: str

    @field_validator("from_currency", "to_currency")
    @classmethod
    def must_be_known_currency(cls, value: str) -> str:
        value = value.upper().strip()
        if value not in KNOWN_CURRENCIES:
            raise ValueError(f"{value!r} isn't a currency this function recognizes: {KNOWN_CURRENCIES}")
        return value


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Unchanged from File 5 -- still a plain function, still calling the real API."""
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": from_currency, "symbols": to_currency},
            timeout=10,
        )
        response.raise_for_status()
        rate = response.json()["rates"][to_currency]
        return round(amount * rate, 2)
    except requests.exceptions.RequestException as exc:
        return f"Couldn't reach the currency service: {exc}"
    except KeyError:
        return f"No rate available for {from_currency} -> {to_currency}"


def convert_currency_validated(raw_arguments: dict) -> float | str:
    """The new part: validate BEFORE calling. Untrusted dict in, trusted call out."""
    try:
        validated = ConvertCurrencyArgs(**raw_arguments)
    except ValidationError as exc:
        return f"Rejected before the API was ever called: {exc}"

    return convert_currency(
        amount=validated.amount,
        from_currency=validated.from_currency,
        to_currency=validated.to_currency,
    )


if __name__ == "__main__":
    print("--- Good arguments: validation passes, the real API gets called ---")
    print(convert_currency_validated({"amount": 100, "from_currency": "usd", "to_currency": "inr"}))

    print("\n--- Bad arguments: rejected BEFORE the API is ever touched ---")
    print(convert_currency_validated({"amount": -50, "from_currency": "dollars", "to_currency": "inr"}))

    print(
        "\nNotice: in the bad case, no network call happened at all -- check the absence of any "
        "delay or network error message. Pydantic stopped it before it could even try."
    )
