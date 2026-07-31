"""Streamlit front end for the Project Zero agent -- three tools, one chat UI.

Needs an OpenAI-compatible provider (Groq, OpenRouter, or OpenAI).

Setup: uv add streamlit openai requests python-dotenv
.env:  set at least one of GROQ_API_KEY / OPENROUTER_API_KEY / OPENAI_API_KEY
Run:   uv run streamlit run _07_streamlit_app.py
"""

import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# --- tools ---

SAMPLE_WEATHER = {
    "tokyo": {"celsius": 22, "conditions": "partly cloudy"},
    "delhi": {"celsius": 34, "conditions": "clear skies"},
    "london": {"celsius": 15, "conditions": "light rain"},
}


def get_weather(city: str) -> str:
    """Sample data, not a live API -- keeps this tool network-independent."""
    data = SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['conditions']}"


def calculator(expression: str) -> str:
    """Evaluates a plain arithmetic expression. Only digits, operators, and
    parentheses are allowed through before eval() ever runs, so arbitrary
    code can't be smuggled in via the expression string.
    """
    allowed_characters = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_characters:
        return f"Rejected -- expression contains disallowed characters: {expression!r}"
    try:
        return str(eval(expression))
    except Exception as exc:  # noqa: BLE001
        return f"Could not evaluate: {exc}"


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Live conversion via the Frankfurter API (free, no key required).
    A real network call, unlike the other two tools -- worth pointing out
    that tools can mix live data and static data freely.
    """
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": from_currency.upper(), "symbols": to_currency.upper()},
            timeout=10,
        )
        response.raise_for_status()
        rate = response.json()["rates"][to_currency.upper()]
        return str(round(amount * rate, 2))
    except requests.exceptions.RequestException as exc:
        return f"Currency service unavailable: {exc}"
    except KeyError:
        return f"No rate available for {from_currency} -> {to_currency}"


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another using live rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_currency": {"type": "string", "description": "3-letter code, e.g. USD"},
                    "to_currency": {"type": "string", "description": "3-letter code, e.g. INR"},
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        },
    },
]

TOOLS_BY_NAME = {
    "get_weather": get_weather,
    "calculator": calculator,
    "convert_currency": convert_currency,
}


# --- brain ---

def get_client_and_model():
    """Picks whichever OpenAI-compatible provider has a key set. Raises
    clearly if none is configured.
    """
    from openai import OpenAI

    if os.environ.get("GROQ_API_KEY"):
        return (
            OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1"),
            "llama-3.3-70b-versatile",
        )
    if os.environ.get("OPENROUTER_API_KEY"):
        return (
            OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1"),
            "openrouter/free",
        )
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"]), "gpt-4o-mini"

    raise RuntimeError(
        "No OpenAI-compatible key found. Set one of GROQ_API_KEY, "
        "OPENROUTER_API_KEY, or OPENAI_API_KEY in your .env file."
    )


def run_agent(messages: list, max_turns: int = 5) -> str:
    """Same loop as File 6: choose -> execute -> observe -> repeat, until
    the model returns a final answer with no further tool calls, or
    max_turns is reached.
    """
    client, model = get_client_and_model()

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=model, max_tokens=300, messages=messages, tools=TOOL_SCHEMAS
        )
        message = response.choices[0].message

        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content})
            return message.content

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.function.name, "arguments": call.function.arguments},
                    }
                    for call in message.tool_calls
                ],
            }
        )

        for call in message.tool_calls:
            arguments = json.loads(call.function.arguments)
            tool_function = TOOLS_BY_NAME[call.function.name]
            result = tool_function(**arguments)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    return "Reached max_turns without a final answer."


# --- front end ---

st.set_page_config(page_title="Project Zero Agent", page_icon=":robot_face:")
st.title("Project Zero Agent")
st.caption("Weather, calculator, and currency conversion -- no framework, just Python.")

# st.session_state.messages is this app's memory -- it survives Streamlit's
# re-runs on every interaction, which a plain local variable would not.
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] in ("user", "assistant") and message.get("content"):
        with st.chat_message(message["role"]):
            st.write(message["content"])

user_input = st.chat_input("Ask about the weather, do some maths, or convert a currency...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_agent(st.session_state.messages)
        st.write(answer)
