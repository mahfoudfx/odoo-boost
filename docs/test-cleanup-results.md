# Test cleanup results

Comparison against the working tree immediately after the production refactor:

| Measurement | Before | After |
|---|---:|---:|
| Passing pytest cases | 801 | 718 |
| Combined statement/branch coverage | 85.45% | 85.47% |
| Agent/platform matrix cases | 36 | 48 |
| Test Python lines, including comments and blank lines | 6,005 | 6,018 |

The suite has 83 fewer collected cases through consolidation. All 12 agents
are checked across native, Windows, HTTP, and automatic companion generation.
Parsed JSON/TOML/YAML configuration equality replaces substring assertions and
overlapping private-command checks. Stronger assertions add 13 lines overall.

Generic tests previously grouped under `TestPiAgent` now live under the shared
agent contract class. Static agent metadata checks no longer instantiate every
agent with filesystem fixtures, and related absolute-path assertions share one
test per agent. Distinct format, custom-port, override, migration, permissions,
symlink, and preservation checks remain.

Diagnostics tests exercise `run_lint()` with the external process mocked and
without unnecessary server context. Separate MCP tool tests verify compact and
full responses. Registry exception checks use `pytest.raises`, removing manual
defensive branches. Production code was unchanged during this cleanup.

Validation: all 718 tests pass; Ruff lint and formatting, mypy, and
`git diff --check` pass. This was a targeted cleanup of verified overlap and
weak assertions, not proof that every remaining test or fixture is essential.
