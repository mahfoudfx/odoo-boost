# Contributing to Odoo Boost

## Development Setup

```bash
git clone https://github.com/havmedia/odoo-boost.git
cd odoo-boost

# Create virtual environment with Python 3.12+
uv venv --python 3.12
source .venv/bin/activate

# Install with development and linting extras
uv pip install -e ".[lint]"

# Verify
odoo-boost --version
```

## Project Layout

```
src/odoo_boost/
├── ast_scanner/            # Fast, pure-Python AST & XML analyzer (Docker-Free)
├── cli/                    # Typer CLI commands (install, check, lint, update, mcp)
├── config/                 # Pydantic schema + load/save helpers
├── connection/             # Abstract base + XML-RPC client
├── mcp_server/
│   ├── server.py           # Dual-compatible MCP Server (mcp 2.x & 1.x)
│   ├── context.py          # Singleton holding connection + config
│   └── tools/              # 22 MCP tools (one file per tool)
├── agents/                 # 11 agent adapters + base class
├── guidelines/
│   ├── composer.py         # Assembles markdown into unified agent prompt
│   └── core/               # 10 core markdown topics + versions (v14-v19)
└── skills/                 # 20 skills (Core, Workflows, Domain Patterns) + routing
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

import json
from odoo_boost.mcp_server.context import get_connection

def my_tool(param1: str, limit: int = 10) -> str:
    """One-line description shown to the AI agent.

    Args:
        param1: Description of param1.
        limit: Max records.
    """
    conn = get_connection()
    records = conn.search_read("ir.model", [], fields=["model", "name"], limit=limit)
    return json.dumps({"data": records}, indent=2, default=str)
```

2. **Register the tool** in `src/odoo_boost/mcp_server/server.py`:

```python
from odoo_boost.mcp_server.tools.my_tool import my_tool

# Inside create_mcp_server():
mcp.tool()(my_tool)
```

3. **Add unit tests** in `tests/test_tools.py`.

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

1. **Create the agent file** at `src/odoo_boost/agents/my_agent.py`:
   - Inherit from `Agent` in `odoo_boost.agents.base`.
   - Define `id`, `display_name`, `guidelines_path`, `mcp_config_path`, `skills_dir`, and `_mcp_config_content()`.
2. **Register in `src/odoo_boost/agents/__init__.py`**.
3. **Add unit tests** in `tests/test_agents.py`.

## Running Tests and Linting

```bash
# Run full pytest suite
pytest tests/ -v

# Run ruff code checks
ruff check src tests
```
