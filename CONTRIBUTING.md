# Contributing to Odoo Boost

## Development Setup

```bash
git clone https://github.com/mahfoudfx/odoo-boost.git
cd odoo-boost

# Create the venv and install the locked development dependencies
uv sync --extra dev
source .venv/bin/activate

# Optional: run the checks automatically on commit
pre-commit install

# Verify
odoo-boost --version
```

`uv.lock` is committed; CI installs from it with `uv sync --frozen`. Re-lock
after changing dependencies with `uv lock`.

## Project Layout

```
src/odoo_boost/
├── ast_scanner/            # Fast, pure-Python AST & XML analyzer (Docker-Free)
├── cli/                    # Typer CLI commands (install, check, lint, update, mcp)
├── config/                 # Pydantic schema + load/save helpers
├── connection/             # Abstract base + XML-RPC client
├── mcp_server/
│   ├── server.py           # MCP v2 server assembly (resources + prompts)
│   ├── registry.py         # Single source of truth for the 23 tools
│   ├── context.py          # ContextVar holding connection + config
│   ├── auth.py             # Static bearer-token verifier for HTTP
│   ├── policy.py           # Opt-in readonly / allowed_roots guardrails
│   └── tools/              # 23 MCP tools (one file per tool)
│       └── _common.py      # Shared JSON/error/compaction helpers
├── agents/                 # 11 agent adapters + base class + declarative specs
│   ├── spec.py             # AgentSpec registry (paths + output format)
│   └── base.py             # Spec-driven Agent base class
├── guidelines/
│   ├── composer.py         # Assembles markdown into unified agent prompt
│   └── core/               # 10 core markdown topics + versions (v14-v20)
├── skills/                 # 23 skills (Core, Workflows, Domain Patterns) + routing
├── versions.py             # Registered series, inherited compatibility facts and doc paths
├── logging_config.py       # stderr-only logging (stdout is the MCP wire)
└── mcp_launcher.py         # native/WSL/HTTP command + URL resolution
```

## Pure-Python & Docker-Free Rule

A foundational constraint of Odoo Boost is that local static inspection must remain **lightweight, fast, and completely free of Docker or external heavy daemons**:
- AST analysis relies on Python's standard `ast` module.
- XML analysis relies on `defusedxml` (with `xml.etree` fallback) for hardened, zero-dependency parsing.
- External tools like `pylint-odoo`, `lxml`, and `odoo-ls` must always be optional with graceful fallbacks.

## Adding a New MCP Tool

1. **Create the tool file** at `src/odoo_boost/mcp_server/tools/my_tool.py`:

```python
"""MCP tool: my_tool – short description."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response

def my_tool(param1: str, limit: int = 10) -> str:
    """One-line description shown to the AI agent.

    Args:
        param1: Description of param1.
        limit: Max records.
    """
    conn = get_connection()
    records = conn.search_read("ir.model", [], fields=["model", "name"], limit=limit)
    return json_response({"data": records})
```

Use `error_response(...)` for error payloads and `parse_json_arg(...)` for JSON
string arguments; validate parsed shapes before passing them to Odoo. Prefer
extending a suitable existing tool when its call and response serve the same use.

**Token efficiency:** new listing tools should accept
`response_format: str | None = None` and use `resolve_full(...)` to decide
between a compact summary (default) and full detail, plus `limit`/`offset` and
`total`/`returned` counters. Use `compact_text(...)` for truncation (never
silently cut), `compact_records(...)` for record lists, and respect the global
`max_response_chars` budget automatically via `json_response(...)` (pass
`bypass_budget=True` only for tools where full fidelity is the point, e.g.
`execute_method`).

2. **Register the tool** in `src/odoo_boost/mcp_server/registry.py`:

```python
from odoo_boost.mcp_server.tools.my_tool import my_tool

# Add to LIVE_TOOLS when it needs the Odoo connection, otherwise LOCAL_TOOLS.
LIVE_TOOLS = (..., my_tool)
```

`server.py` iterates the registry automatically; live tools are wrapped so
connection failures become clear `ToolError` messages.
All 23 tools are registered. Choose `LOCAL_TOOLS` for bundled documentation or filesystem
tools that do not need a running Odoo connection.

3. **Add unit tests** in `tests/test_tools.py`. The suite asserts the total tool
count in `tests/test_registry.py`, so update it deliberately when adding tools.

## Adding an Odoo Version

Follow the [version support and onboarding guide](docs/versions.md). Register
only changed compatibility facts and documentation paths in `versions.py`, add
the version note, then test isolation from earlier releases and unknown newer
series. Keep shared guidance in core topics.

## Adding a New MCP Resource or Prompt

Odoo Boost runs natively on **MCP v2 (`mcp.server.MCPServer`)**.

### Adding a Resource
In `src/odoo_boost/mcp_server/server.py`:

```python
@mcp.resource("odoo://custom/{param}")
def custom_resource(param: str) -> str:
    """Dynamic resource description."""
    return f"Data for {param}"
```

### Adding a Prompt
In `src/odoo_boost/mcp_server/server.py`:

```python
@mcp.prompt("custom_workflow")
def custom_prompt(arg: str) -> str:
    """Pre-built prompt workflow."""
    return f"Execute custom workflow on {arg}..."
```

## Adding a New Agent

1. **Add an `AgentSpec`** in `src/odoo_boost/agents/spec.py` describing the
   paths, skills directory, and MCP output format (`mcpServers`, `vscode`,
   `opencode`, `codex`, or `hermes`).
2. **Create a thin wrapper** at `src/odoo_boost/agents/my_agent.py`:

```python
from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS

class MyAgentAgent(Agent):
    spec = AGENT_SPECS["my_agent"]
```

   `id` and `display_name` are derived from the spec automatically.
3. **Register in `src/odoo_boost/agents/__init__.py`**.
4. **Add unit tests** in `tests/test_agents.py` (the parametrized contract suite
   covers new agents automatically once registered).

## Logging

Use `logging.getLogger(__name__)` in modules. Call `configure_logging()` at
entry points, and respect `--log-level` / `ODOO_BOOST_LOG_LEVEL`. Logs must go
to stderr: stdout carries the stdio MCP protocol stream. Prefer `logger.debug`
for expected/optional failures (e.g. an uninstalled optional Odoo module) and
`logger.warning` for genuine problems.

## Running Tests and Linting

```bash
# Run full pytest suite with branch coverage (fails under 70%)
pytest --cov --cov-report=term-missing

# Lint and format
ruff check src tests
ruff format --check src tests

# Type check (strict)
mypy src/odoo_boost/

# Run everything the way CI does
pre-commit run --all-files
```

CI runs the test suite on Python 3.10, 3.11, 3.12, and 3.13, plus a build job
that installs the wheel and verifies bundled skills/guidelines package data.

## Release Process

Releases use PyPI Trusted Publishing (OIDC) — no API tokens are stored.

1. Move the relevant `CHANGELOG.md` entries from `[Unreleased]` under a new
   version heading and add fresh compare links.
2. Bump `__version__` in `src/odoo_boost/__version__.py`.
3. Merge to `main`. The `Auto Tag` workflow creates and pushes `vX.Y.Z`.
4. The `Release` workflow then:
   - runs CI,
   - verifies the tag matches `__version__`,
   - builds the sdist/wheel and smoke-tests the installed wheel,
   - publishes to PyPI via Trusted Publishing (with attestations) **only when
     the repository variable `PUBLISH_TO_PYPI` is `true`**,
   - creates a GitHub Release with generated notes.

PyPI publishing is gated so version bumps are safe before the publisher is
configured. To enable it:

1. Configure a [PyPI trusted publisher](https://docs.pypi.org/trusted-publishers/)
   for the repository, workflow `release.yml`, and environment `pypi`.
2. Set the repository variable `PUBLISH_TO_PYPI` to `true`
   (Settings → Secrets and variables → Actions → Variables).
