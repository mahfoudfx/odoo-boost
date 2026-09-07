---
name: Conventional Commits for Odoo
description: Standardized Odoo & OCA git commit formatting with proper semantic tags and issue references.
globs: ["*"]
---

# Odoo Conventional Git Commits

Follow the standard Odoo and OCA commit guidelines to keep git logs clear, searchable, and bisect-friendly.

## Commit Message Format

```
[TAG] module_name: short description in imperative mood (max 60 chars)

Optional longer description explaining:
- Why the change was needed (problem description)
- How the solution works
- Any architectural trade-offs or breaking changes

Fixes #123
Closes #456
```

## Standard Odoo Tags

| Tag | Purpose | Example |
|---|---|---|
| `[ADD]` | Addition of a new module, model, feature, or view | `[ADD] sale_commission: add partner commission tracking` |
| `[FIX]` | Bug fix for incorrect behavior or error | `[FIX] account: prevent zero division during tax calculation` |
| `[REF]` | Refactoring code without altering external behavior | `[REF] stock: simplify reservation query logic` |
| `[REM]` | Removal of deprecated files, fields, or dead code | `[REM] website: remove obsolete v16 asset bundles` |
| `[MOV]` | Moving files, views, or code blocks between packages | `[MOV] project: move task template wizard to views/` |
| `[IMP]` | Minor improvement or optimization of existing feature | `[IMP] purchase: improve purchase order list view responsiveness` |
| `[MIG]` | Version migration changes | `[MIG] pos_orders: migrate module to Odoo 18.0` |

## Golden Rules
- **One Concern Per Commit**: Do not mix `[FIX]` and `[REF]` in the same commit.
- **Imperative Mood**: Write "add partner view", not "added partner view" or "adds partner view".
- **Module Prefix**: Always include the impacted module name before the colon.
- **Reference Issues**: Always include issue or PR numbers if applicable.
