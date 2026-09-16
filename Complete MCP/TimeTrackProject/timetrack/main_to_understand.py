from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles



import database as db
from pydantic import BaseModel

db.init_db() # Initialize the database and seed it with initial data if empty


app = FastAPI(title="TimeTrack", description="A simple time tracking app with REST and MCP endpoints.", version="1.0.0")

@app.get("/api/entries")
def api_list_all_entries():
    """List all time entries in the database."""
    return db.list_all_entries()


@app.get("/api/projects")
def api_list_projects():
    return db.list_projects()


@app.get("/api/projects/{project}/summary")
def api_project_summary(project: str):
    return db.get_project_summary(project)


@app.get("/api/timesheet/{employee_name}")
def api_get_timesheet(employee_name: str, start_date: str = None, end_date: str = None):
    return db.get_timesheet(employee_name, start_date, end_date)



class NewEntry(BaseModel):
    employee_name: str
    project: str
    entry_date: str
    hours: float
    description: str = ""

@app.post("/api/entries")
def api_log_entry(entry: NewEntry):
    return db.log_time(entry.employee_name, entry.project, entry.entry_date, entry.hours, entry.description)


# uvicorn main_to_understand:app --port 9998

# uv run uvicorn main_to_understand:app --port 9998 -reload
# http://127.0.0.1:9998/docs ------> Open swagger page, port should be right.


## MCP Server 


from fastmcp import FastMCP

# Assumes the FastAPI app from above is already defined

# Convert to MCP server
mcp = FastMCP.from_fastapi(app=app)



if __name__ == "__main__":
    mcp.run()


@mcp.tool()
def execute_query_dynamically(query: str, params: list = []) -> list[dict]:
    """Execute a custom SQL query with optional parameters. Access the resource for schema so that you know the tables etc."""
    
    return db.execute_query(query, params)

@mcp.resource("timesheet://schema")
def get_schema() -> dict:
    """Return the database schema for reference."""
    return {
        "tables": {
            "time_entries": {
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "employee_name": "TEXT NOT NULL",
                    "project": "TEXT NOT NULL",
                    "entry_date": "TEXT NOT NULL",
                    "hours": "REAL NOT NULL",
                    "description": "TEXT"
                }
            }
        }
    }

# @mcp.tool()
# def log_time(employee_name: str, project: str, entry_date: str, hours: float, description: str = "") -> dict:
#     """Log a time entry. entry_date must be YYYY-MM-DD. Shows up on the website immediately."""
#     return db.log_time(employee_name, project, entry_date, hours, description)



# @mcp.tool
# def get_timesheet(employee_name: str, start_date: str = "", end_date: str = "") -> list[dict]:
#     """Get one employee's logged entries, optionally filtered to a date range (YYYY-MM-DD)."""
#     return db.get_timesheet(employee_name, start_date or None, end_date or None)


# @mcp.tool
# def get_project_summary(project: str) -> dict:
#     """Get total hours logged against a project, broken down by employee."""
#     return db.get_project_summary(project)


# @mcp.tool
# def list_projects() -> list[str]:
#     """List every project that has at least one logged time entry."""
#     return db.list_projects()


# @mcp.resource("timesheet://projects")
# def known_projects() -> list[str]:
#     """The current set of projects with logged time, for consistent naming."""
#     return db.list_projects()


# @mcp.prompt
# def generate_weekly_report(employee_name: str, week_start: str) -> str:
#     """Guides the AI to build a structured weekly hours report from this server's own tools."""
#     return f"""Build a weekly report for {employee_name}, starting {week_start}.

# 1. Call get_timesheet with employee_name='{employee_name}', start_date='{week_start}'
# 2. Group the results by project
# 3. Present it as:
#    {{employee_name}} -- Week of {week_start}
#    [Project]: {{total hours for that project}}h
#    Total: {{sum of all hours}}h

# If no entries are found for that week, say so plainly instead of inventing data.
# """



if __name__ == "__main__":
    mcp.run()