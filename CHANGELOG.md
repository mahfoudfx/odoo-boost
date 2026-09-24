# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.13.0] - 2026-09-24

### Added

- Focused skills for editing translations and extending existing models, with
  routine-task routing that favors direct edits and relevant checks.
- Project context reporting for the custom-addon VENV, Odoo configuration,
  external source roots, and effective addons path.
- Version-matched offline documentation search and installer choices for cached,
  packaged, local-checkout, and downloaded sources. A separate optional package
  carries pinned Odoo 18, 19, and 20 text snapshots.

### Changed

- Narrow the default guidance for simple view, report, Owl, controller, and
  translation changes so agents load deeper references only when needed.
- Build and attach the optional documentation package to GitHub Releases while
  keeping the core PyPI publication separate.

## [0.12.0] - 2026-09-23

### Added

- Opt-in `.gitignore` management during install and uninstall, with exact-path
  previews, explicit CLI flags, and removal limited to managed entries for
  files actually deleted.

## [0.11.0] - 2026-09-23

### Added

- Explicit Deadline mode for the shortest route to a working Odoo change,
  while retaining task-specific version, reference, and security checks.
- OCA addon migration guidance for intermediate versions, metadata, and
  separating compatibility work from feature changes.
- On-demand verification guidance by Odoo change type and a scenario set for
  evaluating agent behavior in supported clients.

### Changed

- Route low, medium, and high effort by affected behavior rather than forcing
  every task through first-pass coding or fixed tool-call counts.
- Remove the `lean_tools` switch and register all 23 MCP tools; clients decide
  whether to load their definitions eagerly or through tool discovery. Existing
  saved `lean_tools` values are ignored.
- Generate Claude Code's `CLAUDE.md` as an import of shared `AGENTS.md`.
- Use proportionate offline checks for behavioral changes while preserving
  the opt-in boundary for database and server commands.
- Shorten generated agent rules to a small assurance router, keep Deadline as
  an urgency modifier, and narrow skill descriptions that could activate on
  routine edits.
- Remove stale `lean_tools` compatibility documentation and replace a hanging
  offline MCP test with a focused registered-handler check.

## [0.10.2] - 2026-09-21

### Fixed

- Generate standards-compliant, hyphenated skill identifiers and matching
  directory names for Pi, OpenCode, Codex, Antigravity, and Zed.
- Install Claude Code skills in its native `.claude/skills/` directory.

## [0.10.0] - 2026-09-21

### Added

- Three-level adaptive agent workflow: unconditional first-pass coding, medium
  effort for bounded coupled work, and high effort for production readiness and
  high-risk changes. Generated instructions include explicit edit-or-escalate
  and post-edit stop conditions.
- Rolling MCP repeated-call protection, which blocks identical requests even
  when an agent alternates them with other tools.
- Explicit opt-outs for deliberate broad source inspection:
  `allow_external_local_paths` in configuration and
  `allow_collection_scan` on `inspect_local_addon`.

### Changed

- New configurations advertise the lean eight-tool MCP profile by default.
- Local MCP file tools are confined to `project_path` by default when no
  `allowed_roots` are configured.
- `inspect_local_addon` now requires an addon manifest by default, preventing
  accidental recursive scans of Odoo core, addon collections, and workspace
  roots.
- Documentation now distinguishes advisory model workflow rules from enforceable
  MCP limits and notes that native file, search, shell, test, and model-turn
  activity remains outside Odoo Boost's control.

## [0.9.0] - 2026-09-21

### Changed

- The interactive installer now installs official Odoo LS and `pylint-odoo` by
  default. Users can decline the prompt or pass `--skip-dev-tools` for a
  lightweight or offline setup.

## [0.8.0] - 2026-09-21

### Added

- First-class Zed integration using `AGENTS.md`, project-local Agent Skills,
  and merge-safe `.zed/settings.json` MCP configuration for stdio and HTTP.
- Official Odoo LS installer and discovery (`odoo-boost odoo-ls install|status`)
  with platform-specific release selection and structured CLI diagnostics.

### Fixed

- Generate Antigravity remote MCP entries with its current `serverUrl` schema.
- Verify HTTP servers with an MCP `initialize` request and support an explicit
  client-facing `mcp_http_url` for Windows-to-WSL connections.

## [0.7.1] - 2026-09-14

### Changed

- Enhanced Agent Operating Rules (`operating_rules.md`) with a strict prohibition on live environment execution: never run `odoo-bin shell` or live Python diagnostic scripts without explicit user request, require code analysis exclusively via file reading (`view_file`, `grep_search`), and require direct file edits without unsolicited live verification. Included across all generated agent guidelines (`AGENTS.md`, `CLAUDE.md`, etc.).

## [0.7.0] - 2026-09-11

### Added

- `odoo-boost uninstall`: New CLI command to cleanly remove generated agent files
  (`AGENTS.md`, `CLAUDE.md`, `.mcp.json`, skills) and empty directories, with options
  to keep config (`--keep-config`) or run non-interactively (`-y`).
- Orphan agent reconciliation in `odoo-boost update`: Automatically detects and cleans up
  files from removed agents, while preserving shared files like `AGENTS.md`.
- Agent Operating Rules & Boundaries in core guidelines (`operating_rules.md`) defining
  workflow modes (direct implementation vs. plan & walkthrough), command boundaries,
  and scope restraint.

## [0.6.0] - 2026-09-11

### Added

- Cross-OS MCP startup: generated configs now work from Windows-native IDEs while
  the project lives in WSL. `mcp_target: "auto"` writes a `*.windows.*` companion
  that wraps the interpreter in `wsl.exe`.
- HTTP transport (`odoo-boost mcp --transport http`) with a static bearer-token
  verifier; non-loopback binds are refused without a token, and generated
  HTTP configs embed the `Authorization: Bearer` header.
- `odoo-boost mcp-config --platform native|windows|http` to regenerate only MCP
  configs, and `odoo-boost check --mcp` to verify the server's `initialize`
  handshake.
- Opt-in tool guardrails: `readonly` blocks mutating `execute_method` calls and
  `allowed_roots` confines local file tools.
- Central tool registry, shared tool helpers, stderr-only logging with
  `--log-level`, and a declarative agent spec registry.
- `uv.lock`, pre-commit hooks, Dependabot, and a wheel smoke-test CI job.
- Token-efficient tool responses: compact by default with per-call
  `response_format="full"`, pagination, secret redaction, a global
  `max_response_chars` budget, a `lean_tools` profile, and a compact
  `odoo://guidelines/oca/compact` resource.

### Security

- `odoo-boost.json` is written with owner-only (`0600`) permissions on POSIX and
  is appended to an existing `.gitignore` during `install`.
- HTTP transport authentication is required for non-loopback binds.

### Fixed

- `search_docs` version normalization for patch versions (`18.0.1` → `18`) and
  two-digit majors (`10.0` → `10`).
- MCP `serverInfo.version` is now populated.
- Consistent error handling for malformed JSON tool arguments.

## [0.5.0] - 2026-09-07

### Added

- Pure-Python AST/XML scanner for local addons (no Docker required).
- Expanded MCP tool set (model schema, records, aggregation, XML IDs,
  inheritance, workflows, routes, logs, and more) plus MCP resources and prompts.
- 20 progressive skills with a routing index across core, workflow, and domain
  patterns, installed for all 11 supported agents.

## [0.4.1] - 2026-02-20

### Changed

- Documented `expand`/`string` search-view attribute support per Odoo version.

## [0.4.0] - 2026-02-10

### Added

- Configurable generation via `generate_mcp` and `generate_ai_files`, plus
  `.gitignore` documentation for generated files.

## [0.3.0] - 2026-02-07

### Changed

- MCP configs now use the absolute Python interpreter path for robust server
  resolution.

## [0.2.1] - 2026-02-07

### Fixed

- CI reusable workflow.

## [0.2.0] - 2026-02-07

### Added

- CI/CD pipeline, test suite, linting, and the release/auto-tag workflow.

## [0.1.0] - 2026-02-06

### Added

- Initial implementation: connection layer, core MCP server, guidelines, and the
  install wizard.

[Unreleased]: https://github.com/mahfoudfx/odoo-boost/compare/v0.13.0...HEAD
[0.13.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.10.2...v0.11.0
[0.7.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/mahfoudfx/odoo-boost/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/mahfoudfx/odoo-boost/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mahfoudfx/odoo-boost/releases/tag/v0.1.0
