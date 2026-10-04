# MCP Interview Questions

## Q1. How does the agent discover MCP servers and their capabilities?

- It doesn't "find" them. Servers come from config or an allowlisted registry.
- The `initialize` handshake has both sides declare capabilities.
- `tools/list` returns name, description and schema. That is what the LLM sees.

Tool descriptions are prompt input. Pin and review them.

## Q2. How do you handle authN/authZ between the agent and MCP servers?

- The MCP server acts as an OAuth 2.1 resource server.
- A 401 with resource metadata leads the client to auth code + PKCE.
- The token is short-lived and audience-bound to that one server.
- No passthrough. Downstream APIs get a token exchange.

## Q3. How do you scope OAuth per capability, especially for sensitive actions?

- One tool, one scope. `payments:read` ≠ `payments:transfer`.
- Check the scope on every `tools/call` and filter `tools/list` by scope.
- A missing scope returns 403 `insufficient_scope`, followed by step-up and human approval.
- Amount, env and tenant limits live in gateway policy, with an audit log per user and per agent.

## Q4. How did you run an MCP server with multiple replicas when streamable HTTP sessions are stateful?

By default a streamable HTTP server is stateful: `initialize` returns an `Mcp-Session-Id`, and the server keeps that session in memory. If the next request lands on a different replica, that replica does not know the session and rejects it.

Three ways out:

- **Run the server stateless** (preferred for request/response tool servers). Each request is self-contained, so any replica can serve it. In the Python SDK this is `FastMCP(..., stateless_http=True)`. You lose server-initiated messages, which most tool servers never use.
- **Sticky routing** on the `Mcp-Session-Id` header at the ingress or service mesh. Avoid Kubernetes `sessionAffinity: ClientIP` for this: every request from one agent pod then pins to one replica, so load is not balanced.
- **Shared session store** (e.g. Redis). Works, but adds a dependency for little gain.

Verify it by scaling to 2+ replicas and running a multi-turn conversation.

## Q5. How did you make sensitive tool calls like transfers idempotent across retries and pod failures?

Risk: the database commits, the agent dies before the response, and a retry moves the money twice.

- Pass an **idempotency key** as a tool argument (MCP has none built in).
- Store the key **in the same transaction** as the transfer; a repeat returns the stored result.
- Re-check balances **at execution**, not at approval.

## Q6. How did you keep the agent's tool list in sync when an MCP server changes its tool contract?

Treat the tool schema and description as an API contract.

- **Only additive changes in place:** new tools, new optional parameters. A breaking change (renamed or removed parameter) ships as a new tool name alongside the old one; remove the old one once no agent uses it.
- **Agents usually load tools once at startup,** so a server change only takes effect after the agents restart. Either roll the agents after a server change, or handle `notifications/tools/list_changed` to refresh the list at runtime.
- **Descriptions change model behaviour.** The model picks tools by their descriptions, so a docstring edit can change routing. Run server changes through the same agent eval suite as agent changes.
- In CI, **snapshot `tools/list` and diff it** so contract changes are visible in review.

## Q7. How did you tell tool failures apart from empty results, both for the model and for monitoring?

Keep three outcomes distinct:

- **Success with data.**
- **Success, but empty:** an explicit empty result such as `{"count": 0, "items": []}`, so the model can truthfully say "no transactions".
- **Failure:** a tool result with `isError: true` and a message the model can act on, e.g. "Account not found; call list_accounts first". Invalid requests (bad parameters) are protocol-level JSON-RPC errors.

Returning `{"error": ...}` as a normal successful result is the anti-pattern: the model may treat it as data, and your metrics count it as a success.

For monitoring, emit a per-tool metric on the server labelled `ok`, `empty` or `error`. HTTP status codes will not help, because tool errors still travel as HTTP 200. Page on infrastructure errors (database down, timeouts). Let the model handle user-input errors (unknown account, bad date).

## Q8. What changed in the latest MCP spec, and how does it affect how you run MCP servers?

The July 2026 spec (2026-07-28) made MCP stateless: every request stands alone, like a normal HTTP API.

- **No `initialize` handshake.** Version and capabilities travel in `_meta` on every request.
- **No sessions.** `Mcp-Session-Id` is gone, so any replica serves any request; no sticky routing.
- **State moves into tools.** Cross-call state becomes a handle the tool returns (e.g. `basket_id`).
- **Deprecated:** Sampling, Roots, Logging, the old HTTP+SSE transport, and Dynamic Client Registration.

Most production servers still run 2025-11-25, where sessions are optional but stateful by default.

**What replaces the Deprecated features**

- Roots: pass paths as tool parameters.
- Sampling: call the LLM provider's API directly.
- Logging: use OpenTelemetry or stderr.
- HTTP+SSE: move to Streamable HTTP.
- Dynamic Client Registration: replaced by Client ID Metadata Documents.
