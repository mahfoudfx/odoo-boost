# Architecture

Odoo Boost sits between AI coding agents and your Odoo instance / codebase. It
has no server-side Odoo component: everything runs locally and connects over
standard XML-RPC.

```text
┌─────────────────────────┐     stdio / HTTP     ┌─────────────────────────────────┐
│        AI Agent         │◄────────────────────►│        Odoo Boost MCP            │
│ (Antigravity, Claude,   │                      │  registry → tools               │
│  Cursor, OpenCode, ...) │                      │  ContextVar(connection, config) │
└───────────┬─────────────┘                      └───────────┬─────────────────────┘
            │                                                 │
            ▼                                                 ▼
   Guidelines, skills,                          ┌───────────────────────────┐
   generated MCP configs                        │  XML-RPC                  │
   (written by agent adapters)                  │  AST/XML scanner (local)  │
                                                │  pylint-odoo / odoo-ls    │
                                                └───────────────────────────┘
```

## Runtime components

| Module | Responsibility |
|---|---|
| `cli/` | Typer commands: `install`, `check`, `lint`, `update`, `mcp`, `mcp-config` |
| `config/` | Pydantic schema and `odoo-boost.json` load/save (owner-only perms) |
| `mcp_launcher.py` | Resolves the stdio command for native/WSL targets and builds HTTP URLs |
| `mcp_server/server.py` | Assembles the MCP v2 server (resources, prompts, tool loop) |
| `mcp_server/registry.py` | Single source of truth for the 23 tools (`LIVE_TOOLS` / `LOCAL_TOOLS`) |
| `mcp_server/context.py` | `ContextVar` holding the active connection + config |
| `mcp_server/auth.py` | Static bearer-token verifier for HTTP |
| `mcp_server/policy.py` | Opt-in `readonly` / `allowed_roots` guardrails |
| `mcp_server/tools/` | One module per tool plus `_common.py` response helpers |
| `versions.py` | Registered Odoo series, inherited compatibility facts and documentation paths |
| `agents/` | Declarative `AgentSpec` registry + spec-driven base class |
| `connection/` | Abstract connection interface and the XML-RPC implementation |
| `ast_scanner/` | Pure-Python AST/XML analysis of local addons (no Docker) |
| `guidelines/`, `skills/` | Bundled markdown content loaded via `importlib.resources` |
| `logging_config.py` | stderr-only logging; stdout is reserved for the MCP wire |

## Tool-call lifecycle

1. The agent launches the server over stdio (`python -m odoo_boost mcp -c …`) or
   connects to a running HTTP endpoint.
2. `create_mcp_server()` opens the Odoo connection, stores it in the
   `ContextVar`, and registers `LIVE_TOOLS` (wrapped to surface connection
   failures as `ToolError`) and `LOCAL_TOOLS`.
3. A tool resolves `get_connection()` / `get_context()` and returns JSON.
   Live tools use `_common.json_response`; file tools first pass through
   `policy.enforce_path`.
4. Errors are logged to stderr; protocol messages stay on stdout.

## Configuration generation

`install` and `update` instantiate each selected agent with its `AgentSpec`
(paths + output format) and write:

- **Guidelines** — a compact fast/deep router and effective version contract in
  the agent's native file; complete expert topics are installed as references.
- **MCP config** — JSON/TOML/YAML in the format the agent expects.
- **Skills** — the 23 bundled skills plus `SKILLS_ROUTING.md`.

Generated guideline sections and Odoo Boost MCP entries are updated in place;
unrelated user content and other MCP servers are preserved. Edited generated
sections are left for the user to reconcile. Existing configurations retain
explicit option values such as `lean_tools`.

Version guidance follows shared Odoo topics → registered version facts and
delta note → task-specific skill or tool. Unknown series receive shared topics
and an uncertainty warning rather than inheriting the newest release. See
[version support](versions.md) for the onboarding sequence.

The generated router selects first-pass coding automatically for small field,
label, translation, and view edits. It keeps version facts active but avoids MCP
calls, plans, broad scans, and unrelated skills. Medium effort covers bounded
multi-file features, localized refactoring, and packaging with focused checks.
High effort progressively loads expert material for broad refactors, production
readiness, security, migrations, audits, accounting/stock integrity, and failed
lower-effort attempts.

For stdio, `mcp_target: "auto"` writes the native config plus a `*.windows.*`
companion that wraps the interpreter in `wsl.exe`. For `mcp_transport: "http"`,
URL-based configs are written instead (with an `Authorization` header when a
token is configured).

## Extension points

- **New tool** → add a module under `mcp_server/tools/` and register it in
  `mcp_server/registry.py` (`LIVE_TOOLS` or `LOCAL_TOOLS`). See
  [CONTRIBUTING](../CONTRIBUTING.md).
- **New agent** → add an `AgentSpec` and a thin wrapper class. `id`,
  `display_name`, paths, and serialization are derived from the spec.
- **New transport** → extend `mcp_launcher.py` and `cli/mcp_cmd.py`.
- **New Odoo version** → register an explicit parent and changed facts in
  `versions.py`, then add the targeted note, docs and regression tests.

## Security boundaries

See [SECURITY.md](../SECURITY.md). In short: credentials live in
`odoo-boost.json` (owner-only, plaintext), HTTP non-loopback binds require a
token, and `readonly` / `allowed_roots` are defense-in-depth rather than a
sandbox.

## Selective patterns from related projects

The optional `source_trace` skill adopts source-first tracing and a short context
brief for coupled changes, inspired by [Agent Skills](https://github.com/unclecatvn/agent-skills)
and the [universal Odoo development skill](https://github.com/fhidalgodev/odoo-development-skill).
`count_records` adopts the useful count-only query from
[Vauxoo's MCP server](https://github.com/Vauxoo/mcp.odoo). These are native
Odoo Boost features, not runtime dependencies on those projects. The response
cap, compact modes, and full-detail escape hatches retain the useful part of
[Letzdoo's token-saving approach](https://github.com/letzdoo/claude-marketplace)
without filtering source files or hiding test failures. A database index, global
command hook, or per-call environment profiles would add setup and security
complexity to the current project-scoped server; use an external project tool
when those workflows are actually needed.
