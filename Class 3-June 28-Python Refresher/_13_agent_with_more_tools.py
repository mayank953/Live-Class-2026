"""
_13_agent_with_more_tools.py

File 12's agent, now with THREE tools instead of one: currency
conversion (real, from File 9/10), plus weather and a calculator
(both simple, local, no network -- the point here is "more than one
tool registered," not "every tool must hit the internet").

Run with: uv run _13_agent_with_more_tools.py
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


# --- Tool 1: currency conversion (unchanged from File 12) ---

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


# --- Tool 2: weather (new -- simple sample data, no network) ---

SAMPLE_WEATHER = {"tokyo": "22°C, partly cloudy", "delhi": "34°C, clear skies", "london": "15°C, light rain"}


@tool
def get_weather(city: str) -> str:
    return SAMPLE_WEATHER.get(city.lower(), f"No data for {city!r}")


# --- Tool 3: calculator (new -- the safe-eval pattern from Class 1) ---

@tool
def calculator(expression: str) -> float:
    allowed_characters = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_characters:
        raise ValueError(f"Expression contains characters that aren't allowed: {expression!r}")
    return eval(expression)


# --- Validated dispatch across ALL three tools, by name ---

def call_tool_safely(name: str, raw_arguments: dict):
    if name == "convert_currency":
        try:
            validated = ConvertCurrencyArgs(**raw_arguments)
        except ValidationError as exc:
            return f"Rejected before the tool ran: {exc}"
        return convert_currency(**validated.model_dump())
    if name == "get_weather":
        return get_weather(**raw_arguments)
    if name == "calculator":
        return calculator(**raw_arguments)
    return f"No tool named {name!r}"


@dataclass
class Agent:
    name: str
    system_prompt: str
    tools: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)

    def remember(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def show_transcript(self) -> None:
        for turn in self.messages:
            print(f"{turn['role']:>9}: {turn['content']}")

    def use_tool(self, name: str, **arguments):
        return call_tool_safely(name, arguments)

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

    @staticmethod
    def _fallback(question: str) -> str:
        from _6_fake_ai_call import FakeAIClient

        client = FakeAIClient()
        response = client.chat.completions.create(
            model="fallback", max_tokens=200, messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    trip_planner = Agent(name="Trip Planner", system_prompt="You help people plan trips.", tools=TOOL_REGISTRY)

    print("--- Three tools, used one after another ---")
    print(trip_planner.use_tool("get_weather", city="Tokyo"))
    print(trip_planner.use_tool("calculator", expression="22 * 9 / 5 + 32"))
    print(trip_planner.use_tool("convert_currency", amount=100, from_currency="usd", to_currency="inr"))

    print("\n--- All tools registered ---")
    print(list(trip_planner.tools.keys()))

    print("\nThree working hands now, not one. File 14 gives this agent a memory worth keeping.")
