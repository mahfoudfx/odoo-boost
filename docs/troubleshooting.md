# Troubleshooting

## Many tool calls or very high token use on small edits

- Run `odoo-boost update` after upgrading the package. This refreshes the generated agent guidelines and XML view skill; existing generated files do not change by themselves.
- For a source-only change, the agent should locate the relevant files, edit them, and inspect the diff. Live Odoo queries are useful when the task depends on current database state.
- New configurations advertise 8 common tools. To use omitted tools such as `list_views` and `list_access_rights`, set `"lean_tools": false` to expose all 23.
- `compact_responses` and `max_response_chars` limit individual MCP outputs.
  `max_consecutive_identical_calls` blocks mechanical repetition of one call,
  while generated instructions impose investigation budgets and prevent repeated
  native file reads. `cache_local_scans` avoids reparsing unchanged addons.
  Odoo Boost still cannot hard-cap reasoning or native file operations performed
  internally by the agent host; compare the host's call/file trace when totals
  remain unexpectedly high.
- An Odoo “no create access” error identifies a denied operation for the configured user. If the task concerns access rights, inspect that model's ACLs; otherwise stop that line of investigation and report the denial.

## The MCP server does not appear in my IDE

1. Verify the configured server actually starts:

   ```bash
   odoo-boost check --mcp
   ```

   This spawns the resolved command and performs the MCP `initialize`
   handshake. A failure here is almost always a bad interpreter path or a
   missing `odoo-boost.json`.

2. Regenerate the configs:

   ```bash
   odoo-boost update
   ```

3. Confirm your IDE is reading the file Odoo Boost wrote (see the
   [agent table](agents.md)).

## Windows IDE, project inside WSL

A Windows-native IDE cannot execute a Linux interpreter path. Two options:

- **stdio wrapper** — regenerate with the WSL launcher and use the generated
  `*.windows.*` config (or switch `mcp_target` to `"wsl"`):

  ```bash
  odoo-boost mcp-config --platform windows
  ```

  Ensure `wsl_distro` matches your distribution (default `Ubuntu`).

- **HTTP transport** — start the server once and point the IDE at the printed
  URL (`http://localhost:8765/mcp` by default). WSL2 forwards `localhost`, so
  Windows IDEs reach it without spawning a process:

  ```bash
  odoo-boost mcp --transport http --host 0.0.0.0 --port 8765 --token "$MCP_TOKEN"
  ```

  Keep the command running. Put the same token in `mcp_token`, run
  `odoo-boost mcp-config --platform http`, and reload MCP servers in the IDE.
  Current Antigravity configurations use `serverUrl`; Odoo Boost generates it
  automatically.

  From Windows PowerShell, verify WSL forwarding with:

  ```powershell
  Test-NetConnection localhost -Port 8765
  ```

  If that fails, get the current address with `hostname -I` inside WSL and set
  the exact client endpoint while continuing to bind on all WSL interfaces:

  ```json
  {
    "mcp_host": "0.0.0.0",
    "mcp_port": 8765,
    "mcp_http_url": "http://172.30.10.2:8765/mcp"
  }
  ```

  Regenerate the HTTP configuration after an address change. WSL addresses can
  change after restart; fixing Windows localhost forwarding is preferable for
  a stable setup.

## HTTP server refuses to start / clients get 401

- Non-loopback binds (`0.0.0.0`, LAN IPs) require a token. Pass `--token`,
  set `ODOO_BOOST_MCP_TOKEN`, or configure `mcp_token`.
- Regenerate client configs after setting the token so the
  `Authorization: Bearer …` header is embedded:

  ```bash
  odoo-boost mcp-config --platform http
  ```

- Use `127.0.0.1` for local-only access.
- WSL2 usually forwards `localhost`; if not, use `mcp_http_url` with the WSL IP
  and allow the port through Windows Firewall.

## "Cannot reach Odoo" / authentication failures

The MCP server starts in **resilient mode** when Odoo is offline: tools report
the connection error on demand instead of preventing startup. Check:

- `odoo-boost check` — verifies URL, database, and credentials.
- The URL is reachable from the machine running `odoo-boost` (inside WSL, not
  just Windows).
- Prefer an Odoo API key over a password; use a dedicated technical user.

## `odoo-boost.json` not found

The server resolves the config by walking up from its working directory. An IDE
may start it from an unexpected directory. Generated commands include an
explicit `-c <path>`, so regenerate the config; or pass `--config` manually.

## Linting or language-server tools

- The installer selects `pylint-odoo` and official Odoo LS by default. Without
  them, Odoo Boost falls back
  to the built-in AST scanner. Install with `pip install "odoo-boost[lint]"` for
  `pylint-odoo`.
- File tools use `project_path` as their default boundary and respect explicit
  `allowed_roots`. If a tool reports a path outside the allowed roots, widen the
  list in `odoo-boost.json`; use `allow_external_local_paths=true` only when
  unrestricted shared-source inspection is intentional.

## Debugging

- Global logging: `--log-level DEBUG` or `ODOO_BOOST_LOG_LEVEL=DEBUG`. Logs go
  to stderr; stdout carries the MCP protocol stream.
- In an IDE, inspect the server's stderr log for `[odoo-boost]` warnings.
- `odoo-boost check --mcp` prints the exact command that was probed.
