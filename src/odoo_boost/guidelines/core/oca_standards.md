## Odoo Community Association (OCA) Standards

### 1. General Principles
- **PEP 8 & DRY & KISS**: Follow PEP 8 formatting, keep code simple, modular, and reusable.
- **Explicit over Implicit**: Explicitly specify dependencies, domains, and field definitions.
- **No Direct SQL Execution**: Always prefer Odoo ORM methods. Never use raw SQL queries when ORM methods can achieve the result. If raw SQL is unavoidable, always use parameterized queries to prevent SQL injection (`self.env.cr.execute("SELECT id FROM res_partner WHERE name = %s", (name,))`).
- **Transaction ownership**: Let Odoo commit or roll back the request transaction.
  Exceptional code that opens its own cursor must document why, handle rollback,
  and close that cursor. For cron progress, follow the target series' documented
  scheduler API rather than adding arbitrary commits to model methods.

### 2. Method Conventions & Decorators
- **Compute Methods**:
  - Name compute methods `_compute_<field_name>()`.
  - Always decorate compute methods with `@api.depends(...)`.
  - Always assign a value to the computed field for **every record** in `self` (including empty conditions) to prevent `CacheMiss` errors.
- **Constraint Methods**:
  - Name constraint methods `_check_<condition>()`.
  - Always decorate with `@api.constrains(...)`.
  - Always raise `odoo.exceptions.ValidationError` with translated messages `_("...")`.
- **Onchange Methods**:
  - Prefer compute fields (`compute=...`, `store=True`) over onchange methods whenever possible.
  - Onchange methods should only be used to suggest defaults or dynamic warning banners in the UI.

### 3. Security & Access Rights
- Every new persistent business model needs an intentional access policy. Select
  the target version's access model and CSV filename from the
  [module layout guide](module_structure.md); evaluate transient and abstract
  models separately.
- Never use `sudo()` to bypass security checks unless strictly required (e.g. public portal actions or low-level background tasks). Always restrict the scope of `sudo()`: `self.sudo().read(...)` instead of converting the entire recordset.
- For multi-company restrictions, choose shared or company-restricted record
  domains from the `domain-multi-company` skill and use the target access model.

### 4. Manifest & File Layout
- Manifest keys:
  - `name`: Short, clear module title.
  - `version`: Version format `<odoo_major>.0.x.y.z` (e.g. `18.0.1.0.0`).
  - `category`: Valid Odoo category.
  - `license`: Explicit open source license, e.g. `'LGPL-3'` or `'AGPL-3'`.
  - `depends`: List only direct dependencies.
  - `data`: Views, security, data files in strict dependency order (security first, views second, menus last).

### 5. Generated Documentation
- In repositories using `oca-gen-addon-readme`, update the applicable `readme/`
  fragments and run the configured generator to refresh `README.rst`.
- Preserve an existing `readme/CONTEXT.md` for the business need, chosen
  approach, and useful setup; add one only when that context helps maintainers.
- Follow the target series and repository configuration for manifests and
  assets; an upstream example template may target an older Odoo version.
