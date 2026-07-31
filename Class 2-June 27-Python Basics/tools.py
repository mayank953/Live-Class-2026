

import functools
import time
from typing import Callable

# -----------------------------------------------------------------------
# Step 1: A tiny decorator that builds a "tool registry"
# -----------------------------------------------------------------------

TOOL_REGISTRY: dict[str, Callable] = {}


def tool(func: Callable) -> Callable:
    """Register `func` in TOOL_REGISTRY and time how long it takes to run.

    A decorator is just a function that takes a function and returns a
    (usually wrapped) function. Here we do two things:
      1. Wrap the function so every call is timed and printed -- handy
         for seeing what your agent is actually doing, step by step.
      2. Add the original function to TOOL_REGISTRY so it can be looked
         up by name later -- exactly what Class 4's agent loop will need
         when Claude says "call get_weather" and your code has to find
         the actual get_weather function to run.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[tool call] {func.__name__}({args}, {kwargs}) -> {result!r}  ({elapsed_ms:.2f} ms)")
        return result

    TOOL_REGISTRY[func.__name__] = wrapper
    return wrapper


# -----------------------------------------------------------------------
# Step 2: The three tools
# -----------------------------------------------------------------------

@tool
def get_current_time() -> str:
    """Return the current time as a human-readable string."""
    return time.strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculator(expression: str) -> float:
    """Safely evaluate a simple arithmetic expression, e.g. '12 * (4 + 1)'.

    Only digits, parentheses, whitespace, and + - * / are allowed. This
    is deliberately restricted -- a real tool should never be able to
    run arbitrary code, even if something unexpected ends up here.
    """
    allowed_characters = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_characters:
        raise ValueError(f"Expression contains characters that aren't allowed: {expression!r}")
    return eval(expression)  # noqa: S307 -- safe here because of the character check above


@tool
def get_weather(city: str) -> str:
    """Return the current weather for `city`. (Mock data for teaching.)"""
    fake_weather_data = {
        "tokyo": "22°C, partly cloudy",
        "delhi": "34°C, clear skies",
        "london": "15°C, light rain",
    }
    return fake_weather_data.get(city.lower(), f"No weather data for {city!r}")


if __name__ == "__main__":
    get_current_time()
    calculator("12 * (4 + 1)")
    get_weather("Tokyo")
    print("\nRegistered tools:", list(TOOL_REGISTRY.keys()))

    # --- A quick look at WHY calculator raises ValueError on bad input ---
    # A tool that crashes the whole program on bad input can't be trusted
    # with an AI calling it automatically. This is the other half of that
    # safety story: catch the error, don't let it take everything down.
    print("\n--- What happens with deliberately bad input ---")
    try:
        calculator("12 + ; DROP TABLE users;")
    except ValueError as exc:
        print(f"Caught cleanly, nothing crashed: {exc}")
