"""
_8_pydantic_with_ai.py

The headline topic. Pydantic's job: take data you don't fully trust
(an LLM's text output, especially) and turn it into data you DO trust
-- with a clear, loud error the moment something doesn't match what
you expected.

Setup: `uv add pydantic`
Run with: uv run _8_pydantic_with_ai.py
"""

from pydantic import BaseModel, Field, field_validator, ValidationError

# =============================================================================
# PART 1 -- THE PROBLEM, FIRST
# =============================================================================
# Go back to File 7 and ask the real model the same question three times.
# Real models are NOT perfectly consistent in formatting -- different
# wording, a number written as text, extra commentary. If your code
# blindly trusts the SHAPE of what comes back, it WILL break eventually.

print("=== The problem ===")
print("Imagine an LLM replied with:", {"amount": "five hundred", "currency": "us dollars"})
print("'five hundred' isn't a number Python can do math with. 'us dollars' isn't a currency CODE.\n")


# =============================================================================
# PART 2 -- BaseModel: defining the shape you'll accept
# =============================================================================

class CurrencyAmount(BaseModel):
    """The shape we're willing to trust."""
    amount: float
    currency: str


good = CurrencyAmount(amount=100, currency="USD")
print(f"=== Valid: {good} ===")

print("=== Invalid, caught immediately ===")
try:
    CurrencyAmount(amount="five hundred", currency="USD")
except ValidationError as exc:
    print(exc)

# Sensible coercion: "100" (a string) becomes 100.0 (a float) automatically.
coerced = CurrencyAmount(amount="100", currency="USD")
print(f"\n'100' (str) became {coerced.amount!r} ({type(coerced.amount).__name__})\n")


# =============================================================================
# PART 3 -- Field(): constraints beyond just "the right type"
# =============================================================================

class BoundedAmount(BaseModel):
    amount: float = Field(gt=0, description="Must be positive")
    currency: str = Field(min_length=3, max_length=3)


print("=== Field() constraints ===")
try:
    BoundedAmount(amount=-50, currency="USD")
except ValidationError as exc:
    print(exc)


# =============================================================================
# PART 4 -- @field_validator: custom rules
# =============================================================================
# Same decorator pattern from File 4's `announce`/`timed` -- just a more
# specialized version of an idea you already own.

KNOWN_CURRENCIES = {"USD", "INR", "EUR", "GBP", "JPY"}


class StrictAmount(BaseModel):
    amount: float = Field(gt=0)
    currency: str

    @field_validator("currency")
    @classmethod
    def must_be_known(cls, value: str) -> str:
        value = value.upper().strip()
        if value not in KNOWN_CURRENCIES:
            raise ValueError(f"{value!r} isn't a recognized currency: {KNOWN_CURRENCIES}")
        return value


print("\n=== Custom validator ===")
normalized = StrictAmount(amount=100, currency="usd")
print(f"'usd' normalized to {normalized.currency!r} automatically.")
try:
    StrictAmount(amount=100, currency="zzz")
except ValidationError as exc:
    print(exc)


# =============================================================================
# PART 5 -- NESTED MODELS
# =============================================================================

class ConversionRequest(BaseModel):
    source: StrictAmount
    target_currency: str


print("\n=== Nested models ===")
request = ConversionRequest(source={"amount": 250, "currency": "eur"}, target_currency="GBP")
print(f"{request.source.amount} {request.source.currency} -> {request.target_currency}")


# =============================================================================
# PART 6 -- THE USE CASE THAT MATTERS MOST: validating an LLM's raw text
# =============================================================================

llm_clean_output = '{"amount": 300, "currency": "usd"}'
print("\n=== Validating a clean LLM JSON response ===")
print(StrictAmount.model_validate_json(llm_clean_output))

llm_messy_output = '{"amount": "a few hundred", "currency": "dollars"}'
print("\n=== A realistic, messier response ===")
try:
    StrictAmount.model_validate_json(llm_messy_output)
except ValidationError as exc:
    print(f"Caught before it could break anything downstream:\n{exc}")


if __name__ == "__main__":
    print("\n--- Pydantic done. Next file applies this back onto File 5's currency API call. ---")
