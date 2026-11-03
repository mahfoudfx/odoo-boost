# Refactoring results

The baseline is the working-tree source captured before this refactor, including
the user's existing changes. Measurements use the same local Python 3.12
environment and the same benchmark script against that saved source and the
refactored source.

## Before and after

| Measurement | Before | After |
|---|---:|---:|
| Production Python lines, including comments and blank lines | 8,161 | 8,102 |
| Python lines under `cli/` | 1,624 | 1,547 |
| Cached addon scan, median milliseconds | 71.043 | 25.815 |
| Directory reads per cached scan | 488 | 21 |
| Update all 12 agents, median milliseconds | 436.989 | 88.067 |
| File writes per update of all 12 agents | 1,262 | 4 |
| Passing tests | 786 | 801 |

Production line counts include all new modules under `src/`; tests and the
benchmark tool are counted separately. The net production reduction is 59 lines.
The primary improvements are shared rules, clearer responsibilities, and less
filesystem work.

## Measurement method

Run the offline benchmark with:

```bash
.venv/bin/python tools/benchmark_refactor.py
```

It creates an addon with 200 Python files, 200 XML files, a manifest, and 1,000
excluded build files across 100 directories. It measures cached scans after an
initial scan. Agent generation uses all 12 integrations with Odoo 18.0 guidance
and the default native/Windows companion configurations. Updates are measured
after an initial installation. Each reported time is the median of five runs;
before and after runs were sequential, without tests running concurrently.

Directory reads are counted through `os.scandir`; writes count both
`Path.write_text` and the private MCP configuration writer. Four writes remain
because agents with different reference directories update their shared
`AGENTS.md` in order. Shared skills and unchanged ownership manifests are no
longer rewritten. Times are synthetic local measurements, not live Odoo latency
or a guarantee for every project.

## Changes

- Centralized project paths, VENV interpreter resolution, filesystem access
  rules, active MCP configuration lookup, and duplicated defaults.
- Shared agent selection/instantiation, batch generation, file reporting, empty
  directory cleanup, and current/legacy Cursor guideline formatting.
- Pruned excluded directories before scanning and reused the inventory when
  rebuilding an addon cache. Removed redundant model classification and obsolete
  AST compatibility branches while retaining field extraction behavior.
- Cached immutable bundled resources, installed shared skill destinations once,
  and skipped identical file and manifest writes. Project files are reread to
  preserve local edits; MCP file permissions remain enforced.
- Extracted structured lint execution into `diagnostics.py`. CLI output now
  displays all diagnostics directly; MCP compaction and response limits remain
  in the tool adapter.
- Consolidated documentation checkout hashing, removed an unused ORM field
  fetch, and fixed unnecessary blank lines on the first TOML configuration
  update.

Regression checks cover batch output equivalence, unchanged timestamps, local
edits, scanner pruning, cache invalidation, internal/external symlinks, shared
access rules, fallback linting, complete CLI diagnostics, and documentation
cache revisions. Existing uncommitted changes were retained.

## Validation

All 801 tests pass with 85.45% combined statement/branch coverage, exceeding the
configured 70% threshold. Ruff lint and formatting, mypy on all 88 source
modules, CLI version/help smoke checks, and `git diff --check` also pass.
