# Guidelines

Odoo Boost bundles comprehensive Odoo development guidelines injected into your AI agent's native context. This ensures that generated code is idiomatic, clean, secure, and compliant with OCA (Odoo Community Association) standards.

## What's Included

Guidelines are composed from 11 core files plus a version-specific addendum:

### Core Guidelines (11 Topics)

| File | Topic | Covers |
|---|---|---|
| `operating_rules.md` | Operating Rules & Boundaries | Workflow modes (Direct vs Plan), command boundaries, scope restraint |
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
| `v17.md` | Odoo 17 | `<list>` tag introduced, `attrs` deprecated, `Command` API, new dark/light UI |
| `v18.md` | Odoo 18 | Mandatory `<list>` tag, inline view expressions, portal revamp |
| `v19.md` | Odoo 19 | `<tree>` strictly removed, Python 3.12+ required, search view cleanups |

## How Version Selection Works

During `odoo-boost install`, Odoo Boost detects your server version and writes it to `odoo-boost.json`:

```json
{
  "odoo_version": "18.0"
}
```

When building agent guidelines, the composer:
1. Concatenates all 11 core guideline files (including OCA standards).
2. Appends the version-specific file (e.g. `v18.md` for Odoo 18).
3. Writes the document directly into the target agent's guidelines file.

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
