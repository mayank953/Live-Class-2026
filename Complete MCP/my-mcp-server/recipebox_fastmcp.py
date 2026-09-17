import logging

from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("recipebox")

recipes = {
    1: {"title": "Weeknight Pasta", "minutes": 20, "tags": ["quick", "vegetarian"]},
    2: {"title": "Slow-Roasted Chicken", "minutes": 150, "tags": ["sunday", "meat"]},
    3: {"title": "Five-Minute Salsa", "minutes": 5, "tags": ["quick", "vegan"]},
}

mcp = FastMCP("RecipeBox")

@mcp.tool()
def list_recipes() -> list[dict]:
    """List every recipe in the box, with id and title only."""
    logger.info("Tool call: list_recipes")
    result = [{"id": k, "title": v["title"]} for k, v in recipes.items()]
    logger.info("Tool result: list_recipes -> %s", result)
    return result

@mcp.tool()
def get_recipe(recipe_id: int) -> dict:
    """Get the full detail for one recipe by id."""
    logger.info("Tool call: get_recipe with recipe_id=%s", recipe_id)
    if recipe_id not in recipes:
        logger.warning("Tool call failed: get_recipe recipe_id=%s not found", recipe_id)
        raise ValueError(f"No recipe with id {recipe_id}")
    result = recipes[recipe_id]
    logger.info("Tool result: get_recipe -> %s", result)
    return result

@mcp.tool()
def search_recipes(tag: str) -> list[dict]:
    """Search recipes by a single tag, valid tags are present in recipe://tags e.g. 'quick' or 'vegetarian'."""
    logger.info("Tool call: search_recipes with tag=%s", tag)
    result = [{"id": k, **v} for k, v in recipes.items() if tag in v["tags"]]
    logger.info("Tool result: search_recipes -> %s", result)
    return result


# resources 
VALID_TAGS=["quick", "vegetarian", "sunday", "meat", "vegan"]

@mcp.resource("recipe://tags")
def get_valid_tags() -> list[str]:
    """Get the list of valid tags for recipes."""
    logger.info("Resource call: get_valid_tags")
    result = VALID_TAGS
    logger.info("Resource result: get_valid_tags -> %s", result)
    return result

@mcp.prompt("recipe://search")
def search_prompt(tag: str) -> str:
    """Prompt for searching recipes by tag."""
    logger.info("Prompt call: search_prompt with tag=%s", tag)
    result = f"Searching for recipes with tag '{tag}'..."
    logger.info("Prompt result: search_prompt -> %s", result)
    return result


if __name__ == "__main__":
    logger.info("Starting RecipeBox MCP server")
    mcp.run()

    # CLIENT_PORT=8080 npx @modelcontextprotocol/inspector python3 recipebox_fastmcp.py
    
    # uv run fastmcp install claude-desktop recipebox_fastmcp.py