"""
_10_tool_with_ai_call.py

Two things that work independently, sitting next to each other for the
first time: a validated tool (File 9) and a real AI call (File 7). They
don't know about each other yet -- that's the next 4 files. Today's new
piece: the @tool decorator from File 4, applied for real instead of to
a generic example.

Run with: uv run _10_tool_with_ai_call.py
"""

import functools
import os
import time
from typing import Callable

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, ValidationError

load_dotenv()

# =============================================================================
# PART 1 -- THE DECORATOR, APPLIED (File 4's exact pattern, no longer generic)
# =============================================================================

TOOL_REGISTRY: dict[str, Callable] = {}


def tool(func: Callable) -> Callable:
    """File 4's `timed` decorator, plus registering the function by name."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[tool call] {func.__name__}({kwargs}) -> {result!r}  ({elapsed_ms:.1f} ms)")
        return result

    TOOL_REGISTRY[func.__name__] = wrapper
    return wrapper


# =============================================================================
# PART 2 -- THE VALIDATED TOOL (Files 8 + 9, combined and wrapped)
# =============================================================================

KNOWN_CURRENCIES = {"USD", "INR", "EUR", "GBP", "JPY"}


class ConvertCurrencyArgs(BaseModel):
    amount: float = Field(gt=0)
    from_currency: str
    to_currency: str

    @field_validator("from_currency", "to_currency")
    @classmethod
    def must_be_known_currency(cls, value: str) -> str:
        value = value.upper().strip()
        if value not in KNOWN_CURRENCIES:
            raise ValueError(f"{value!r} isn't recognized: {KNOWN_CURRENCIES}")
        return value


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Convert `amount` between currencies using real, live ECB rates."""
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


def call_tool_safely(raw_arguments: dict) -> float | str:
    try:
        validated = ConvertCurrencyArgs(**raw_arguments)
    except ValidationError as exc:
        return f"Rejected before the tool ran: {exc}"
    return convert_currency(
        amount=validated.amount, from_currency=validated.from_currency, to_currency=validated.to_currency
    )


# =============================================================================
# PART 3 -- THE AI CALL (File 7, condensed -- Groq, falling back if unavailable)
# =============================================================================

def ask_ai(question: str) -> str:
    if os.environ.get("GROQ_API_KEY"):
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", max_tokens=200, messages=[{"role": "user", "content": question}]
            )
            return response.choices[0].message.content
        except Exception:  # noqa: BLE001
            pass
    from _6_fake_ai_call import FakeAIClient

    client = FakeAIClient()
    response = client.chat.completions.create(
        model="fallback", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("--- The AI call, on its own ---")
    print(ask_ai("In one sentence, what is currency conversion useful for?"))

    print("\n--- The tool, on its own, validated ---")
    print(call_tool_safely({"amount": 100, "from_currency": "usd", "to_currency": "inr"}))

    print("\n--- Tools registered so far ---")
    print(list(TOOL_REGISTRY.keys()))

    print(
        "\nBoth work. Neither knows the other exists. The AI didn't decide to use the tool --\n"
        "WE called both, by hand, one after another. Files 11-12 wire them together properly."
    )
