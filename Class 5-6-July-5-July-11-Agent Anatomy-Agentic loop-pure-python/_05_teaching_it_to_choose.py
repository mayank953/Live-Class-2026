"""Letting the model choose a tool for itself, via a tool schema.

Needs an OpenAI-compatible provider (Groq, OpenRouter, or OpenAI) --
Anthropic's tool-calling API uses a different response shape, covered
in a later module.

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
    """Same tool as File 4 -- a plain function, unaware that an AI exists."""
    data = SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['conditions']}"


# The "menu" handed to the model. It never sees get_weather() itself --
# only this description. The wording of "description" is what tells the
# model when this tool is relevant to a given question.
get_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever "
                        "the user asks about weather, temperature, or conditions "
                        "in a specific place. Don't use it for AQI"
                        },
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Tokyo'."}
            }
                            },
}

get_air_quality_schema = {
    "type": "function",
    "function": {
        "name": "get_air_quality",
        "description": "Get the current air quality for a city. Use this whenever "
                        "the user asks about air quality, pollution, or AQI "
                        "in a specific place.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Delhi'."}
            },
            "required": ["city"],
        },
    },
}

get_calculator_schema = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Use this tool to perform calculations. Use this whenever "
                        "the user asks for a calculation or a math problem.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The mathematical expression to calculate, e.g. '2 + 2'."}
            },
            "required": ["expression"],
        },
    },
}
get_complete_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever "
                        "the user asks about weather, temperature, or conditions "
                        "in a specific place.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Tokyo'."}
            },
            "required": ["city"],
        },
    },
}

get_capital_schema = {
    "type": "function",
    "function": {
        "name": "get_capital",
        "description": "Get the capital city of a country. Use this whenever "
                        "the user asks about the capital of a specific country.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "The country name, e.g. 'France'."}
            },
            "required": ["country"],
        },
    },
}


def get_tool_information(tool_name):
    return get_tool_schemas().get(tool_name)

get_tool_schemas = lambda: {
    "get_weather": get_complete_weather_schema,
    "get_air_quality": get_air_quality_schema,
    "calculator": get_calculator_schema,
    "get_capital": get_capital_schema,
}

get_tool_schema_for_llm={
    "type": "function",
    "function": {
        "name": "get_tool_schema_for_llm",
        "description": "Get the schema of a tool by its name. Use this whenever " 
                        "the user asks for the schema of a specific tool.",     
        "parameters": {
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "The name of the tool, e.g. 'get_weather'."}
            },
            "required": ["tool_name"],
        },
    },
}



def get_client_and_model():
    """Picks whichever OpenAI-compatible provider has a key set. Raises
    clearly if none is configured, since real decision-making genuinely
    needs a real model to call.
    """
    from openai import OpenAI

    if os.environ.get("GROQ_API_KEY"):
        print("Using Groq API...")
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
        print("Using OpenAI API...")
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"]), "gpt-4o-mini"

    raise RuntimeError(
        "No OpenAI-compatible key found. Set one of GROQ_API_KEY, "
        "OPENROUTER_API_KEY, or OPENAI_API_KEY in your .env file."
    )


def ask_ai_to_choose(question: str):
    """Sends the question plus the tool schema in one call. The reply may
    contain a tool_calls list instead of plain text -- that list is the
    model's decision, not an executed result.
    """

    client, model = get_client_and_model()
    response = client.chat.completions.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": question}],
        tools=[get_weather_schema,get_capital_schema, get_tool_schema_for_llm],
    )


    return response.choices[0].message


if __name__ == "__main__": 
    question =  "what is the Weather in Tokyo? "
    message = ask_ai_to_choose(question)

    print(f"Model's raw reply: {message!r}")

    if message.tool_calls:
        call = message.tool_calls[0]
        # print('\n\n\n')
        # print(call)
        arguments = json.loads(call.function.arguments)
        # print('\n\n\n')
        # print(arguments, call.function.name)
        result = get_weather(**arguments)
        print(f"{call.function.name}({arguments}) -> {result}")
    else:
        print(message.content)



'''
Hi How are you ?

Model's raw reply: ChatCompletionMessage(content="I'm just a computer program, so I don't have feelings, but I'm here and ready to help you! How can I assist you today?", refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None)


what is the weather like in Tokyo right now?

Model's raw reply: ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=
[ChatCompletionMessageToolCall(id='call_x4l82uTQXd3UR6Nw4Nq8wy48', function=Function(arguments='{"city":"Tokyo"}', name='get_weather'), type='function')]


)

What is 2 times 2?

Model's raw reply: ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_xOvtjwScctaVoFq3YIX8cwvn', function=Function(arguments='{"expression":"2 * 2"}', name='calculator'), type='function')])

What is the capital of Japan?

Model's raw reply: ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='nf9wkeb1q', function=Function(arguments='{"country":"Japan"}', name='get_capital'), type='function'),
ChatCompletionMessageToolCall(id='nf9wkeb3q', function=Function(arguments='{"country":"Tokyo"}', name='get_capital'), type='function'),
ChatCompletionMessageToolCall(id='nf9w4eb1q', function=Function(arguments='{"country":"Delhi"}', name='get_capital'), type='function')])

'''
'''

ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=
[ChatCompletionMessageToolCall(id='call_x4l82uTQXd3UR6Nw4Nq8wy48', function=Function(arguments='{"city":"Delhi"}', name='get_weather'), type='function')]

call_x4l82uTQXd3UR6Nw4Nq8wy48 - wrong weather API key

ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=
[ChatCompletionMessageToolCall(id='call_x4l82uTQXd3UR6Nw4Nq8wy49', function=Function(arguments='{"city":"Delhi"}', name='get_weather'), type='function')]


call_x4l82uTQXd3UR6Nw4Nq8wy49 - wrong weather API key

ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=
[ChatCompletionMessageToolCall(id='call_x4l82uTQXd3UR6Nw4Nq8wy50', function=Function(arguments='{"city":"Delhi"}', name='get_weather'), type='function')]



'''