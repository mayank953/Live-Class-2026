"""
_7_ai_call_free_and_paid.py

The real version of File 6. Same shape every time -- only the client
setup changes. Three providers, in order from "definitely free" to
"definitely paid," so you see the whole spectrum, not just one vendor.

  1. Groq       -- free, fast, email signup, no card
  2. OpenRouter  -- free tier too, and "openrouter/free" auto-routes to
                    whichever free model is currently available, so this
                    code doesn't go stale when free model names change
  3. OpenAI      -- paid. Shown for completeness, NOT required to run.

Setup: `uv add openai python-dotenv`
       .env: GROQ_API_KEY=... and/or OPENROUTER_API_KEY=...

Run with: uv run _7_ai_call_free_and_paid.py
"""

import os

from dotenv import load_dotenv

load_dotenv()

QUESTION = "In one sentence, explain why someone might use a currency conversion tool instead of guessing."


def call_groq(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


def call_openrouter(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
    response = client.chat.completions.create(
        model="openrouter/free",   # auto-routes to whatever's free right now -- never goes stale
        max_tokens=200,
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


def call_openai_paid(question: str) -> str:
    """PAID. Don't run this live in class unless you want to spend money.
    Shown so the room sees the full provider landscape, not run as a demo."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])   # no base_url override -- this IS OpenAI directly
    response = client.chat.completions.create(
        model="gpt-4o-mini", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


def call_fallback(question: str) -> str:
    from _6_fake_ai_call import FakeAIClient

    client = FakeAIClient()
    response = client.chat.completions.create(
        model="fallback", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("--- Groq (free) ---")
    if os.environ.get("GROQ_API_KEY"):
        try:
            print(call_groq(QUESTION))
        except Exception as exc:  # noqa: BLE001
            print(f"Groq failed ({exc}), falling back: {call_fallback(QUESTION)}")
    else:
        print(f"No GROQ_API_KEY set. Stand-in: {call_fallback(QUESTION)}")

    print("\n--- OpenRouter (also free, via the auto-router) ---")
    if os.environ.get("OPENROUTER_API_KEY"):
        try:
            print(call_openrouter(QUESTION))
        except Exception as exc:  # noqa: BLE001
            print(f"OpenRouter failed ({exc}), falling back: {call_fallback(QUESTION)}")
    else:
        print(f"No OPENROUTER_API_KEY set. Stand-in: {call_fallback(QUESTION)}")

    print("\n--- OpenAI (PAID -- not called automatically) ---")
    print("Same exact shape as the two calls above. The only changes: no base_url override")
    print("(OpenAI's own API is the default), and a different, paid, API key.")
    print("Uncomment call_openai_paid(QUESTION) above if you want to spend real money trying it.")
