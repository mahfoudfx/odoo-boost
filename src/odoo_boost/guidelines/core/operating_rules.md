## Agent Operating Rules & Boundaries

### 1. Adaptive Effort Levels
- **Low effort (default for clear local edits):**
  - For labels, translations, existing view fields, formatting, and small methods with a known target.
  - Locate the exact definition, edit directly, inspect the diff, and perform the cheapest relevant check. A label-only XML edit needs the right record and valid XML, not a new test suite.
- **Medium effort:**
  - For bounded multi-file features, localized refactoring, unfamiliar inheritance, packaging, integrations, and persistent schema changes.
  - Inspect direct dependencies and check the affected Odoo boundary: imports, manifest/data order, XML IDs and XPath anchors, access rights, or tests where relevant.
- **High effort:**
  - For broad architectural refactoring, production/release readiness, shipping validation, migrations, security audits, accounting/stock integrity, and exhaustive investigations.
  - Plan only when the task needs coordination or the user explicitly asks for a plan. Validate in proportion to risk and distinguish unrelated failures.
- **Deadline mode (explicit request, orthogonal to effort):**
  - Take the shortest path to a working result: identify the target, edit, perform the cheapest check that catches a realistic error, and report briefly.
  - Skip plans, broad scans, optional skills, and unrelated cleanup. Keep the configured version, exact symbols/anchors, and relevant security checks. Report behavior that could not be verified.
- Choose assurance from the task's affected behavior, not a fixed sequence of levels. Start inspection narrowly even for high effort. Raise effort for a named dependency or risk; high-risk work can start at high effort.

### 2. Strict Prohibition on Live Environment Execution
- **NEVER use `odoo-bin shell`** or live Python diagnostic scripts unless the user explicitly writes *"launch a shell"* or *"check in database"* (*"lance un shell"* or *"vérifie en base"*).
- Use targeted source reads and searches first. Static checks and focused offline tests are allowed when they address a plausible failure in the change.
- **No Unsolicited Live Commands:** The agent's core responsibility is writing clean, idiomatic code and editing files. Do **not** automatically execute `odoo-bin` module upgrades (`-u`), reboot running servers/daemons, or run live verification scripts in `odoo shell` unless the user explicitly asks (e.g. *"upgrade the module"*, *"test this in db"*, *"run verification"*).
- **Proportionate tests:** Do not create tests for trivial presentation edits. For behavior, access control, or data changes, use existing focused offline tests when available. Add a regression test when it verifies a meaningful failure mode; do not mirror the implementation.

### 3. Scope Restraint
- Only edit the files, models, and records relevant to the request.
- Avoid re-authoring or generating massive translation catalogs or auxiliary files unless explicitly requested.

### 4. Context and Tool Budget
- Read the closest implementation and configuration first. Keep a short evidence map of
  files already read; do not read an unchanged file twice in the same task.
- Start with targeted searches and compact tool responses. Load a routed skill or
  reference when its procedure addresses the task; add others for concrete uncertainty.
  Do not load the full pattern library for a routine edit.
- Stop when the requested behavior and its applicable checks are satisfied. Avoid exploratory
  reads, broad checks, cleanup, and unrelated fixes after that point. Do not use a fixed call
  count as a substitute for first-pass correctness.
- Never repeat a tool call with identical arguments after it succeeds or returns a stable
  error. Reuse the result. After two failed approaches with the same blocker, change the
  approach or report the blocker instead of looping.
- Search once with grouped patterns, inspect only matching ranges, and broaden gradually.
  Do not request full output merely to avoid choosing fields, filters, files, or a model.
- Never recursively scan an Odoo checkout, shared base source, or addons collection during
  ordinary custom-addon work. Resolve uncertainty with the exact inherited symbol/file; broad
  source scans require an explicit audit scope.

### 5. Enforcement Boundary
- These rules guide model behavior; they cannot guarantee it. Odoo Boost can cap
  its MCP responses and detect repeated calls through its server. The client
  decides whether tool schemas are sent on every model request or discovered on
  demand. Native editor reads, searches, shell commands, tests, model turns, and
  total per-task calls remain outside Odoo Boost's visibility and control.
