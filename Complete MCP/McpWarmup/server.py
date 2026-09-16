from fastmcp import FastMCP

mcp = FastMCP("Warm-Up Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to MCP."

@mcp.tool
def query_db(a: int, b: int,c:int) -> int:
    """Query the database with three parameters."""

    return a + b + c

if __name__ == "__main__":
    mcp.run()

# uv run python server.py
# npx -y @modelcontextprotocol/inspector uv run python server.py

