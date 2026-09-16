"""
RecipeBox -- built with the RAW, low-level official `mcp` SDK.

No decorators-that-do-magic here. Every piece of plumbing the protocol
needs -- describing tools with hand-written JSON Schema, dispatching a
call to the right function by name, wiring up the stdio transport --
is written out in full, on purpose. This is what FastMCP is quietly
doing FOR you in the next file.

Install: pip install mcp
Run:     python3 recipebox_lowlevel.py
Inspect: npx @modelcontextprotocol/inspector python3 recipebox_lowlevel.py
"""
import asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# ---------- the actual data, same as every other version of RecipeBox in this course ----------
RECIPES = {
    1: {"title": "Weeknight Pasta", "minutes": 20, "tags": ["quick", "vegetarian"]},
    2: {"title": "Slow-Roasted Chicken", "minutes": 150, "tags": ["sunday", "meat"]},
    3: {"title": "Five-Minute Salsa", "minutes": 5, "tags": ["quick", "vegan"]},
}

server = Server("RecipeBox")


# ---------- Step 1 of 2: describe every tool by hand, as JSON Schema ----------
# Notice: this is pure description. Nothing here actually RUNS anything yet.
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_recipes",
            description="List every recipe in the box, with id and title only.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_recipe",
            description="Get the full detail for one recipe by id.",
            inputSchema={
                "type": "object",
                "properties": {"recipe_id": {"type": "integer"}},
                "required": ["recipe_id"],
            },
        ),
        types.Tool(
            name="search_recipes",
            description="Search recipes by a single tag, e.g. 'quick' or 'vegetarian'.",
            inputSchema={
                "type": "object",
                "properties": {"tag": {"type": "string"}},
                "required": ["tag"],
            },
        ),
    ]


# ---------- Step 2 of 2: dispatch a call to the right function, by hand ----------
# Notice: WE write the if/elif chain matching a name to real logic.
# FastMCP generates both this AND the schema above from one plain function.
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    if name == "list_recipes":
        result = [{"id": k, "title": v["title"]} for k, v in RECIPES.items()]
    elif name == "get_recipe":
        recipe_id = arguments["recipe_id"]
        if recipe_id not in RECIPES:
            raise ValueError(f"No recipe with id {recipe_id}")
        result = RECIPES[recipe_id]
    elif name == "search_recipes":
        tag = arguments["tag"]
        result = [{"id": k, **v} for k, v in RECIPES.items() if tag in v["tags"]]
    else:
        raise ValueError(f"Unknown tool: {name}")

    return [types.TextContent(type="text", text=str(result))]


# ---------- the transport wiring -- also written out by hand ----------
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
