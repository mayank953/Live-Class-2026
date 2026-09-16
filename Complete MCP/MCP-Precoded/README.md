# Building Your First MCP Server — RecipeBox, Two Ways

The same server, built twice: once with the raw official `mcp` SDK, once with the
standalone `fastmcp` package. Same three tools, same behavior, verified identical.

## Setup

```bash
# For the raw version
pip install mcp

# For the FastMCP version
pip install fastmcp
```

## Run either one

```bash
python3 recipebox_lowlevel.py
# or
python3 recipebox_fastmcp.py
```

## Inspect either one

```bash
npx @modelcontextprotocol/inspector python3 recipebox_lowlevel.py
npx @modelcontextprotocol/inspector python3 recipebox_fastmcp.py
```

Both expose the identical three tools — `list_recipes`, `get_recipe`, `search_recipes` —
and produce identical results when called. Try both, side by side.

## The real comparison

| | `recipebox_lowlevel.py` | `recipebox_fastmcp.py` |
|---|---|---|
| Lines of real code (no comments/blanks) | 72 | 31 |
| JSON Schema | Hand-written | Generated from type hints |
| Tool dispatch | Manual if/elif chain | Generated from function names |
| Transport wiring | Explicit `stdio_server()` context manager | Hidden inside `mcp.run()` |

## Files

- `recipebox_lowlevel.py` — the raw official SDK version, heavily commented
- `recipebox_fastmcp.py` — the FastMCP version, heavily commented
- `part4_building_first_server_notebook.ipynb` — full walkthrough, both servers built
  and tested live, with the line-count comparison computed (not just claimed)

## A note on the two packages

`mcp` and `fastmcp` are two separate, independently-installed Python packages. The
official SDK also ships its own bundled high-level class, which was renamed in its
newest major version specifically to avoid confusion with the standalone `fastmcp`
project — which remains the more widely-used choice for real-world servers today.
