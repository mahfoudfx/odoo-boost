# Security audit checks

Search for each relevant construct, then judge its data flow. A textual match is
evidence to inspect, not automatically a defect.

- `sudo`, `with_user`, `with_company`: identify attacker-controlled records,
  domains, fields, values, and x2many commands. Keep elevation minimal.
- Public model methods and routes: validate recordsets and parameters. Use POST
  for state changes, retain CSRF on HTTP routes, and match authentication to the
  data exposed.
- Raw SQL: prefer the ORM. If SQL is necessary, parameterize values and validate
  dynamic identifiers. Preserve record-rule filtering where user access matters.
- Dynamic domains: compose trusted conditions with `fields.Domain`; never append
  an untrusted domain to a security restriction.
- Sensitive and related fields: use field groups, inspect `related_sudo`, and
  test reads and writes as a restricted user.
- HTML: inspect `Markup`, `markup`, `innerHTML`, `insertAdjacentHTML`, and template
  output. Keep literals trusted and escape dynamic content.
- Files and data: use `file_open` for addon resources; reject `eval`, `exec`, and
  `pickle`; constrain any unavoidable `safe_eval` to trusted administrators.
- Dynamic record access: use `record[field_name]` after validating the field,
  rather than `getattr` or `setattr` with untrusted names.
- Secrets: compare with `odoo.tools.consteq` and never log or expose credentials.
