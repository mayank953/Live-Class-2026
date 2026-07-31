"""
_14_agent_with_memory.py

Today's final file. One new idea, explicitly named this time: MEMORY.
You've been building it since File 11 (`self.messages`) without
calling it out -- it was always just a Python list. Today: why that
list IS the agent's memory, nothing more mysterious than that, and a
final call that uses the brain, all three tools, and memory together.

Run with: uv run _14_agent_with_memory.py
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

# =============================================================================
# PART 1 -- MEMORY, NAMED EXPLICITLY
# =============================================================================
# Memory, in every agent you'll ever build, is a Python list. Each entry
# is a dict with a role and content -- the exact shape from File 1's data
# structures. There is no separate "memory system" hiding underneath.

conversation_memory = []   # this IS memory. Nothing more is coming later to replace it.


def remember(role: str, content: str) -> None:
    conversation_memory.append({"role": role, "content": content})


remember("user", "What's the weather in Tokyo?")
remember("assistant", "Let me check that for you.")

print("=== Memory, inspected directly ===")
for turn in conversation_memory:
    print(f"{turn['role']:>9}: {turn['content']}")

print(f"\nType of conversation_memory: {type(conversation_memory).__name__}")
print(f"Type of one entry: {type(conversation_memory[0]).__name__}")
print("That's it. A list of dicts. That's what 'memory' means here, completely literally.\n")


# =============================================================================
# PART 2 -- EVERYTHING TOGETHER: brain + 3 tools + memory, one more time
# =============================================================================

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


SAMPLE_WEATHER = {"tokyo": "22°C, partly cloudy", "delhi": "34°C, clear skies", "london": "15°C, light rain"}


@tool
def get_weather(city: str) -> str:
    return SAMPLE_WEATHER.get(city.lower(), f"No data for {city!r}")


@tool
def calculator(expression: str) -> float:
    allowed_characters = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_characters:
        raise ValueError(f"Expression contains characters that aren't allowed: {expression!r}")
    return eval(expression)


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
    messages: list = field(default_factory=list)   # memory, exactly as Part 1 defined it

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
    trip_planner = Agent(
        name="Trip Planner",
        system_prompt="You help people plan trips using weather, currency conversion, and basic math.",
        tools=TOOL_REGISTRY,
    )

    print("=== The full set, one call after another ===")
    trip_planner.ask_brain("What should I check before traveling to Tokyo?")
    print(trip_planner.use_tool("get_weather", city="Tokyo"))
    print(trip_planner.use_tool("calculator", expression="22 * 9 / 5 + 32"))
    print(trip_planner.use_tool("convert_currency", amount=5000, from_currency="inr", to_currency="jpy"))

    print("\n=== Full transcript -- this IS the agent's memory, end to end ===")
    trip_planner.show_transcript()

    print("\n=== Everything this agent has access to ===")
    print(list(trip_planner.tools.keys()))

    print(
        "\nA brain that remembers. Three validated tools. All sitting in one object.\n"
        "What's still missing: the brain deciding, on its own, which tool to reach for, and when.\n"
        "That decision -- the actual agent loop -- is Class 4."
    )
