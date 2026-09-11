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

### 2. Execution Boundaries: Code Authoring vs. Live Commands
- **Code Authoring (Default):** The agent's core responsibility is writing clean, idiomatic code and modifying files.
- **No Unsolicited Live Commands:** Do **not** automatically execute `odoo-bin` module upgrades (`-u`), reboot running servers/daemons, or run verification scripts in `odoo shell` unless the user explicitly asks (e.g. *"upgrade the module"*, *"test this in db"*, *"run verification"*).
- **No Unsolicited Automated Tests:** Do not generate or execute automated tests unless explicitly instructed.

### 3. Scope Restraint
- Only edit the files, models, and records relevant to the request.
- Avoid re-authoring or generating massive translation catalogs or auxiliary files unless explicitly requested.
