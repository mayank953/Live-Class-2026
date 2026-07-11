"""The assembled agent: brain + tool + schema + a loop that lets the model
keep calling tools until it is ready to give a final answer.

Needs an OpenAI-compatible provider (Groq, OpenRouter, or OpenAI).

Setup: uv add openai python-dotenv
.env:  set at least one of GROQ_API_KEY / OPENROUTER_API_KEY / OPENAI_API_KEY
"""

import json
import os

from dotenv import load_dotenv

load_dotenv()


SAMPLE_WEATHER = {
    "tokyo": {"celsius": 22, "conditions": "partly cloudy"},
    "delhi": {"celsius": 34, "conditions": "clear skies"},
    "london": {"celsius": 15, "conditions": "light rain"},
}


def get_weather(city: str) -> str:
    data = SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['conditions']}"


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
    }
]

TOOLS_BY_NAME = {"get_weather": get_weather}


def get_client_and_model():
    """Same provider picker as File 5. Raises if no compatible key is set."""
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


def run_agent(messages: list, max_turns: int = 4) -> str:
    """The agent loop. Each turn: call the model with the tool schema
    attached; if it replies with tool_calls, execute every one of them
    and feed the results back in; if it replies with plain content
    instead, that is the final answer and the loop stops. max_turns is a
    safety limit so a confused model can't loop forever.
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

        call = message.tool_calls[0]
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
                ],
            }
        )

        for call in message.tool_calls:
            arguments = json.loads(call.function.arguments)
            tool_function = TOOLS_BY_NAME[call.function.name]
            result = tool_function(**arguments)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    return "Reached max_turns without a final answer."


def chat() -> None:
    """A minimal terminal REPL. conversation_memory is the agent's entire
    memory -- a plain list, grown by run_agent() on every turn.
    """
    conversation_memory: list[dict] = []
    print("Type a question (Ctrl+C to quit).")

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        conversation_memory.append({"role": "user", "content": user_input})
        answer = run_agent(conversation_memory)
        print(f"Agent: {answer}\n")


if __name__ == "__main__":
    chat()
