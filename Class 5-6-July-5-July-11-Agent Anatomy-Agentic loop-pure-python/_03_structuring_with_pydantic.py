"""Structuring an AI reply with Pydantic so it can be trusted downstream.

Setup: uv add pydantic openai anthropic python-dotenv
.env:  set at least one of OPENAI_API_KEY / ANTHROPIC_API_KEY / GROQ_API_KEY / OPENROUTER_API_KEY
"""

import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()


# --- brain: same four-provider picker as File 2, duplicated here so this
# file can run entirely on its own, with no import from another file. ---

def ask_openai(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    print(question)
    print('openAI',response.choices[0].message.content)

    return response.choices[0].message.content


def ask_anthropic(question: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-3-5-haiku-20241022", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text


def ask_groq(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


def ask_openrouter(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
    response = client.chat.completions.create(
        model="openrouter/free", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


def ask_ai(question: str) -> str:
    if os.environ.get("GROQ_API_KEY"):
        return ask_groq(question)
    if os.environ.get("OPENROUTER_API_KEY"):
        return ask_openrouter(question)
    if os.environ.get("OPENAI_API_KEY"):
        return ask_openai(question)
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ask_anthropic(question)
    raise RuntimeError(
        "No API key found. Set one of GROQ_API_KEY, OPENROUTER_API_KEY, "
        "OPENAI_API_KEY, or ANTHROPIC_API_KEY in your .env file."
    )


# --- structured extraction ---

class WeatherQuestion(BaseModel):
    """The only shape we're willing to trust back from the model: a plain
    city name plus whether the person wants Fahrenheit instead of Celsius.
    """

    city: str 
    wants_fahrenheit: bool = False 


def extract_weather_question(user_message: str) -> WeatherQuestion | str:
    """Asks the model to respond with ONLY a JSON object matching
    WeatherQuestion, then parses and validates it. Returns the validated
    model on success, or a short error string if the reply didn't match
    the expected shape -- so a bad response never silently continues.
    """
    instruction = (
        "Read the user's message and reply with ONLY a JSON object -- no other "
        'text -- in this exact shape: {"city": "<city name>", '
        '"wants_fahrenheit": <true or false>}. '
        f"User's message: {user_message!r}"
    )
    raw_reply = ask_ai(instruction)

    print(f" \n \n \n Raw reply from model: {raw_reply!r}")
    try:
        cleaned = raw_reply.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)
        return WeatherQuestion(**data)
    except (json.JSONDecodeError, ValidationError) as exc:
        return f"Rejected: {exc}"


if __name__ == "__main__":
    for message in [
        "What's the weather like in Tokyo right now?",
        "Is it warm in Delhi today? I want it in Fahrenheit please.",
    ]:
        result = extract_weather_question(message)
        print(f"{message!r} -> {result}")
