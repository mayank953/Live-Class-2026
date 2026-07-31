"""
_12_agent_with_one_tool.py

The exact same Agent class from File 11, with one addition: a `tools`
dict, and the validated currency tool from File 10 dropped into it.
The agent can now hold both its brain AND a working tool -- it still
doesn't decide on its own when to use it. That's Class 4.

Run with: uv run _12_agent_with_one_tool.py
"""

import functools
import os
import time
from dataclasses import dataclass, field
from typing import Callable

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, ValidationError

load_dotenv()

# --- The tool, exactly as File 10 built it ---

TOOL_REGISTRY: dict[str, Callable] = {}


def tool(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[tool call] {func.__name__}({kwargs}) -> {result!r}  ({elapsed_ms:.1f} ms)")
        return result

    TOOL_REGISTRY[func.__name__] = wrapper
    return wrapper


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


def call_tool_safely(name: str, raw_arguments: dict):
    if name == "convert_currency":
        try:
            validated = ConvertCurrencyArgs(**raw_arguments)
        except ValidationError as exc:
            return f"Rejected before the tool ran: {exc}"
        return convert_currency(**validated.model_dump())
    return f"No tool named {name!r}"


# --- The Agent, now with a `tools` attribute (File 11 + one new field) ---

@dataclass
class Agent:
    name: str
    system_prompt: str
    tools: dict = field(default_factory=dict)   # <-- new since File 11
    messages: list = field(default_factory=list)

    def remember(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def show_transcript(self) -> None:
        for turn in self.messages:
            print(f"{turn['role']:>9}: {turn['content']}")

    def ask_brain(self, question: str) -> str:
        self.remember("user", question)
        if os.environ.get("GROQ_API_KEY"):
            try:
                from openai import OpenAI

                client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile", max_tokens=200, messages=self.messages
                )
                answer = response.choices[0].message.content
            except Exception:  # noqa: BLE001
                answer = self._fallback(question)
        else:
            answer = self._fallback(question)
        self.remember("assistant", answer)
        return answer

    def use_tool(self, name: str, **arguments):
        """Manually trigger a tool by name -- WE decide, not the brain. Yet."""
        return call_tool_safely(name, arguments)

    @staticmethod
    def _fallback(question: str) -> str:
        from _6_fake_ai_call import FakeAIClient

        client = FakeAIClient()
        response = client.chat.completions.create(
            model="fallback", max_tokens=200, messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    trip_planner = Agent(
        name="Trip Planner",
        system_prompt="You help people plan trips using currency conversion.",
        tools=TOOL_REGISTRY,
    )

    print("--- Talking to the brain ---")
    print(trip_planner.ask_brain("Should I exchange money before or after I travel?"))

    print("\n--- Manually using its tool ---")
    print(trip_planner.use_tool("convert_currency", amount=100, from_currency="usd", to_currency="inr"))

    print("\n--- Tools this agent has access to ---")
    print(list(trip_planner.tools.keys()))

    print("\nThe agent now HAS a working hand. It still waits for us to move it. File 13 adds more hands.")
