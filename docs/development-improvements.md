# Development improvements: before and after

This report covers this implementation only. Pre-existing workspace changes were
preserved. The implementation is local; no release or production deployment was
performed.

| Area | Before | After |
|---|---|---|
| Tool inventory | 23 tools, including one duplicate query alias and two misleading names | 30 tools; duplicate removed, names corrected, eight focused development tools added |
| Inheritance and routes | Runtime field contributors and website page/rewrite records only | Explicit names for existing behavior; local declarations for inheritance, delegation, transitive parents, method locations, view parents and controller decorators |
| Diagnostics | Separate pylint/fallback and LS output | Unified report with normalized findings, duplicate suppression, engine availability, coverage and limitations |
| Fallback checks | Python syntax, direct commits, selected deprecated API checks | Also XML syntax, manifest data/demo files, local ACL/reference candidates, SQL construction, sudo and public/CSRF-disabled route review candidates |
| Skills | Review procedures primarily expressed as instructions | Review, XML, security, testing and tracing skills reference executable tools and require reporting actual verification |
| Changed-code checks | Agent selected checks without a dedicated diff tool | Git-based recommendations include staged, unstaged and untracked changes |
| Environments | One configured connection | Named profiles, CLI/environment selection, readonly default per profile, profile visible in check output |
| Runtime drift | Agent manually compared local/runtime tool results | Field-name and XML ID presence comparison, local manifest version and runtime module metadata |
| Testing | Agent assembled Odoo commands | Focused runner requires named disposable database, dedicated test configuration, source and VENV; reports missing test execution as partial |
| Efficiency | Compaction, scan caching and repeated-call guards | Per-server calls/failures/latency/response sizes, consecutive same-tool counts, process-wide cache statistics and optional call budget |

## Breaking interface changes

- `get_model_inheritance` → `get_model_field_contributors`.
- `list_routes` → `list_website_pages`.
- `database_query` removed; use `search_records` (default record limit 20).

No aliases remain. Restart MCP clients and update saved integrations using the
removed names. Agent skill updates reach existing installations through
`odoo-boost update`.

## New entry points

- MCP: `trace_odoo_source`, `list_controller_routes`, `diagnose_odoo_code`,
  `plan_changed_checks`, `compare_local_runtime`, `tool_readiness`,
  `tool_metrics`, `run_odoo_tests`.
- CLI: `diagnose`, `changed-checks`, `profiles list`, `profiles use`, `test`.
- Configuration: see [named environments and checks](configuration.md#named-environments-and-development-checks).

## Verification and limits

The complete suite passes: **732 tests**, **84.94% branch-aware coverage**.
Ruff lint, formatting, mypy and diff whitespace checks pass. A wheel builds
successfully. Regression checks exercise route/model/view discovery, static
checks, changed-file recommendations, profile selection, database refusal,
empty test execution, call budgets, metrics and mocked runtime comparison.

Live Odoo permissions, real Odoo LS execution and real database test execution
were not verified against a running deployment during this work. Registration
and prerequisite reporting do not establish live usability.

Source tracing describes static declarations in the selected directory, not
runtime MRO or effective routing. Drift comparison does not compare effective
view architecture or field semantics. Static checks flag review candidates;
they do not establish absence of SQL injection, N+1 queries or multi-company
leaks. Changed checks are recommendations, not an automatic test scheduler.
Metrics count response characters rather than tokens and cover only this MCP
server; native agent commands and model turns remain outside its controls.
