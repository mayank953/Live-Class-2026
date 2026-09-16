"""
RecipeBox -- the EXACT same server as recipebox_lowlevel.py, rebuilt with
the standalone `fastmcp` package. Same tools, same behavior, same result
if you call it from Inspector. Count the lines.

Install: pip install fastmcp
Run:     python3 recipebox_fastmcp.py    (or: fastmcp dev recipebox_fastmcp.py)
Inspect: uv run fastmcp dev recipebox_fastmcp.py
"""
from fastmcp import FastMCP

RECIPES = {
    1: {"title": "Weeknight Pasta", "minutes": 20, "tags": ["quick", "vegetarian"]},
    2: {"title": "Slow-Roasted Chicken", "minutes": 150, "tags": ["sunday", "meat"]},
    3: {"title": "Five-Minute Salsa", "minutes": 5, "tags": ["quick", "vegan"]},
}

mcp = FastMCP("RecipeBox")


@mcp.tool
def list_recipes() -> list[dict]:
    """List every recipe in the box, with id and title only."""
    return [{"id": k, "title": v["title"]} for k, v in RECIPES.items()]


@mcp.tool
def get_recipe(recipe_id: int) -> dict:
    """Get the full detail for one recipe by id."""
    if recipe_id not in RECIPES:
        raise ValueError(f"No recipe with id {recipe_id}")
    return RECIPES[recipe_id]


@mcp.tool
def search_recipes(tag: str) -> list[dict]:
    """Search recipes by a single tag, e.g. 'quick' or 'vegetarian'."""
    return [{"id": k, **v} for k, v in RECIPES.items() if tag in v["tags"]]


if __name__ == "__main__":
    mcp.run()


# CLIENT_PORT=9999 npx @modelcontextprotocol/inspector python3 recipebox_fastmcp.py