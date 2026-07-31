"""
_5_calling_a_real_api.py

How Python talks to a service running somewhere else on the internet.
Today's example: Frankfurter (api.frankfurter.dev), real currency
conversion, free, no key, no signup, ever.

Setup: `uv add requests`
Run with: uv run _5_calling_a_real_api.py
"""

import requests

# --- The simplest possible request ---
response = requests.get(
    "https://api.frankfurter.dev/v1/latest",
    params={"base": "USD", "symbols": "INR"},
    timeout=10,   # never call a real API with no timeout
)
print("Status code:", response.status_code)
print("Parsed as a dict:", response.json())

# --- Wrapped in a reusable function, with error handling from File 3 ---
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Convert `amount` between currencies using real, live ECB rates."""
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": from_currency.upper(), "symbols": to_currency.upper()},
            timeout=10,
        )
        response.raise_for_status()
        rate = response.json()["rates"][to_currency.upper()]
        return round(amount * rate, 2)
    except requests.exceptions.RequestException as exc:
        return f"Couldn't reach the currency service: {exc}"
    except KeyError:
        return f"No rate available for {from_currency} -> {to_currency}"


if __name__ == "__main__":
    print("\n--- Using the wrapped function ---")
    print(convert_currency(100, "USD", "INR"))
    print(convert_currency(5000, "INR", "JPY"))
    print(convert_currency(50, "USD", "ZZZ"))

    print("\nThis function still knows nothing about AI. That changes starting next file.")
