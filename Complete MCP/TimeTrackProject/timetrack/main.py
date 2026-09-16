"""
TimeTrack -- one running application, two front doors onto the same
SQLite database of logged time entries:

  1. A real website (served from ./static) -- for people, in a browser
  2. An MCP server, mounted at /mcp -- for AI assistants, over HTTP

Both talk to the exact same database.py functions.

Setup:
    uv init .
    uv add fastmcp fastapi "uvicorn[standard]"
    uv run uvicorn main:app --reload

Then visit http://127.0.0.1:8000 for the website,
and http://127.0.0.1:8000/mcp is the MCP endpoint (Streamable HTTP).
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastmcp import FastMCP

import database as db

# ---------- persistence, initialized once at startup ----------
db.init_db()

# ---------- Step 1: build the MCP server FIRST ----------
# Hand-curated tools, calling the SAME database functions the REST API
# below uses -- nothing duplicated between the two front doors.
mcp = FastMCP("TimeTrack")


@mcp.tool
def log_time(employee_name: str, project: str, entry_date: str, hours: float, description: str = "") -> dict:
    """Log a time entry. entry_date must be YYYY-MM-DD. Shows up on the website immediately."""
    return db.log_time(employee_name, project, entry_date, hours, description)


@mcp.tool
def get_timesheet(employee_name: str, start_date: str = "", end_date: str = "") -> list[dict]:
    """Get one employee's logged entries, optionally filtered to a date range (YYYY-MM-DD)."""
    return db.get_timesheet(employee_name, start_date or None, end_date or None)


@mcp.tool
def get_project_summary(project: str) -> dict:
    """Get total hours logged against a project, broken down by employee."""
    return db.get_project_summary(project)


@mcp.tool
def list_projects() -> list[str]:
    """List every project that has at least one logged time entry."""
    return db.list_projects()


@mcp.resource("timesheet://projects")
def known_projects() -> list[str]:
    """The current set of projects with logged time, for consistent naming."""
    return db.list_projects()


@mcp.prompt
def generate_weekly_report(employee_name: str, week_start: str) -> str:
    """Guides the AI to build a structured weekly hours report from this server's own tools."""
    return f"""Build a weekly report for {employee_name}, starting {week_start}.

1. Call get_timesheet with employee_name='{employee_name}', start_date='{week_start}'
2. Group the results by project
3. Present it as:
   {{employee_name}} -- Week of {week_start}
   [Project]: {{total hours for that project}}h
   Total: {{sum of all hours}}h

If no entries are found for that week, say so plainly instead of inventing data.
"""


# path="/" here, NOT "/mcp" -- app.mount() below adds that prefix.
# Setting both would double up into /mcp/mcp -- a real, easy-to-miss bug,
# verified against FastMCP's own documentation.
mcp_app = mcp.http_app(path="/")


# ---------- Step 2: build the FastAPI app, lifespan wired in AT CONSTRUCTION ----------
app = FastAPI(title="TimeTrack", lifespan=mcp_app.lifespan)


class NewEntry(BaseModel):
    employee_name: str
    project: str
    entry_date: str
    hours: float
    description: str = ""


@app.get("/api/entries")
def api_list_entries():
    return db.list_all_entries()


@app.post("/api/entries")
def api_log_entry(entry: NewEntry):
    return db.log_time(entry.employee_name, entry.project, entry.entry_date, entry.hours, entry.description)


@app.get("/api/projects")
def api_list_projects():
    return db.list_projects()


@app.get("/api/projects/{project}/summary")
def api_project_summary(project: str):
    return db.get_project_summary(project)


@app.get("/api/timesheet/{employee_name}")
def api_get_timesheet(employee_name: str, start_date: str = None, end_date: str = None):
    return db.get_timesheet(employee_name, start_date, end_date)


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/mcp", mcp_app)
