# Guidelines

Odoo Boost bundles complete expert guidelines while keeping routine agent context
small. Generated agent files contain an adaptive fast/deep router and the effective
target-version contract. Full topic references and version notes are installed beside
the skills and loaded only when relevant. The MCP resource `odoo://guidelines/oca`
provides the complete combined document for broad audits.

## What's Included

Guidelines are composed from 11 core files plus a version-specific addendum:

### Core Guidelines (11 Topics)

| File | Topic | Covers |
|---|---|---|
| `operating_rules.md` | Operating Rules & Boundaries | Workflow modes (Direct vs Plan), strict prohibition on live execution, scope restraint |
| `odoo_general.md` | General Principles | Architecture, module lifecycle, dependencies |
| `module_structure.md` | Module Structure | Directory layout, `__manifest__.py`, file naming |
| `orm_best_practices.md` | ORM Best Practices | Models, fields, CRUD, domains, performance, batched queries |
| `security.md` | Security | ACLs (`ir.model.access`), record rules (`ir.rule`), groups, `sudo()` audits |
| `views_and_ui.md` | Views & UI | Form, list, kanban, search views, XPath inheritance, actions |
| `controllers.md` | Controllers | HTTP routes, JSON-RPC endpoints, authentication |
| `javascript_owl.md` | JavaScript & OWL | OWL components, templates, hooks, services, assets |
| `testing.md` | Testing | Python `TransactionCase`, HTTP tests, tour tests |
| `coding_style.md` | Coding Style | Python conventions, XML formatting, git commits |
| `oca_standards.md` | OCA Standards | Community quality guidelines, SQL safety, transaction handling |

### Version-Specific Addenda

| File | Version | Key Highlights |
|---|---|---|
| `v14.md` | Odoo 14 | Legacy `attrs`, Classic `web.assets_backend`, `[(0, 0, vals)]` tuples |
| `v15.md` | Odoo 15 | Asset bundles in manifest `assets` dict, OWL 1 introduction |
| `v16.md` | Odoo 16 | Transition to OWL 2, performance improvements |
| `v17.md` | Odoo 17 | Inline view modifiers and `_compute_display_name` replace older patterns |
| `v18.md` | Odoo 18 | `<list>` replaces `<tree>` as the list view root |
| `v19.md` | Odoo 19 | `jsonrpc` controller routes and search view differences |
| `v20.md` | Odoo 20 | Runtime baseline, `fields.Domain`, bearer scopes, and security APIs |

The [version support guide](versions.md) describes the effective version facts and how to add a release. The registry in `versions.py` is authoritative for compatibility facts; each version note provides targeted detail.

## How Version Selection Works

During `odoo-boost install`, Odoo Boost detects your server version and writes it to `odoo-boost.json`:

```json
{
  "odoo_version": "18.0"
}
```

When building agent guidelines, the composer:
1. Writes a compact automatic effort router plus effective compatibility rules.
2. Uses first-pass coding for small view, field, label, and translation edits, normally
   within two to four tool calls.
3. Uses medium effort for bounded cross-model features, localized refactoring,
   and packaging; high effort covers production readiness, security, migrations,
   audits, and failed lower-effort attempts.
4. Installs all 11 expert topics and the matching version note under the agent's
   `guidelines/` directory for selective loading. Unknown series keep an explicit
   uncertainty notice.
5. Keeps the complete combined document available through the MCP resource and
   `compose_guidelines()` API.

## Where Guidelines Are Written

| Agent | File | Format |
|---|---|---|
| Antigravity (App & CLI) | `AGENTS.md` | Markdown |
| Claude Code | `CLAUDE.md` | Markdown |
| Cursor | `.cursor/rules/odoo-boost.mdc` | Markdown with YAML frontmatter |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown |
| OpenAI Codex | `AGENTS.md` | Markdown |
| OpenCode | `AGENTS.md` | Markdown |
| Pi | `AGENTS.md` | Markdown |
| Hermes | `AGENTS.md` | Markdown |
| Windsurf | `.windsurfrules` | Markdown |
| Cline | `.clinerules` | Markdown |
| Junie | `.junie/guidelines.md` | Markdown |
| Zed | `AGENTS.md` | Markdown |

## Refreshing Guidelines

To refresh or re-generate guidelines after updating Odoo Boost:

```bash
odoo-boost update
```

## Programmatic Access

```python
from odoo_boost.guidelines import compose_guidelines

# All core guidelines + OCA standards + v19 notes
content = compose_guidelines("19.0")

# Core guidelines only
core_only = compose_guidelines()
```
