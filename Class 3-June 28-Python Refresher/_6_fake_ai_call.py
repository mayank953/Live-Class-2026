"""
_6_fake_ai_call.py

The first mention of AI in today's class. A zero-dependency stand-in,
shaped exactly like the real thing -- so the next file (a real, free
model) feels familiar instead of intimidating.

Run with: uv run _6_fake_ai_call.py
"""

from __future__ import annotations


class _Message:
    def __init__(self, content: str):
        self.content = content


class _Choice:
    def __init__(self, content: str):
        self.message = _Message(content)


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_Choice(content)]


class _Completions:
    def create(self, *, model: str, max_tokens: int, messages: list[dict]) -> _FakeResponse:
        last_user_message = messages[-1]["content"].lower()
        if "currency" in last_user_message or "convert" in last_user_message:
            reply = "I'd reach for a currency conversion tool rather than guess an exchange rate."
        elif "weather" in last_user_message:
            reply = "I'd reach for a weather tool for that -- I don't have real eyes on the sky."
        else:
            reply = "I'm a stand-in today, running on simple rules, not a real model."
        return _FakeResponse(reply)


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class FakeAIClient:
    """A drop-in stand-in for a real LLM client, in the OpenAI-compatible shape."""

    def __init__(self):
        self.chat = _Chat()


if __name__ == "__main__":
    client = FakeAIClient()
    for question in ["Convert 50 dollars to euros.", "What's the weather like?", "Tell me a fact."]:
        response = client.chat.completions.create(
            model="fake-model", max_tokens=200, messages=[{"role": "user", "content": question}]
        )
        print(f"User: {question}")
        print(f"Stand-in: {response.choices[0].message.content}\n")

    print("Shape: client.chat.completions.create(...) -> .choices[0].message.content")
    print("This exact shape is what Groq, OpenRouter, and OpenAI all actually use.")



# https://developers.openai.com/api/docs/guides/completions


"""
_6_fake_ai_call.py

A simple fake AI without using classes.
Run with: uv run _6_fake_ai_call.py
"""


def fake_ai(model, max_tokens, messages):
    # Get the last user message
    user_message = messages[-1]["content"].lower()

    # Simple rule-based replies
    if "currency" in user_message or "convert" in user_message:
        reply = "I'd use a currency conversion tool instead of guessing."

    elif "weather" in user_message:
        reply = "I'd use a weather tool to check the latest weather."

    else:
        reply = "I'm just a fake AI. I'm using simple if-else rules."

    # Return data in the same format as a real AI API
    return {
        "choices": [
            {
                "message": {
                    "content": reply
                }
            }
        ]
    }


questions = [
    "Convert 50 dollars to euros.",

]

for question in questions:
    response = fake_ai(
        model="fake-model",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    print(f"User: {question}")
    print(f"Stand-in: {response['choices'][0]['message']['content']}\n")


print("Shape: fake_ai(...) -> response['choices'][0]['message']['content']")