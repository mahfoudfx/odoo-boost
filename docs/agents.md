# Agent Configuration

Odoo Boost supports 11 modern AI coding agents. For each agent, Odoo Boost generates:

1. **Guidelines** — Odoo development best practices and version notes in the agent's native format
2. **MCP Config** — Machine-readable configuration connecting the agent to the Odoo Boost MCP server
3. **Skills & Progressive Routing** — Step-by-step guides along with `SKILLS_ROUTING.md`

## Supported Agents

### Antigravity (App & CLI `agy`)

| File | Path |
|---|---|
| Guidelines | `AGENTS.md` |
| MCP Config | `.agents/mcp_config.json` |
| Skills | `.agents/skills/` |

**MCP Config format (`.agents/mcp_config.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

Antigravity auto-discovers workspace customizations in `.agents/`, reading `mcp_config.json`, `AGENTS.md`, and skills in `.agents/skills/`.

---

### Claude Code

| File | Path |
|---|---|
| Guidelines | `CLAUDE.md` |
| MCP Config | `.mcp.json` |
| Skills | `.ai/skills/` |

**MCP Config format (`.mcp.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

Claude Code auto-detects `CLAUDE.md` and `.mcp.json` in your project root upon launch.

---

### Cursor

| File | Path |
|---|---|
| Guidelines | `.cursor/rules/odoo-boost.mdc` |
| MCP Config | `.cursor/mcp.json` |
| Skills | `.cursor/skills/` |

**Guidelines format:** Cursor uses `.mdc` rules with YAML frontmatter:
```markdown
---
description: Odoo development guidelines from Odoo Boost
globs:
alwaysApply: true
---

# Odoo Development Guidelines
...
```

**MCP Config format (`.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

---

### GitHub Copilot

| File | Path |
|---|---|
| Guidelines | `.github/copilot-instructions.md` |
| MCP Config | `.vscode/mcp.json` |
| Skills | `.github/skills/` |

**MCP Config format (`.vscode/mcp.json`):**
```json
{
  "servers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

---

### OpenAI Codex

| File | Path |
|---|---|
| Guidelines | `AGENTS.md` |
| MCP Config | `.codex/config.toml` |
| Skills | `.agents/skills/` |

**MCP Config format (`.codex/config.toml`):**
```toml
# Odoo Boost MCP configuration for Codex
[mcp_servers.odoo-boost]
command = "/path/to/python"
args = ["-m", "odoo_boost", "mcp"]
```

---

### OpenCode

| File | Path |
|---|---|
| Guidelines | `AGENTS.md` |
| MCP Config | `opencode.json` |
| Skills | `.agents/skills/` |

**MCP Config format (`opencode.json`):**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "odoo-boost": {
        "command": "/path/to/python",
        "args": ["-m", "odoo_boost", "mcp"]
      }
    }
  }
}
```

---

### Pi

| File | Path |
|---|---|
| Guidelines | `AGENTS.md` |
| MCP Config | `.pi/mcp.json` |
| Skills | `.agents/skills/` |

**MCP Config format (`.pi/mcp.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

---

### Hermes

| File | Path |
|---|---|
| Guidelines | `AGENTS.md` |
| MCP Config | `.hermes/config.yaml` |
| Skills | `.agents/skills/` |

**MCP Config format (`.hermes/config.yaml`):**
```yaml
mcp_servers:
  odoo-boost:
    command: "/path/to/python"
    args:
      - "-m"
      - "odoo_boost"
      - "mcp"
```

---

### Windsurf

| File | Path |
|---|---|
| Guidelines | `.windsurfrules` |
| MCP Config | `.windsurf/mcp.json` |
| Skills | `.windsurf/skills/` |

**MCP Config format (`.windsurf/mcp.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

---

### Cline

| File | Path |
|---|---|
| Guidelines | `.clinerules` |
| MCP Config | `.cline/mcp_settings.json` |
| Skills | `.cline/skills/` |

**MCP Config format (`.cline/mcp_settings.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

### Junie

| File | Path |
|---|---|
| Guidelines | `.junie/guidelines.md` |
| MCP Config | `.junie/mcp/mcp.json` |
| Skills | `.junie/skills/` |

**MCP Config format (`.junie/mcp/mcp.json`):**
```json
{
  "mcpServers": {
    "odoo-boost": {
      "command": "/path/to/python",
      "args": ["-m", "odoo_boost", "mcp"]
    }
  }
}
```

---

## Selecting Agents

### During Install Wizard
The interactive wizard prompts:
```
Step 3: Select AI agents to configure

  1. Antigravity (App & CLI agy) (antigravity)
  2. Claude Code (claude_code)
  3. Cursor (cursor)
  4. GitHub Copilot (copilot)
  5. OpenAI Codex (codex)
  6. OpenCode (opencode)
  7. Pi (pi)
  8. Hermes (hermes)
  9. Windsurf (windsurf)
  10. Cline (cline)
  11. Junie (junie)

  Enter agent numbers (comma-separated) or 'all' [all]:
```

### In `odoo-boost.json`
You can configure agents explicitly in `odoo-boost.json`:
```json
{
  "agents": ["antigravity", "claude_code", "cursor", "windsurf", "cline"]
}
```

Valid identifiers:
`antigravity`, `claude_code`, `cursor`, `copilot`, `codex`, `opencode`, `pi`, `hermes`, `windsurf`, `cline`, `junie`.

Run `odoo-boost update` to apply changes.
