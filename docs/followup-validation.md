# Follow-up validation

## Installed package and Python compatibility

Built the core 0.14.0 and optional documentation 0.1.1 wheels with Hatchling.
Installed both into temporary environments using the development dependencies
exported from the existing frozen lockfile. The repository environment and
dependency metadata were unchanged.

The full suite passes against the installed wheel on Python 3.10.22, 3.11.15,
3.12.13, and 3.13.16. Coverage source paths were checked to confirm execution
from `site-packages/odoo_boost`, rather than the editable source tree.

| Python | Passing tests | Combined coverage |
|---|---:|---:|
| 3.10.22 | 721 | 85.45% |
| 3.11.15 | 721 | 85.41% |
| 3.12.13 | 721 | 85.41% |
| 3.13.16 | 721 | 85.41% |

A separate Python 3.12 smoke check outside the repository verified the console
entry point, new modules, all 25 bundled skills, integrity and series metadata
of all three documentation archives, installation of the 18.0 documentation
pack, and a successful indexed offline search.

## Targeted mutation testing

Mutmut 3.8.1 ran in an isolated copy of the workspace. Only `local_paths.py` and
`source_files.py` were mutated; this is not a whole-project mutation score.

| Outcome | Before additional tests | After additional tests |
|---|---:|---:|
| Mutations generated | 57 | 57 |
| Mutations caught by tests | 49 | 56 |
| Behavior-changing survivors | 7 | 0 |
| Equivalent survivors | 1 | 1 |

The missing behavior was Windows-style VENV directory selection and interpreter
path spelling. Three new cases exercise POSIX layout, Windows layout, and a
regular file named `Scripts` which must not select Windows layout. No production
change was required. The suite increased from 718 to 721 collected cases.

The equivalent survivor forces `resolve_path` to join the base directory even
for an absolute path. Joining a `Path` with an absolute path already discards
the base, so this mutation produces the same result. It was classified by
inspection rather than hidden with a mutation exclusion.

The selected tests covered local policy, project context, AST scanning,
diagnostics, Odoo LS arguments, CLI behavior, and the new VENV layout cases.
No mutants timed out or lacked test coverage.

## Unused code, fixtures, and dependencies

- Vulture 2.16 found no unused-code candidates at 90% confidence. Lower-confidence
  findings were reviewed: they are framework-registered CLI commands, MCP
  resources/prompts, pytest markers, and mock configuration attributes.
- All eight declared project fixtures occur in collected tests' fixture
  dependency closures. No unused project fixture was identified.
- At audit time, `packaging>=24.0` had no references in production Python, tests,
  or project tools. Its explicit runtime requirement was a removal candidate;
  development dependencies still require it transitively.
- At audit time, the `xml` extra installed `lxml`, but production code did not
  use it and no RelaxNG validation was implemented. README and getting-started
  descriptions advertised that validation. Retaining the extra preserves
  compatibility; the documentation correction is recorded below.

These checks do not prove that all remaining code is essential. No dependency
or public installation extra was removed during this audit.

## Real addon measurements

Read-only scans of three existing local custom addons were compared against the
saved source from before the production refactor. Workloads are labeled without
including project source or model names. No Odoo instance was contacted and no
addon was modified.

| Workload | Python/XML files | Parse-cache-cleared scan, before/after ms | Cached scan, before/after ms |
|---|---:|---:|---:|
| Addon 1 | 8 / 9 | 13.929 / 11.181 | 2.407 / 1.663 |
| Addon 2 | 7 / 1 | 10.267 / 9.250 | 1.354 / 0.974 |
| Addon 3 | 122 / 82 | 464.831 / 407.125 | 30.889 / 18.820 |

Parse-cache-cleared times are medians of nine runs; cached times are medians of
21 runs. Operating-system disk caches were not flushed. Before/after runs were
sequential, without compatibility tests or mutation workers running. Full scan
results had identical SHA-256 digests for every workload. Cached scans improved
by approximately 28–39%; the larger synthetic benchmark gains are not assumed
to apply to every real addon.

Ruff lint and formatting, mypy, and `git diff --check` also pass.

## Initial dependency and documentation cleanup

The two follow-ups were subsequently addressed:

- Removed the unused direct `packaging` requirement, reducing direct runtime
  requirements from nine to eight. The lockfile changed only at the project's
  dependency and requirement entries; every locked package version was retained.
  `packaging` remains locked as a transitive development dependency.
- Corrected README, getting-started, and contributing guidance to describe
  `defusedxml` inspection and `lxml` as an optional compatibility dependency for
  external tooling. RelaxNG validation requires separate tooling. The `xml`
  extra and all other installation extras remain available.

Rebuilt wheel metadata differs only by the removed requirement and updated
README text. A fresh core-only environment has neither `packaging` nor `lxml`
installed; server imports, CLI entry point, addon scanning, fallback linting,
agent generation, and bundled skills all work there. `uv pip check` confirms
compatible installed dependencies, and `uv lock --check --offline` succeeds.
All 721 tests pass against the rebuilt installed wheel on Python 3.12, alongside
Ruff lint/formatting, mypy, and diff checks. No runtime source changes or new
tests were needed for this dependency and documentation cleanup.

## Unused extra cleanup

Following the request to remove unused extras rather than retain speculative
compatibility, removed `xml` and its `lxml` dependency. Removed `all` as well:
after discarding `lxml` and its redundant `PyYAML` entry, it duplicated `lint`.
The remaining extras are `lint` (implemented OCA checks) and `dev` (test, lint,
format, and type-check tools). Each of the eight runtime requirements has a
production reference; no other unused runtime requirement was identified.

Updated installation and contributing documentation and recorded the removed
extras in the changelog. The lockfile drops only `lxml`, reducing its package
count from 77 to 76; all remaining versions are preserved. The rebuilt wheel
exposes only `lint` and `dev`, with no `lxml` requirement or optional `PyYAML`
duplicate. Base XML inspection remains available through `defusedxml`.

Validated core XML inspection and fallback linting without `lxml` or `packaging`
installed, then installed `[lint]` and successfully ran real `pylint-odoo`
diagnostics. Installed `[dev]` from the rebuilt wheel and ran all 721 tests
successfully (85.41% coverage). Wheel metadata, dependency consistency, frozen
lockfile, Ruff, mypy, and diff checks also pass. The core, `lint`, and `dev`
requirement lists are unchanged by this extra cleanup.
