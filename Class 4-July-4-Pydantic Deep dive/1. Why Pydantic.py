


name : str = "Pydantic"

tags: list[str] = ["python", "pydantic", "fastapi"]
quantities: list[int] = [1, 5, 3, 2]
word_counts: dict[str, int] = {"error": 12, "warning": 5}
settings: dict[str, str] = {"theme": "dark", "language": "en"}

print(tags, quantities, word_counts, settings)


tags
settings

name


from pydantic import BaseModel,EmailStr