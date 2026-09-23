---
name: pattern-library
description: Use when a concrete Odoo implementation question needs an example pattern for fields, workflows, integrations, performance, migration, or troubleshooting; open only the relevant reference.
globs: ["**/*.py", "**/*.xml", "**/*.csv", "**/*.js", "__manifest__.py"]
---

# Odoo implementation pattern library

Use this library when a task needs a concrete pattern not already covered by a
focused Odoo Boost skill. Search `references/INDEX.md` by intent, then read only
one or two matching files. Do not load the whole directory.

Before applying an example:

1. Resolve the target Odoo version from Odoo Boost configuration. Its effective
   version facts and version note override examples in this library.
2. Inspect the closest existing implementation in the project, then local Odoo
   or OCA source when it materially improves correctness. Confirm module
   dependencies, XML IDs, field/method existence, and license compatibility.
3. Adapt the smallest relevant fragment to the business requirement. Do not
   paste full modules or add an abstraction merely because a template has one.
4. Validate access rights, multi-company behavior, translations, transactions,
   performance, and relevant tests for the changed flow.

For coupled or unfamiliar behavior, use `source_trace` first. Use the dedicated
security, testing, OWL, XML, accounting, stock, or upgrade skill when it is more
specific.

## Version-sensitive examples

Treat every reference as a candidate pattern, not as evidence about the active
Odoo release. In particular, confirm these changes against the configured
version note and target source:

- Odoo 17 and earlier use `tree` view types; Odoo 18+ use `list`.
- Controller JSON routes use `type="json"` through Odoo 18 and
  `type="jsonrpc"` in Odoo 19.
- OWL services, hooks, asset declarations, and component APIs must match the
  target web client. Do not infer an OWL major version from a reference title.
- Deprecated ORM decorators, method signatures, XML attributes, and manifest
  assets must be checked before reuse.

## High-risk examples

Some references explain migration, recovery, integration, or administrative
techniques. Never copy manual `cr.commit()` calls, raw SQL, `sudo()`, public
routes, direct `stock.quant` mutation, or arbitrary model operations into
normal application code. Prefer request-managed transactions, ORM access
checks, official stock workflows, allowlisted models and fields, and the
smallest required privilege. Use an exceptional technique only when its
transaction and security boundary is explicit and verified in the target
version. The dedicated security and domain skills take precedence.
