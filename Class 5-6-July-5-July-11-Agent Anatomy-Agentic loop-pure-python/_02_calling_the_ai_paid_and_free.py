"""Calling a real AI model: two paid providers, two free providers.

Setup: uv add openai anthropic python-dotenv
.env:  set at least one of OPENAI_API_KEY / ANTHROPIC_API_KEY / GROQ_API_KEY / OPENROUTER_API_KEY
"""

import os

from dotenv import load_dotenv

load_dotenv()


def ask_openai(question: str) -> str:
    """Paid. Calls OpenAI directly using the standard chat completions shape:
    a list of messages in, a single string answer out.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=200,
        messages=[{"role": "user", "content": question}],
    )

    print(response)
    return response.choices[0].message.content # 2024


def ask_anthropic(question: str) -> str:
    """Paid. Anthropic's SDK shape is the one exception among these four:
    it uses .messages.create() instead of .chat.completions.create(), and
    the reply is read from .content[0].text instead of
    .choices[0].message.content. Worth knowing before working with Claude
    directly in a later module.
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def ask_groq(question: str) -> str:
    """Free. Groq uses the OpenAI SDK, pointed at Groq's own base_url --
    the request and response shapes are otherwise identical to ask_openai().
    """
    from openai import OpenAI
    print("Answering question using Groq API...")
    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=200,
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


def ask_openrouter(question: str) -> str:
    """Free. Also OpenAI-shaped. The model name "openrouter/free" auto-routes
    to whichever free model OpenRouter currently has available, so this
    code doesn't go stale if the underlying free model changes.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
    response = client.chat.completions.create(
        model="openrouter/free",
        max_tokens=200,
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


def ask_ai(question: str) -> str:
    """Picks whichever provider has a key set in .env, trying free providers
    first, then paid. Raises clearly if nothing is configured, rather than
    silently returning a placeholder answer.
    """
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


if __name__ == "__main__":
    question = "In one short sentence, what does an AI agent do that a plain chatbot can't?"
    print(ask_ai(question))
