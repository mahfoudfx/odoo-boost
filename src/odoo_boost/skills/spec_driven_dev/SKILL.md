---
name: spec-driven-dev
description: End-to-end workflow to take a feature specification and produce a production-ready Odoo module.
globs: ["__manifest__.py", "models/**/*.py", "views/**/*.xml", "security/*"]
---

# Spec-Driven Odoo Module Development

Follow this structured phase-by-phase workflow to implement any business requirement cleanly into an idiomatic Odoo module.

## Phase 1: Architecture & Data Modeling
1. **Identify Existing Models**:
   - Check if you should extend existing models (`sale.order`, `res.partner`) via `_inherit` or create new entities with `_name`.
   - Minimize custom models when standard fields/mixins suffice.
2. **Define Field Types & Constraints**:
   - Choose appropriate types (`Char`, `Text`, `Monetary`, `Selection`, `Many2one`, `One2many`, `Many2many`).
   - Identify which fields require `index=True` (foreign keys, search criteria).
   - Identify compute vs stored logic and their `@api.depends`.

## Phase 2: Scaffolding Order (Strict Dependency Flow)
Always build files in dependency order so tests and installations succeed without missing reference errors:
1. `__manifest__.py`:
   - Declare name, summary, category, version, license, and direct `depends`.
2. `security/ir.model.access.csv`:
   - Declare group permissions before referencing models in views or tests.
3. `models/`:
   - Implement data models and logic; register in `models/__init__.py`.
4. `views/`:
   - 1. Actions (`ir.actions.act_window`)
   - 2. Form views
   - 3. List views (`<list>` in v18+)
   - 4. Search views (filters and group bys)
   - 5. Menus (`<menuitem>` referencing actions)
5. `data/`:
   - Sequences, default categories, scheduled actions (`ir.cron`).
6. `tests/`:
   - Unit tests extending `odoo.tests.common.TransactionCase`.

## Phase 3: Validation & Quality Gates
1. Run AST analysis or `lint_odoo_code` to ensure OCA compliance.
2. Verify all XML IDs resolve properly without dangling references.
3. Verify test coverage for both positive flows and edge-case exceptions (`ValidationError`, `AccessError`).
