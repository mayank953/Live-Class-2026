"""
_2_oop_classes.py

Classes, taught clean -- no Agent in sight. Class 1 only ever showed
you a class wearing an "Agent" costume; this file is the bare pattern,
on its own, so it actually generalizes instead of feeling like
something you can only use for AI.

Run with: uv run _2_oop_classes.py
"""

# --- A class is a blueprint. An instance is one specific thing built from it. ---

class BankAccount:
    """A blueprint for a bank account -- nothing to do with AI."""

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner       # every instance gets its OWN owner
        self.balance = balance   # and its OWN balance -- this is the account's STATE
        self.history = []        # a list, just like File 1's data structures

    def deposit(self, amount: float) -> None:
        self.balance += amount
        self.history.append(f"Deposited {amount}")

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            print(f"Insufficient funds: tried to withdraw {amount}, balance is {self.balance}")
            return
        self.balance -= amount
        self.history.append(f"Withdrew {amount}")

    def show_history(self) -> None:
        for entry in self.history:
            print(f"  - {entry}")


# Build TWO separate accounts from the same blueprint -- each has its own state.
account_1 = BankAccount(owner="Mayank", balance=1000)
account_2 = BankAccount(owner="Krish", balance=500)

account_1.deposit(200)
account_1.withdraw(50)
account_2.withdraw(1000)   # deliberately too much -- shows the guard clause working

print(f"{account_1.owner}'s balance: {account_1.balance}")
account_1.show_history()

print(f"\n{account_2.owner}'s balance: {account_2.balance}")
account_2.show_history()


# --- @dataclass: the same idea, with less typing ---
# Normally you write __init__ by hand, like BankAccount above. `@dataclass`
# writes that boilerplate FOR you, just from type-hinted attributes.

from dataclasses import dataclass, field


@dataclass
class Book:
    """The same blueprint concept, written the shorter way."""
    title: str
    author: str
    pages_read: int = 0
    # tags = []
    tags: list = field(default_factory=list)   # mutable defaults need field(default_factory=...)

    def read(self, pages: int) -> None:
        self.pages_read += pages

    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)


my_book = Book(title="Atomic Habits", author="James Clear")
my_book.read(40)
my_book.add_tag("self-help")
print(f"\n{my_book}")


if __name__ == "__main__":
    print("\nOOP done. Two completely ordinary classes -- a bank account and a book.")
    print("Hold onto this exact pattern: file 11 today reuses it, unchanged, to define an Agent.")
