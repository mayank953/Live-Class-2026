"""
_4_decorators.py

A decorator is a gift wrapper: the function inside doesn't change, but
the wrapper adds something extra every time the function gets called.
Last topic before we touch the outside world -- still no AI, no agents.

Run with: uv run _4_decorators.py
"""

import functools
import time


def announce(func):
    """Announces when a function starts and finishes."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}.")
        return result

    return wrapper


@announce
def greet(name):
    return f"Hello, {name}!"


print(greet("Mayank"))


def timed(func):
    """Prints how long a function took to run."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {elapsed_ms:.2f} ms")
        return result

    return wrapper


@timed
def slow_addition(a, b):
    time.sleep(0.05)
    return a + b


print(slow_addition(3, 4))


# --- Stacking two decorators on the same function ---
@announce
@timed
def slow_greeting(name):
    time.sleep(0.02)
    return f"Hello there, {name}!"


print(slow_greeting("Krish"))


if __name__ == "__main__":
    print("\nDecorators done. Nothing above mentioned tools or agents once.")
    print("File 10 today reuses this exact pattern -- the wrapper idea, applied to something real.")
