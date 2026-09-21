---
name: odoo-core-contribution
description: Apply official Odoo house rules when changing or reviewing the upstream community or enterprise source trees; do not use stable-branch restrictions as generic custom-addon policy.
globs: ["odoo/**/*.py", "addons/**/*", "odoo/addons/**/*"]
---

# Contributing to Odoo core

Use this skill only when the target is the official Odoo community or enterprise
source tree. For OCA or customer addons, use the normal Odoo Boost guidelines and
the project's own conventions instead.

1. Pin the exact target and base revisions. Read the changed modules' manifests,
   commit message, and change request. If the same branch exists in the sibling
   community or enterprise repository, inspect both halves together.
2. Route each changed file to only the relevant material in `references/`.
   Backend addon files use `backend.md`; `static/src` and `static/tests` use
   `web.md`; sensitive constructs use `security.md`.
3. Review twice: first against applicable house rules, then against behavior.
   For the second pass, test boundary values, empty and multi-record sets,
   rounding, time zones, concurrency, repeated execution, scale, and whether
   tests fail without the change.
4. Search all available addon paths for overrides and consumers of changed
   methods, fields, XML IDs, templates, context keys, exports, and JavaScript
   patches. Confirm signatures and shared data contracts remain compatible.
5. On a stable branch, keep the fix minimal and preserve surrounding style,
   public method signatures, stored schema, XML IDs, and translated source
   strings. Do not mix cleanup or cosmetic work into the fix.
6. Report findings with severity, exact file and line, a concrete failure
   scenario, the smallest fix, and whether the basis is an official rule or
   reviewer judgement. State which references were read.

Official guidance is a strong source for Odoo's repository, but the checked-out
code remains authoritative for APIs and branch behavior. Verify remembered facts
with `git grep` in that revision, especially around ORM, views, templates, and
controllers.

Source: Odoo 20.0 `skills/`, reviewed at revision
`b0329e93ae894cd90cc3136bc694ed22507b96b8` (LGPL-3.0).
