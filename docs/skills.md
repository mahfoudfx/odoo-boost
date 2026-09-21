# Skills & Progressive Routing

Odoo Boost includes **23 specialized development skills** organized into three categories: **Core**, **Workflows**, and **Domain Patterns**.

To prevent context window bloat, Odoo Boost generates a compact **`SKILLS_ROUTING.md`** index file in each agent's skills directory. AI agents consult this routing index to progressively fetch only the skill files required for the task at hand.

---

## Skills Catalog

### 1. Core Development (9 Skills)
| Skill | Directory | Description |
|---|---|---|
| Creating Models | `creating_models/` | Create a new Odoo model with fields, constraints, and methods |
| XML Views | `xml_views/` | Create and customize form, list, kanban, and search views |
| Security Rules | `security_rules/` | Set up ACLs (`ir.model.access.csv`) and record rules (`ir.rule`) |
| OWL Components | `owl_components/` | Create custom OWL frontend components and templates |
| Controllers & Routes | `controllers_routes/` | Create HTTP controllers and JSON-RPC API endpoints |
| Report Development | `report_development/` | Create QWeb PDF reports and report actions |
| Automated Actions | `automated_actions/` | Create `base.automation` and server actions |
| Testing | `testing/` | Write Python and JavaScript tests for Odoo modules |
| Pattern Library | `pattern_library/` | Route to 52 detailed functional references without loading them globally |

### 2. Workflows & Engineering Standards (6 Skills)
| Skill | Directory | Description |
|---|---|---|
| Source Trace | `source_trace/` | Follow entry points, overrides, views, security, and side effects for complex changes |
| Code Review | `code_review/` | Comprehensive review checklist for OCA standards, SQL injection, and N+1 queries |
| Odoo Core Contribution | `odoo_core_contribution/` | Official Odoo house rules, stable-branch constraints, cross-repository review, and targeted backend/web/security references |
| Upgrade Analysis | `upgrade_analysis/` | Migration checklist; consult the [version support guide](versions.md) and target version note for actual differences |
| Spec-Driven Dev | `spec_driven_dev/` | End-to-end workflow to take a spec and produce a production-ready module in proper dependency order |
| Conventional Commits | `conventional_commit/` | Standardized Odoo & OCA commit formatting (`[ADD]`, `[FIX]`, `[REF]`, `[MIG]`, etc.) |

### 3. High-Impact Domain Patterns (8 Skills)
| Skill | Directory | Description |
|---|---|---|
| Accounting Domain | `domain_accounting/` | Double-entry invariants, `account.move`, `account.move.line`, invoices, and currency rounding |
| Stock & Inventory | `domain_stock/` | Transfers, pickings, stock moves, quant reservations, and valuation integrity |
| Multi-Company | `domain_multi_company/` | Multi-company models, company-dependent properties, and record rules |
| Mail & Chatter | `domain_mail_chatter/` | Inheriting `mail.thread` and `mail.activity.mixin`, field tracking, and chatter UI |
| Wizards & Transients | `domain_wizards/` | `models.TransientModel`, wizard form dialogs, and action button workflows |
| Crons & Automation | `domain_crons_automation/` | Batch-safe scheduled actions (`ir.cron`), error isolation, and cron definitions |
| Computed Fields | `domain_computed_fields/` | `@api.depends`, complete assignment rules, inverse methods, and search handlers |
| Model Inheritance | `domain_inheritance/` | Classical (`_inherit`), prototype, and delegation (`_inherits`) inheritance + XPath view extensions |

---

## Progressive Skill Routing (`SKILLS_ROUTING.md`)

When skills are installed, Odoo Boost writes a `SKILLS_ROUTING.md` table into the agent's skills directory.

For example, an agent working in `.agents/skills/` reads `SKILLS_ROUTING.md` to discover:
- What directory corresponds to an intent (e.g. "audit multi-company code" -> `code_review/SKILL.md` + `domain_multi_company/SKILL.md`)
- File trigger patterns (globs)
- Concise summaries

This allows LLM agents to maintain minimal prompt overhead while retaining immediate access to in-depth Odoo documentation.

The pattern library consolidates 52 focused references instead of exposing the
upstream projects' many overlapping files as top-level skills. Shared guidance,
version deltas, and routing remain authoritative; agents open a detailed pattern
only when a task needs it. The library incorporates selected patterns and
workflow ideas from Letzdoo, UncleCat, Vauxoo, and fhidalgodev with attribution
and license texts bundled beside the references.

---

## Where Skills Are Installed

| Agent | Skills Directory |
|---|---|
| Antigravity (App & CLI) | `.agents/skills/` |
| Claude Code | `.ai/skills/` |
| Cursor | `.cursor/skills/` |
| GitHub Copilot | `.github/skills/` |
| OpenAI Codex | `.agents/skills/` |
| OpenCode | `.agents/skills/` |
| Pi | `.agents/skills/` |
| Hermes | `.agents/skills/` |
| Windsurf | `.windsurf/skills/` |
| Cline | `.cline/skills/` |
| Junie | `.junie/skills/` |
| Zed | `.agents/skills/` |

---

## Programmatic Access

```python
from pathlib import Path
from odoo_boost.skills import (
    list_skills,
    load_skill,
    install_skills,
    generate_skills_routing,
)

# List all 23 skills
all_skills = list_skills()

# Filter by category: "core", "workflows", or "domain"
workflows = list_skills(category="workflows")

# Read a single skill's markdown
review_guide = load_skill("code_review")

# Install all skills and generate SKILLS_ROUTING.md
install_skills(Path("./custom_skills"))
```
