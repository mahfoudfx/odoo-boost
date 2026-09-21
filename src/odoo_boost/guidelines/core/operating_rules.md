## Agent Operating Rules & Boundaries

### 1. Workflow Modes: Fast Implementation vs. Plan & Walkthrough
- **Direct Implementation (Default - Fast & Token-Efficient):**
  - For targeted bug fixes, field/button additions, view/UI adjustments, method updates, security rule tweaks, or translation updates.
  - Implement directly by editing the target files immediately. Do **not** create `implementation_plan.md` or `walkthrough.md`.
- **Plan & Walkthrough (Deep Reasoning):**
  - Trigger a plan only for:
    1. Brand-new modules from scratch.
    2. **Refactoring actions** (restructuring classes/methods, moving logic between models/modules, reorganizing file layouts, or modifying inheritance hierarchies).
    3. Complex multi-model business logic redesigns or breaking database schema migrations.
    4. When explicitly requested by the user (e.g. *"plan this"*, `/plan`).

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
- Routine changes should normally finish within 8 tool calls. At 8 calls, stop and state
  what unresolved question justifies more investigation. Complex work may continue, but
  reassess every 8 calls and stop at 24 unless the user requested an exhaustive audit or
  new evidence makes the additional calls necessary.
- Never repeat a tool call with identical arguments after it succeeds or returns a stable
  error. Reuse the result. After two failed approaches with the same blocker, change the
  approach or report the blocker instead of looping.
- Search once with grouped patterns, inspect only matching ranges, and broaden gradually.
  Do not request full output merely to avoid choosing fields, filters, files, or a model.
