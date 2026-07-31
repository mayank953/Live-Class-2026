"""
_11_agent_class_ai_only.py

File 2's exact OOP pattern (BankAccount, Book) -- reused, unchanged in
structure, now to define an Agent. Today it only does ONE thing: hold a
conversation with its brain (File 7/10's AI call). No tools yet.

Run with: uv run _11_agent_class_ai_only.py
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Agent:
    """Same blueprint shape as File 2's Book class: a name, some state,
    and methods that act on that state. Nothing here is a new pattern --
    it's the bank account and the book, wearing a new label."""

    name: str
    system_prompt: str
    messages: list = field(default_factory=list)   # File 1's data structures: a list of dicts

    def remember(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def show_transcript(self) -> None:
        for turn in self.messages:
            print(f"{turn['role']:>9}: {turn['content']}")

    def ask_brain(self, question: str) -> str:
        """Talk to the AI -- real if a key exists, the File 6 stand-in if not."""
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

    # No tools attribute. No ability to call one. This Agent is, today,
    # exactly a chatbot -- all brain, no hands. File 12 changes that.


if __name__ == "__main__":
    trip_planner = Agent(name="Trip Planner", system_prompt="You help people plan trips.")

    answer = trip_planner.ask_brain("In one sentence, what's the first thing to plan for a trip abroad?")
    print(answer)

    print("\n--- Transcript ---")
    trip_planner.show_transcript()

    print("\nThis Agent can talk. It cannot yet DO anything beyond talking. File 12 gives it hands.")
