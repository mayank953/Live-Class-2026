from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from fastmcp.server.dependencies import get_access_token


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

# DEVELOPMENT ONLY
#
# Each token represents a different user/role.
#
# user-token    -> user role
# analyst-token -> analyst role
# admin-token   -> admin role

auth = StaticTokenVerifier(
    tokens={
        "user-token": {
            "client_id": "normal-user",
            "scopes": ["user"],
        },

        "analyst-token": {
            "client_id": "data-analyst",
            "scopes": ["user", "analyst"],
        },

        "admin-token": {
            "client_id": "administrator",
            "scopes": ["user", "analyst", "admin"],
        },
    }
)


mcp = FastMCP(
    "Warm-Up Server",
    auth=auth
)


# =========================================================
# USER TOOLS
# =========================================================

@mcp.tool(auth=require_scopes("user"))
def greet(name: str) -> str:
    """
    Greet someone by name.

    Role:
        user
        analyst
        admin
    """

    return f"Hello, {name}! Welcome to MCP."


@mcp.tool(auth=require_scopes("user"))
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers.

    Role:
        user
        analyst
        admin
    """

    return a + b


# =========================================================
# ANALYST TOOLS
# =========================================================

@mcp.tool(auth=require_scopes("analyst"))
def query_db(a: int, b: int, c: int) -> int:
    """
    Query database example.

    Role:
        analyst
        admin
    """

    return a + b + c


@mcp.tool(auth=require_scopes("analyst"))
def calculate_average(numbers: list[float]) -> float:
    """
    Calculate average of numbers.

    Role:
        analyst
        admin
    """

    if not numbers:
        return 0

    return sum(numbers) / len(numbers)


@mcp.tool(auth=require_scopes("analyst"))
def sales_report(month: str) -> dict:
    """
    Return a mock sales report.

    Role:
        analyst
        admin
    """

    return {
        "month": month,
        "revenue": 125000,
        "orders": 430,
        "customers": 310,
    }


# =========================================================
# ADMIN TOOLS
# =========================================================

@mcp.tool(auth=require_scopes("admin"))
def list_users() -> list[dict]:
    """
    List users.

    Role:
        admin only
    """

    return [
        {
            "id": 1,
            "name": "Mayank",
            "role": "admin",
        },
        {
            "id": 2,
            "name": "Alice",
            "role": "analyst",
        },
        {
            "id": 3,
            "name": "Bob",
            "role": "user",
        },
    ]


@mcp.tool(auth=require_scopes("admin"))
def delete_user(user_id: int) -> str:
    """
    Delete a user.

    Role:
        admin only
    """

    return f"User {user_id} deleted successfully."


# =========================================================
# OPTIONAL TOOL - SEE CURRENT AUTH USER
# =========================================================

@mcp.tool(auth=require_scopes("user"))
def who_am_i() -> dict:
    """
    Show information about the authenticated client.
    """

    token = get_access_token()

    return {
        "client_id": token.client_id,
        "scopes": token.scopes,
    }


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------

if __name__ == "__main__":

    
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
    )