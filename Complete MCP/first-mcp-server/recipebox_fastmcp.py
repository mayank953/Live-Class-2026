from fastmcp import FastMCP

RECIPES = {
    1: {"title": "Weeknight Pasta", "minutes": 20, "tags": ["quick", "vegetarian"]},
    2: {"title": "Slow-Roasted Chicken", "minutes": 150, "tags": ["sunday", "meat"]},
    3: {"title": "Five-Minute Salsa", "minutes": 5, "tags": ["quick", "vegan"]},
}


mcp = FastMCP("RecipeBox_Updated")
@mcp.tool()
def list_recipes() -> list[dict]:
    """List every recipe in the box, with id and title only."""
    return [{"id": k, "title": v["title"]} for k, v in RECIPES.items()]

@mcp.tool()
def get_recipe(recipe_id: int) -> dict:
    """Get the full detail for one recipe by id."""
    if recipe_id not in RECIPES:
        raise ValueError(f"No recipe with id {recipe_id}")
    return RECIPES[recipe_id]

@mcp.tool()
def search_recipes(tag: str) -> list[dict]:
    """Search recipes by a single tag, valid tags are present in recipe://tags e.g. 'quick' or 'vegetarian'."""
    return [{"id": k, **v} for k, v in RECIPES.items() if tag in v["tags"]]


## Resource

VALID_TAGS = ["quick", "vegetarian", "sunday", "meat", "vegan"]

@mcp.resource("recipe://tags")
def valid_tags() -> list[str]:
    """Return a list of all valid tags for recipes."""
    return VALID_TAGS


@mcp.prompt
def search_for_quick_recipes() -> str:
    """Search for recipes that are quick to make. Please use the search_recipes tool with the tag 'quick'."""
    return "I will search for recipes that are quick to make."

@mcp.prompt
def send_email() -> str:
    """Plan a week's worth of meals, using only recipes from the box."""
    return "I will plan a week's worth of meals using the recipes in the RecipeBox."


if __name__ == "__main__":
    mcp.run()


# CLIENT_PORT=9999 npx @modelcontextprotocol/inspector python3 recipebox_fastmcp.py


# uv run fastmcp install claude-desktop recipebox_fastmcp.py

# which uv