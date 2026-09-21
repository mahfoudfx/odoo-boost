---
name: source-trace
description: Trace a complex Odoo behavior through models, inherited views, actions, security, and tests before changing it.
globs: ["models/**/*.py", "views/**/*.xml", "security/*", "tests/**/*.py"]
---

# Trace an Odoo behavior

Use this skill when the change crosses several models, inherits an unfamiliar
workflow, or a first attempt failed. A small, clear edit does not need a formal
trace.

1. State the user-visible behavior and the Odoo version. Read the project's
   configuration and addon manifests. A short addon version such as `1.2`
   does not establish the Odoo major version; conflicting manifests do not
   establish one either. If still uncertain, inspect the target source before
   choosing version-specific APIs.
2. Find the entry point: button or action, controller route, cron, automated
   action, computed field, or call site. Follow only the relevant calls and
   overrides through `_inherit`, `_inherits`, and `super()`. Record exact paths
   and lines for conclusions that affect the implementation.
3. Trace the data path: model fields and dependencies, access rights and record
   rules, company context, inherited views and XPath targets, XML IDs, and
   existing tests. Check side effects such as writes, notifications, stock
   moves, accounting entries, or scheduled jobs when applicable.
4. Prefer the closest established implementation in the same project. Search
   local Odoo or OCA source only when it resolves a real uncertainty; verify
   its version and license before reusing a pattern. Use runtime metadata only
   for facts not settled by source, and respect the project's live-access rules.
5. For coupled changes, write a short context brief: business outcome, entry
   point, relevant paths, version, invariants, uncertainties, and smallest
   change. Then implement and run the relevant checks. Keep full logs/source
   available; summarize only after preserving failure details.

This complements `spec_driven_dev` for design, `code_review` for review, and
`upgrade_analysis` for migrations. It does not require a new tool, index, or
external service.
