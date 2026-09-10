# Troubleshooting

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

## HTTP server refuses to start / clients get 401

- Non-loopback binds (`0.0.0.0`, LAN IPs) require a token. Pass `--token`,
  set `ODOO_BOOST_MCP_TOKEN`, or configure `mcp_token`.
- Regenerate client configs after setting the token so the
  `Authorization: Bearer …` header is embedded:

  ```bash
  odoo-boost mcp-config --platform http
  ```

- Use `127.0.0.1` for local-only access.
- WSL2 usually forwards `localhost`; if not, use the WSL IP or enable the
  Windows firewall rule for the port.

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

- `pylint-odoo` and `odoo-ls` are optional. Without them, Odoo Boost falls back
  to the built-in AST scanner. Install with `pip install "odoo-boost[lint]"` for
  `pylint-odoo`.
- File tools respect `allowed_roots`. If a tool reports a path outside the
  allowed roots, widen the list in `odoo-boost.json` or clear it to disable
  confinement.

## Debugging

- Global logging: `--log-level DEBUG` or `ODOO_BOOST_LOG_LEVEL=DEBUG`. Logs go
  to stderr; stdout carries the MCP protocol stream.
- In an IDE, inspect the server's stderr log for `[odoo-boost]` warnings.
- `odoo-boost check --mcp` prints the exact command that was probed.
