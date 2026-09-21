# Odoo Boost

[![CI](https://github.com/mahfoudfx/odoo-boost/actions/workflows/ci.yml/badge.svg)](https://github.com/mahfoudfx/odoo-boost/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/odoo-boost)](https://pypi.org/project/odoo-boost/)
[![Python versions](https://img.shields.io/pypi/pyversions/odoo-boost)](https://pypi.org/project/odoo-boost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AI coding agents with deep runtime introspection and static analysis for Odoo instances and addons.

Inspired by [Laravel Boost](https://github.com/laravel/boost), Odoo Boost equips your AI coding assistants with deep knowledge of your Odoo project — live models, views, records, access rights, configuration, and offline AST/XML scanning — plus Odoo-specific development guidelines, OCA standards, and step-by-step skills.

## Highlights

- **23 MCP Tools, Resources & Prompts** — All tools are available by default; opt into an 8-tool profile with `lean_tools=true`. Includes live introspection, local AST scanning, dynamic resources (`odoo://schema/{model}`), and prompts (`review_odoo_addon`, `upgrade_odoo_addon`).
- **12 Modern AI Agents** — Antigravity (App & CLI `agy`), Claude Code, Cursor, GitHub Copilot, OpenAI Codex, OpenCode, Pi, Hermes, Windsurf, Cline, Junie, Zed.
- **Local Inspection Without Docker** — AST and XML scanning works on local addons; optional lint and language-server checks use installed tools.
- **23 Skills + Progressive Routing** — Core tasks, spec-driven development, code reviews, upgrade migrations, git commits, and specialized domain patterns (Accounting, Stock, Multi-Company, Chatter, Wizards, Crons, Computed Fields, Inheritance).
- **OCA Standards & Version-Aware** — Comprehensive guidelines supporting Odoo 14, 15, 16, 17, 18, 19, and 20.
- **Odoo-Aware Diagnostics by Default** — The setup wizard installs
  `OCA/pylint-odoo` and the official `odoo/odoo-ls` binary by default, with a
  lightweight opt-out and graceful fallbacks.

Install the official Odoo Language Server independently when needed:

```bash
odoo-boost odoo-ls install
odoo-boost odoo-ls status
```
- **Zero Config on Odoo Side** — Connects via standard XML-RPC; no custom module installation required on your Odoo server.
- **Progressive Context** — Compact responses, cached local scans, repeated-call loop protection, and explicit investigation budgets lead to detailed skills only on demand. Use `response_format="full"` when needed, or `lean_tools=true` to reduce the advertised tool set.
- **Automatic Fast/Deep Modes** — Small field, label, translation, and view edits keep the target-version contract but normally use only 2–4 tool calls. New modules, coupled workflows, security, migrations, and audits progressively load the full expert references.

## Installation

```bash
pip install odoo-boost
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install odoo-boost
```

To include optional features:

```bash
# Optional OCA code linter (pylint-odoo)
pip install "odoo-boost[lint]"

# Optional RelaxNG XML schema validation (lxml)
pip install "odoo-boost[xml]"

# All optional dependencies
pip install "odoo-boost[all]"
```

You can also install it as a global CLI tool:

```bash
uv tool install odoo-boost
```

## Quick Start

### 1. Run the install wizard

```bash
cd /path/to/your/odoo-project
odoo-boost install
```

The wizard will:
- Collect your Odoo connection details (URL, database, username, password/API key)
- Test the connection and detect the Odoo version (registered series 14.0–20.0; [version support](docs/versions.md))
- Install the official Odoo LS and OCA `pylint-odoo` checker by default for
  richer diagnostics; answer **No** at the prompt or use
  `odoo-boost install --skip-dev-tools` for a lightweight setup
- Let you select which AI agents to configure (from 12 supported agents)
- Generate guidelines, MCP server configs, skills catalog, and `SKILLS_ROUTING.md`

### 2. Verify the connection

```bash
odoo-boost check
```

Or test with explicit credentials:

```bash
odoo-boost check --url http://localhost:8069 --database mydb --username admin --password admin
```

### 3. Run static code checks (Docker-Free)

```bash
# Lint current directory or specific addon path
odoo-boost lint ./addons/my_custom_addon
```

### 4. Start coding

Your AI assistant is now configured. Odoo Boost selects the appropriate depth
from the request; no mode keyword or special prompt syntax is required.

For small iterative changes, it uses **fast mode** with the active Odoo version
rules and minimal context/tool calls. Example prompts:

- "Rename the `Reference` label to `Order Reference`."
- "Move `partner_id` before `date_order` in the form view."
- "Add `customer_code` to the list view."
- "Translate this label into French."
- "Make this field readonly when the order is confirmed."

For coupled or higher-risk work, it uses **deep mode** and progressively loads
the relevant expert guidelines, skills, source context, and MCP tools. Example
prompts:

- "Create a complete rental management module."
- "Implement multi-company approval for purchase orders."
- "Migrate this module from Odoo 16 to Odoo 20."
- "Audit this addon for security and performance."
- "Trace and fix this stock valuation inconsistency."

You can also ask direct inspection questions:

> "What models are available in this Odoo instance?"  
> "Run inspect_local_addon on ./my_addon to see what models and XML views it declares"  
> "Check whether my computed field implementation follows OCA standards"  
> "Aggregate total invoice amounts by partner for the last quarter using aggregate_records"  

## Commands

| Command | Description |
|---|---|
| `odoo-boost install` | Interactive setup wizard with agent configuration |
| `odoo-boost check [--mcp]` | Test connection to Odoo instance (and the MCP server handshake) |
| `odoo-boost lint [path]` | Run OCA/pylint-odoo or AST static checks on local addons |
| `odoo-boost update` | Re-sync guidelines, configs, and skills (cleans up removed agents) |
| `odoo-boost uninstall` | Remove generated agent files and optionally purge config |
| `odoo-boost mcp [--transport stdio\|http] [--token …]` | Start the MCP server (stdio by default, HTTP optional with bearer auth) |
| `odoo-boost mcp-config [--platform …]` | Regenerate only MCP configs (native/windows/http) |
| `odoo-boost --version` | Show installed version |

You can also run any command via `python -m odoo_boost`, e.g. `python -m odoo_boost lint .`.

## How It Works

```
┌─────────────────────────┐     stdio      ┌─────────────────────────────────┐    XML-RPC     ┌────────────────┐
│        AI Agent         │◄──────────────►│        Odoo Boost MCP           │◄─────────────►│  Odoo Server   │
│ (Antigravity, Claude,   │                │   (Runtime + AST Scanner)       │               │ (v14 - v20)    │
│  Cursor, OpenCode, ...) │                └────────────────┬────────────────┘               └────────────────┘
└───────────┬─────────────┘                                 │
            │                                               ▼
            ▼                                  ┌───────────────────────────┐
     Guidelines, OCA,                          │     23 MCP Tools          │
  23 Skills + Routing Map                      │ - Live ORM & DB schema    │
  (Local Markdown Files)                       │ - read_group aggregation  │
                                               │ - Sub-50ms local AST scan │
                                               │ - XML ID resolution       │
                                               │ - pylint-odoo & odoo-ls   │
                                               └───────────────────────────┘
```

Odoo Boost sits between your AI agent and your Odoo instance / codebase:
1. **23 MCP Tools** — Real-time database queries (including count-only), schema inspection, local AST parsing, and validation.
2. **OCA Guidelines** — Version-specific guidelines (v14-v20) and OCA architectural rules.
3. **23 Progressive Skills** — Focused task and domain guidance indexed in `SKILLS_ROUTING.md` for on-demand loading.

The recommended agent workflow is to understand the business requirement, inspect
local code and configuration, load the relevant version note or skill, and call
live MCP tools only for runtime facts. Start with small filtered results and
expand when needed. Unknown Odoo versions require source or runtime verification
for version-specific behavior; see [version support](docs/versions.md).

### Robust MCP Server Resolution

Generated MCP configs embed the **absolute path to your Python interpreter** rather than relying on a bare `odoo-boost` command on `$PATH`:

```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

This guarantees that:
- The MCP server always executes within the correct virtual environment
- No dependency on environment variable activation or shell state
- Seamless execution inside VS Code, Cursor, Antigravity, OpenCode, or CLI agents

### Cross-OS: WSL server + Windows IDE

When your project lives in WSL but the IDE runs natively on Windows, the
generated configs handle it two ways:

- **stdio with `mcp_target: "auto"`** — the native config is written for
  WSL-native IDEs, plus a `*.windows.*` companion that wraps the interpreter in
  `wsl.exe` (`command: "wsl.exe"`) for Windows IDEs.
- **HTTP transport** — `odoo-boost mcp --transport http` serves a single
  Streamable HTTP endpoint (default `http://127.0.0.1:8765/mcp`) that Windows
  IDEs reach through WSL2 `localhost` forwarding, no process spawning required.
  Non-loopback binds require `--token` / `mcp_token`; generated configs embed
  the `Authorization: Bearer` header. Antigravity receives its required
  `serverUrl` schema; set `mcp_http_url` only when Windows cannot use WSL
  localhost forwarding.

Security guardrails: `odoo-boost.json` is written `0600`, `readonly` blocks
mutating `execute_method` calls, and `allowed_roots` confines the local file
tools. See [Configuration](docs/configuration.md#security-notes).

Regenerate for a specific platform at any time:

```bash
odoo-boost mcp-config --platform windows   # wsl.exe wrapper
odoo-boost mcp-config --platform http      # URL-based configs
odoo-boost check --mcp                     # verify the server starts
```

## .gitignore

Generated files contain environment-specific paths and local configs. Add the following to your project `.gitignore`:

```gitignore
# Odoo Boost
odoo-boost.json
CLAUDE.md
AGENTS.md
.windsurfrules
.clinerules
.mcp.json
opencode.json
.ai/skills/
.agents/
.cursor/rules/odoo-boost.mdc
.cursor/mcp.json
.cursor/skills/
.vscode/mcp.json
.github/copilot-instructions.md
.github/skills/
.codex/
.pi/
.hermes/
.windsurf/
.cline/
.junie/
.zed/settings.json

# Windows/WSL companion MCP configs (mcp_target: "auto")
*.windows.json
*.windows.yaml
*.windows.toml
```

> **Note:** Directories like `.github/` and `.vscode/` may contain existing project files — ignore only the generated sub-files/directories.

## Supported Agents

| Agent | Guidelines | MCP Config | Skills Directory |
|---|---|---|---|
| **Antigravity (App & CLI `agy`)** | `AGENTS.md` | `.agents/mcp_config.json` | `.agents/skills/` |
| **Claude Code** | `CLAUDE.md` | `.mcp.json` | `.ai/skills/` |
| **Cursor** | `.cursor/rules/odoo-boost.mdc` | `.cursor/mcp.json` | `.cursor/skills/` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.vscode/mcp.json` | `.github/skills/` |
| **OpenAI Codex** | `AGENTS.md` | `.codex/config.toml` | `.agents/skills/` |
| **OpenCode** | `AGENTS.md` | `opencode.json` | `.agents/skills/` |
| **Pi** | `AGENTS.md` | `.pi/mcp.json` | `.agents/skills/` |
| **Hermes** | `AGENTS.md` | `.hermes/config.yaml` | `.agents/skills/` |
| **Windsurf** | `.windsurfrules` | `.windsurf/mcp.json` | `.windsurf/skills/` |
| **Cline** | `.clinerules` | `.cline/mcp_settings.json` | `.cline/skills/` |
| **Junie** | `.junie/guidelines.md` | `.junie/mcp/mcp.json` | `.junie/skills/` |
| **Zed** | `AGENTS.md` | `.zed/settings.json` | `.agents/skills/` |

## Documentation

- [Getting Started](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/getting-started.md) — Full setup walkthrough
- [MCP Tools Reference](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/mcp-tools.md) — Complete guide to all 23 tools with examples
- [Agent Configuration](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/agents.md) — Configuration guide for all 12 supported agents
- [Skills Catalog](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/skills.md) — 23 progressive skills and routing table
- [Guidelines](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/guidelines.md) — Bundled guidelines (v14-v20 and OCA rules)
- [Configuration Reference](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/configuration.md) — `odoo-boost.json` schema and options
- [Architecture](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/architecture.md) — Components, tool-call lifecycle, and extension points
- [Troubleshooting](https://github.com/mahfoudfx/odoo-boost/blob/main/docs/troubleshooting.md) — WSL/Windows, HTTP auth, connection, and logging issues
- [Security Policy](https://github.com/mahfoudfx/odoo-boost/blob/main/SECURITY.md) — Vulnerability reporting and security model
- [Changelog](https://github.com/mahfoudfx/odoo-boost/blob/main/CHANGELOG.md) — Release history
- [Contributing](https://github.com/mahfoudfx/odoo-boost/blob/main/CONTRIBUTING.md) — Developer guide and tool authoring

## License

MIT — see [LICENSE](LICENSE).
