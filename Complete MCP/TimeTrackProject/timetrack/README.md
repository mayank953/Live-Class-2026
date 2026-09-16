# TimeTrack

A real timesheet tool — log billable hours through a browser, or through an
AI assistant, and both see the exact same data.

## Complete Setup Checklist

1. Install `uv`
2. `uv init .`
3. `uv add fastmcp fastapi "uvicorn[standard]"`
4. `uv run fastmcp version` — confirm the install
5. This repo's `database.py`, `main.py`, and `static/` are already written for you
6. `uv run uvicorn main:app --reload`
7. Visit `http://127.0.0.1:8000` (website) and `http://127.0.0.1:8000/mcp` (MCP)
8. Connect Claude Desktop (see below)
9. Deploy to Prefect Horizon for a public URL (see below)

## What's inside

| Primitive | Name | What it does |
|---|---|---|
| Tool | `log_time` | Logs a new time entry — appears on the website immediately |
| Tool | `get_timesheet` | One employee's entries, optionally filtered by date range |
| Tool | `get_project_summary` | Total hours per project, broken down by employee (real `GROUP BY`) |
| Tool | `list_projects` | Every project with at least one logged entry |
| Resource | `timesheet://projects` | The current set of known project names |
| Prompt | `generate_weekly_report` | Structures a weekly hours report request |

## Connecting Claude Desktop

```json
{
  "mcpServers": {
    "timetrack": { "url": "http://127.0.0.1:8000/mcp" }
  }
}
```

## Two rules that matter in `main.py` (verified against official FastMCP docs)

1. `mcp.http_app(path="/")` — not `"/mcp"` — since `app.mount("/mcp", mcp_app)`
   already adds that prefix. Setting both doubles it into `/mcp/mcp`.
2. `FastAPI(lifespan=mcp_app.lifespan)` — passed at construction, not set
   afterward — or the MCP session manager silently never initializes.

## Going live: Prefect Horizon

Formerly known as FastMCP Cloud — same team, same idea, current name verified
before writing this. Free for personal projects.

1. Push this project to a GitHub repo
2. Sign in to [Prefect Horizon](https://gofastmcp.com/v2/deployment/fastmcp-cloud) with GitHub
3. Connect the repo — dependencies auto-detected from `pyproject.toml`
4. Optionally verify first: `fastmcp inspect main.py:mcp`
5. Deploy — live at `https://your-project-name.fastmcp.app/mcp`

Worth confirming directly whether the website's static routes come along with
the deployment — Horizon is purpose-built for the MCP piece specifically. If
not, deploying the whole app to a general host like Railway is the fallback.

## Files

- `database.py` — SQLite persistence, tested including real aggregation and a
  genuine restart-and-recover proof
- `main.py` — FastAPI app with MCP mounted in, using the verified-correct
  mounting pattern
- `static/` — the original frontend (3 tabs: entries, summary, log time)
- `timetrack_notebook.ipynb` — full walkthrough, database layer fully executed
  live
