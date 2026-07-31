"""Structural comparison: AI model vs. chatbot vs. agent.

No API calls in this file on purpose -- the goal is to see the SHAPE of
the difference in plain Python before any real model is involved.
"""


def ai_model(question: str) -> str:
    """A single one-shot prediction. Takes a question, returns an answer,
    and remembers nothing about any call that happened before or after it.
    This is the whole capability of a raw model with no wrapping around it.
    """
    return f"[Mock prediction for]: {question}"


class Chatbot:
    """Wraps ai_model() with conversation history.

    Each call to ask() appends both the question and the answer to
    self.history, so the next call can (in a real implementation) see
    everything said before. It still has no ability to check anything
    in the real world -- only to talk, with better memory of the chat.
    """

    def __init__(self) -> None:
        self.history: list[dict] = []

    def ask(self, question: str) -> str:
        self.history.append({"role": "user", "content": question})
        answer = ai_model(question)
        self.history.append({"role": "assistant", "content": answer})
        return answer


class Agent:
    """Wraps ai_model() with history AND a set of tools it can choose to use.

    decide_tool() here is a simple keyword match, only good enough to
    illustrate the idea of "the assistant picks a tool." It is NOT how
    real decision-making works -- File 5 replaces this with a real model
    actually making that choice based on meaning, not string matching.
    """

    def __init__(self, tools: dict[str, callable]) -> None:
        self.history: list[dict] = []
        self.tools = tools

    def decide_tool(self, question: str) -> str | None: # question - use calculator tool to tell what is 2 + 2
        for name in self.tools:  # self.tools = ['weather']
            if name in question.lower():
                return name
        return None

    def ask(self, question: str) -> str:
        self.history.append({"role": "user", "content": question})
        tool_name = self.decide_tool(question)

        if tool_name is not None:
            result = self.tools[tool_name]()
            answer = f"[used tool: {tool_name}] {result}"
        else:
            answer = ai_model(question)

        self.history.append({"role": "assistant", "content": answer})
        return answer


if __name__ == "__main__":
    def weather() -> str:
        return "22C, partly cloudy"

    chatbot = Chatbot()
    print(chatbot.ask("What's the capital of France?"))

    agent = Agent(tools={"weather": weather})
    print(agent.ask("What's the weather like today?"))
    print(agent.ask("What's the capital of France?"))

# stub ======= mock