# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2026-09-21

### Added

- First-class Zed integration using `AGENTS.md`, project-local Agent Skills,
  and merge-safe `.zed/settings.json` MCP configuration for stdio and HTTP.

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

[Unreleased]: https://github.com/mahfoudfx/odoo-boost/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/mahfoudfx/odoo-boost/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/mahfoudfx/odoo-boost/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mahfoudfx/odoo-boost/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mahfoudfx/odoo-boost/releases/tag/v0.1.0
