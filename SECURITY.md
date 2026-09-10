# Security Policy

## Supported Versions

Only the latest released minor version receives security fixes.

| Version | Supported |
|---|---|
| 0.5.x | :white_check_mark: |
| < 0.5 | :x: |

## Reporting a Vulnerability

Please report suspected vulnerabilities privately through
[GitHub Security Advisories](https://github.com/mahfoudfx/odoo-boost/security/advisories/new).
Do **not** open a public issue for security reports.

Include:

- A description of the issue and its impact.
- Steps to reproduce (a minimal `odoo-boost.json` / command, if relevant).
- Affected version(s) and environment (OS, Python, Odoo).

We aim to acknowledge reports within a few business days and will coordinate a
fix and disclosure timeline with you.

## Security Model

Odoo Boost is a local developer tool that connects to an Odoo instance with the
credentials you provide. Keep the following in mind:

- **Credentials are stored in plaintext** in `odoo-boost.json`. On POSIX the
  file is written with owner-only permissions (`0600`) and `odoo-boost install`
  appends it to an existing `.gitignore`, but you are responsible for keeping it
  out of version control. Prefer an Odoo API key over a password and use a
  dedicated technical user.
- **HTTP transport requires a bearer token for non-loopback binds.** The server
  refuses to start on `0.0.0.0`/LAN interfaces without `mcp_token` (or
  `--token` / `ODOO_BOOST_MCP_TOKEN`). Generated HTTP client configs embed the
  token, so treat those files as secrets as well.
- **`readonly` and `allowed_roots` are guardrails, not a sandbox.** `readonly`
  blocks known mutating/private methods on `execute_method`; `allowed_roots`
  confines the local file tools. Odoo access rights remain the source of truth
  for ORM operations, and the OS user governs file access.
- **`execute_method` can call arbitrary public ORM methods** with the
  permissions of the configured Odoo user. Enable `readonly` or use a
  restricted user when running untrusted prompts.
- **Local tools (`inspect_local_addon`, `lint_odoo_code`, `resolve_local_xml_id`,
  `check_odoo_ls`)** read files and may spawn local processes (`pylint-odoo`,
  `odoo-ls`). Set `allowed_roots` to confine them to your project directory.
