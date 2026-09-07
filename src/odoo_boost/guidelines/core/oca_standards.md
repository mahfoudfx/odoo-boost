## Odoo Community Association (OCA) Standards

### 1. General Principles
- **PEP 8 & DRY & KISS**: Follow PEP 8 formatting, keep code simple, modular, and reusable.
- **Explicit over Implicit**: Explicitly specify dependencies, domains, and field definitions.
- **No Direct SQL Execution**: Always prefer Odoo ORM methods. Never use raw SQL queries when ORM methods can achieve the result. If raw SQL is unavoidable, always use parameterized queries to prevent SQL injection (`self.env.cr.execute("SELECT id FROM res_partner WHERE name = %s", (name,))`).
- **Never Commit Transactions**: Never execute `self.env.cr.commit()` inside module code. Transactions must always be managed by the Odoo framework.

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
- Every new model must have an entry in `security/ir.model.access.csv`.
- Never use `sudo()` to bypass security checks unless strictly required (e.g. public portal actions or low-level background tasks). Always restrict the scope of `sudo()`: `self.sudo().read(...)` instead of converting the entire recordset.
- When multi-company rules are needed, define record rules with `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]`.

### 4. Manifest & File Layout
- Manifest keys:
  - `name`: Short, clear module title.
  - `version`: Version format `<odoo_major>.0.x.y.z` (e.g. `18.0.1.0.0`).
  - `category`: Valid Odoo category.
  - `license`: Explicit open source license, e.g. `'LGPL-3'` or `'AGPL-3'`.
  - `depends`: List only direct dependencies.
  - `data`: Views, security, data files in strict dependency order (security first, views second, menus last).
