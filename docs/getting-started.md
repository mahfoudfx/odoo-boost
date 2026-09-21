# Getting Started

This guide walks you through installing Odoo Boost, configuring your AI agents, and using the MCP tools.

## Prerequisites

- **Python 3.10+** (Python 3.12+ recommended)
- **An Odoo instance** (v14 through v20) accessible over HTTP/HTTPS, or local Odoo addons for offline AST scanning
- **User credentials or API key** for your Odoo database

---

## Step 1: Install Odoo Boost

```bash
pip install odoo-boost
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install odoo-boost
```

For optional features:

```bash
# Optional OCA code linting (pylint-odoo)
pip install "odoo-boost[lint]"

# Optional RelaxNG XML view validation (lxml)
pip install "odoo-boost[xml]"

# All optional packages
pip install "odoo-boost[all]"
```

Verify your installation:

```bash
odoo-boost --version
```

---

## Step 2: Run the Install Wizard

Navigate to your Odoo project repository and run:

```bash
cd /path/to/your/odoo-project
odoo-boost install
```

The wizard will:
1. **Prompt for Odoo connection details**: URL, database name, user, and password/API key.
2. **Test the connection**: Verify authentication, detect Odoo version (e.g. 14.0, 17.0, 18.0, 19.0, 20.0), and check for `odoo-ls`.
3. **Select AI agents**: Choose from 12 modern assistants:
   - Antigravity (App & CLI `agy`)
   - Claude Code
   - Cursor
   - GitHub Copilot
   - OpenAI Codex
   - OpenCode
   - Pi
   - Hermes
   - Windsurf
   - Cline
   - Junie
   - Zed
4. **Choose the MCP transport**: stdio (default) or HTTP, and whether the same
   project is opened from Windows IDEs while the server runs in WSL.
5. **Generate files**: Creates guidelines, MCP configs, 23 skills, and the `SKILLS_ROUTING.md` index.

Generated instructions choose an execution depth automatically. Small iterative
edits use fast mode with the configured Odoo version rules and a 2–4 call target.
Complex modules, cross-model behavior, security, migrations, and audits switch to
deep mode and load relevant expert topics and skills progressively. No prompt
prefix or mode keyword is required.

---

## Step 3: Verify the Connection and Local Tools

Test the live connection anytime:

```bash
odoo-boost check
```

Verify that the generated MCP server actually starts (spawns the configured
command and performs the MCP `initialize` handshake):

```bash
odoo-boost check --mcp
```

If you develop inside WSL but use a Windows-native IDE and the MCP server does
not appear, regenerate a Windows-ready config (wraps the interpreter in
`wsl.exe`):

```bash
odoo-boost mcp-config --platform windows
```

Alternatively, run the server over HTTP and point the IDE at
`http://localhost:8765/mcp`:

```bash
# Non-loopback binds require a bearer token
odoo-boost mcp --transport http --host 0.0.0.0 --port 8765 --token "$MCP_TOKEN"
```

Keep that process running, store the same token as `mcp_token` in
`odoo-boost.json`, then generate the remote configuration:

```bash
odoo-boost mcp-config --platform http --agents antigravity
odoo-boost check --mcp
```

Antigravity uses `serverUrl` for remote MCP servers. Odoo Boost writes this
current schema automatically to `.agents/mcp_config.json`.

Run static linting on your local addon code:

```bash
odoo-boost lint ./my_custom_addon
```

---

## Step 4: Start Coding with AI Agents

Open your project in your preferred editor or agent:

- **Antigravity (App & CLI `agy`)**: Auto-detects `AGENTS.md` and `.agents/mcp_config.json`.
- **Claude Code**: Run `claude` in your project root; `.mcp.json` and `CLAUDE.md` are auto-loaded.
- **Cursor**: Open the workspace in Cursor; `.cursor/rules/odoo-boost.mdc` and `.cursor/mcp.json` are active.
- **Windsurf / Cline / OpenCode / Copilot / Codex / Pi / Hermes / Junie / Zed**: Native configurations are in place.

Ask your assistant:
- *"Inspect my local addon in ./addons/my_sale with inspect_local_addon"*
- *"What is the schema of the account.move model?"*
- *"Use aggregate_records to compute total monthly sales for Deco Addict"*
- *"Run lint_odoo_code on my models to check for OCA compliance"*
