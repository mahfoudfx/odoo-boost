## Agent Operating Rules & Boundaries

### 1. Adaptive Effort Levels
- **First-pass coding (default, fast and token-efficient):**
  - For targeted bug fixes, field/button additions, view/UI adjustments, method updates, security rule tweaks, or translation updates.
  - Implement directly by editing the target files immediately. Do **not** create `implementation_plan.md` or `walkthrough.md`.
- **Medium effort:**
  - For bounded multi-file features, localized refactoring, unfamiliar inheritance, packaging, integrations, and persistent schema changes.
  - Inspect direct dependencies and run only focused checks relevant to the changed behavior.
- **High effort:**
  - For broad architectural refactoring, production/release readiness, shipping validation, migrations, security audits, accounting/stock integrity, and exhaustive investigations.
  - Plan only when the task needs coordination or the user explicitly asks for a plan. Validate in proportion to risk and distinguish unrelated failures.
- Every task starts in first-pass coding, including apparently complex tasks. An explicit user
  request may set a higher assurance target, but the initial inspection remains narrow. Escalate
  only for a named dependency, failed direct approach, or specific risk—not apparent complexity.

### 2. Strict Prohibition on Live Environment Execution
- **NEVER use `odoo-bin shell`** or live Python diagnostic scripts unless the user explicitly writes *"launch a shell"* or *"check in database"* (*"lance un shell"* or *"vérifie en base"*).
- Codebase analysis must be performed **exclusively by reading code files** (`view_file`, `grep_search`).
- When a modification is requested, proceed directly to editing the target files without any unsolicited live testing or verification phase.
- **No Unsolicited Live Commands:** The agent's core responsibility is writing clean, idiomatic code and editing files. Do **not** automatically execute `odoo-bin` module upgrades (`-u`), reboot running servers/daemons, or run live verification scripts in `odoo shell` unless the user explicitly asks (e.g. *"upgrade the module"*, *"test this in db"*, *"run verification"*).
- **No Unsolicited Automated Tests:** Do not generate or execute automated tests unless explicitly instructed.

### 3. Scope Restraint
- Only edit the files, models, and records relevant to the request.
- Avoid re-authoring or generating massive translation catalogs or auxiliary files unless explicitly requested.

### 4. Context and Tool Budget
- Read the closest implementation and configuration first. Keep a short evidence map of
  files already read; do not read an unchanged file twice in the same task.
- Start with targeted searches and compact tool responses. Load at most two routed skills
  initially; add another only when a concrete uncertainty requires it. Never load the full
  pattern library.
- First-pass work should normally finish in 2-4 tool calls. Medium work should aim for
  5-10 calls. High effort must reassess every 8 calls and stop at 24 unless the user
  requested an exhaustive audit or new evidence makes additional calls necessary.
- Before a fifth first-pass call, edit or state the concrete escalation reason. Once the requested
  edit succeeds, stop; do not continue with exploratory reads, broad checks, cleanup, or unrelated
  fixes. Focused validation belongs to medium/high work or an explicit user request.
- Never repeat a tool call with identical arguments after it succeeds or returns a stable
  error. Reuse the result. After two failed approaches with the same blocker, change the
  approach or report the blocker instead of looping.
- Search once with grouped patterns, inspect only matching ranges, and broaden gradually.
  Do not request full output merely to avoid choosing fields, filters, files, or a model.
- Never recursively scan an Odoo checkout, shared base source, or addons collection during
  ordinary custom-addon work. Resolve uncertainty with the exact inherited symbol/file; broad
  source scans require an explicit audit scope.

### 5. Enforcement Boundary
- These rules guide model behavior; they cannot guarantee it. Gemini 3.7/3.8 may still produce
  heavy tool loops at low effort. Odoo Boost can enforce limits only
  on calls routed through its MCP server, including tool exposure, response caps, and repeated-call
  guards. Native editor file operations, searches, shell commands, tests, model turns, and total
  per-task tool calls remain outside Odoo Boost's visibility and control.
