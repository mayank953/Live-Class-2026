"""A tool (weather) called manually, using a structured field extracted by the AI.

Setup: uv add pydantic openai anthropic python-dotenv
.env:  set at least one of OPENAI_API_KEY / ANTHROPIC_API_KEY / GROQ_API_KEY / OPENROUTER_API_KEY
"""

import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()


# --- brain ---

def ask_openai(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
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
    print("Instructions to model: ", question)
    print("Answering question using Groq API...", response.choices[0].message.content)
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


# --- structured extraction (same as File 3) ---

class WeatherQuestion(BaseModel):
    city: str
    wants_fahrenheit: bool = False


def extract_weather_question(user_message: str) -> WeatherQuestion | str:
    instruction = (
        "Read the user's message and reply with ONLY a JSON object -- no other "
        'text -- in this exact shape: {"city": "<city name>", '
        '"wants_fahrenheit": <true or false>}. '
        f"User's message: {user_message!r}"
    )
    raw_reply = ask_ai(instruction)

    print(f"Raw reply from model: {raw_reply!r}")

    try:
        cleaned = raw_reply.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)
        return WeatherQuestion(**data)
    except (json.JSONDecodeError, ValidationError) as exc:
        return f"Rejected: {exc}"


# --- the tool ---

SAMPLE_WEATHER = {
    "tokyo": {"celsius": 22, "conditions": "partly cloudy"},
    "delhi": {"celsius": 34, "conditions": "clear skies"},
    "london": {"celsius": 15, "conditions": "light rain"},
}


def get_weather(city: str) -> str:
    """The tool itself -- a plain function with no knowledge of AI at all.
    Uses sample data rather than a live API so the demo never depends on
    classroom internet.
    """
    data = SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['conditions']}"


def answer_weather_question(user_message: str) -> str:
    """The full manual pipeline: extract a trusted city with Pydantic, then
    WE decide to call get_weather and WE pass the extracted field in.
    Nothing here is decided by the model beyond the extraction step.
    """
    extracted = extract_weather_question(user_message)
    print(f"Extracted: {extracted!r}")
    # extracted is of Type WeatherQuestion
    if not isinstance(extracted, WeatherQuestion):
        return f"Could not extract a city: {extracted}"
    return get_weather(extracted.city)


if __name__ == "__main__":
    print(answer_weather_question("What's the weather like in Tokyo right now?"))
