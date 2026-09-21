# Detailed source-trace checklist

Adapted from the trace-first workflow in `unclecatvn/agent-skills` and the
context-gathering workflow in `fhidalgodev/odoo-development-skill`. Use it only
for coupled or unfamiliar changes; the main `source_trace` skill defines when.

## Resolve the running code

1. Confirm the configured Odoo series. Ignore short addon manifest versions
   such as `1.2`. If config and source disagree, report the conflict.
2. Resolve addon roots in their actual `addons_path` order, including core,
   Enterprise, OCA, and custom roots. If the same module occurs twice, the first
   root wins.
3. Read the target module manifest and the transitive dependencies needed by
   the symbols you plan to extend.

## Trace the change

Use narrow searches and line ranges rather than reading whole repositories:

- Model: `_name`, every matching `_inherit`, `_inherits`, and field redefinition.
- Method: every definition, its `super()` chain, hooks called by the relevant
  range, and modules that affect load order.
- Field path: confirm each relation hop used by `related`, `@api.depends`,
  domains, or record rules. Stop at a missing or non-relational hop.
- View: base view XML ID, every relevant inherited view, and the exact XPath
  anchor. Confirm the expected match count in the final architecture.
- Security: ACL, record rules, groups, company context, public/portal exposure,
  and whether a controller or wizard can bypass server-side checks.
- Side effects: writes, chatter, activities, emails, jobs, accounting entries,
  stock moves, recomputation, cache/flush boundaries, and external calls.
- Tests: closest upstream or project test, then the smallest regression that
  protects the requested behavior.

Do not infer that a symbol is available because it exists in the current
checkout or database. The declaring module must be in the dependency graph.
When two unrelated modules override the same method, state that ordering is
uncertain until dependencies or the active registry settle it.

## Context brief

For each symbol changed, capture:

| Layer | Symbol | Evidence | Existing behavior | Intended change |
|---|---|---|---|---|
| model/field/method/view/security/test | technical name | `path:line`, `NOT FOUND`, or `UNCERTAIN: reason` | concise fact | smallest change |

A claim that determines code needs source evidence. If evidence is missing,
inspect more, drop the change, or state the uncertainty. Keep the brief short;
split work that cannot be explained clearly.

## Completion review

Check the diff for the business acceptance criteria, version syntax,
dependency order, access control, multi-company isolation, translations,
transaction safety, batch behavior, upgrade safety, and meaningful tests.
Report the checks actually executed and any runtime fact that remains untested.
