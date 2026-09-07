# MCP Tools Reference

Odoo Boost provides 22 MCP tools that give your AI agent deep introspection into a running Odoo instance as well as local addons.

All tools return JSON strings.

---

## 1. application_info

Get Odoo application info: server version, installed modules, database details.

**Parameters:** None

**Returns:**
```json
{
  "server_version": "18.0",
  "server_serie": "18.0",
  "protocol_version": 1,
  "installed_modules_count": 147,
  "installed_modules": [
    { "name": "account", "description": "Invoicing", "version": "18.0.2.0.0" }
  ]
}
```

---

## 2. database_schema

Get the field definitions (schema) of an Odoo model.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | yes | — | Technical model name, e.g. `res.partner` |

**Returns:**
```json
{
  "model": "res.partner",
  "name": "Contact",
  "field_count": 212,
  "fields": [
    {
      "name": "name",
      "label": "Name",
      "type": "char",
      "relation": null,
      "required": true,
      "readonly": false,
      "stored": true,
      "indexed": true,
      "help": null
    }
  ]
}
```

---

## 3. database_query

Execute an ORM `search_read` on any Odoo model. Safe — goes through Odoo access rights. Supports an optional `compact` mode to preserve AI token context.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | str | yes | — | Technical model name |
| `domain` | str | no | `"[]"` | Odoo domain as JSON string |
| `fields` | str | no | `"[]"` | JSON list of field names. Empty for all |
| `limit` | int | no | `80` | Max records to return |
| `offset` | int | no | `0` | Records to skip |
| `order` | str | no | `""` | Sort order, e.g. `"name asc"` |
| `compact` | bool | no | `false` | When true, strips false/null values and uses compact JSON |

**Returns:**
```json
{
  "model": "res.partner",
  "total_count": 523,
  "returned_count": 5,
  "offset": 0,
  "limit": 5,
  "records": [
    { "id": 1, "name": "My Company", "email": "info@example.com" }
  ]
}
```

---

## 4. aggregate_records

Perform server-side `read_group` aggregations (e.g. sums, counts, averages, and group-bys) without fetching thousands of individual records.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | str | yes | — | Model name, e.g. `sale.order` |
| `fields` | str | yes | — | JSON list of fields to aggregate, e.g. `["amount_total:sum", "partner_id"]` |
| `groupby` | str | yes | — | JSON list of groupby fields, e.g. `["partner_id", "date_order:month"]` |
| `domain` | str | no | `"[]"` | Domain filter as JSON string |
| `limit` | int | no | `80` | Max groups to return |
| `offset` | int | no | `0` | Groups to skip |
| `order` | str | no | `""` | Order string, e.g. `"amount_total desc"` |

**Returns:**
```json
{
  "model": "sale.order",
  "group_count": 3,
  "groups": [
    {
      "partner_id": [12, "Deco Addict"],
      "amount_total": 4520.50,
      "partner_id_count": 4
    }
  ]
}
```

---

## 5. resolve_xml_id

Resolve an external ID (`ir.model.data` XML ID like `base.main_company` or `account.view_move_form`) to its underlying database ID, model, and metadata.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `xml_id` | str | yes | — | Fully qualified XML ID (`module.name`) or local ID |
| `module` | str | no | `""` | Optional module name if not included in `xml_id` |

**Returns:**
```json
{
  "found": true,
  "xml_id": "base.main_company",
  "module": "base",
  "name": "main_company",
  "model": "res.company",
  "res_id": 1,
  "noupdate": true
}
```

---

## 6. get_model_inheritance

Inspect an Odoo model's inheritance hierarchy, including `_inherit` extension chains, `_inherits` delegation pointers, and parent models.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | yes | — | Technical model name, e.g. `product.product` |

**Returns:**
```json
{
  "model": "product.product",
  "name": "Product Variant",
  "inherit": ["mail.thread", "mail.activity.mixin"],
  "inherits": {
    "product.template": "product_tmpl_id"
  }
}
```

---

## 7. inspect_local_addon

Fast, sub-50ms offline static scanner. Uses Python's standard `ast` and `xml.etree` libraries to inspect uncommitted or local addon directories without needing Docker or a live database.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `addon_path` | str | yes | — | Path to the local addon directory |

**Returns:**
```json
{
  "addon_name": "custom_sales",
  "models": [
    {
      "model_name": "custom.order",
      "inherits": ["mail.thread"],
      "field_names": ["name", "order_date", "line_ids"],
      "file": "models/custom_order.py"
    }
  ],
  "xml_elements": [
    {
      "tag": "record",
      "id": "view_custom_order_form",
      "model": "ir.ui.view",
      "file": "views/order_views.xml"
    }
  ],
  "manifest_info": {
    "name": "Custom Sales",
    "version": "18.0.1.0.0",
    "depends": ["sale", "mail"]
  }
}
```

---

## 8. resolve_local_xml_id

Find and locate where an XML ID is declared or referenced within local addon files on disk.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `xml_id` | str | yes | — | XML ID to locate (e.g. `view_order_form`) |
| `directory` | str | no | `"."` | Root directory to search within |

**Returns:**
```json
{
  "xml_id": "view_custom_order_form",
  "matches": [
    {
      "file": "views/order_views.xml",
      "line": 4,
      "tag": "record",
      "type": "declaration"
    }
  ]
}
```

---

## 9. lint_odoo_code

Lint an Odoo module or file against OCA standards. Uses `pylint-odoo` if installed, or falls back to an intelligent built-in AST safety scanner (checking for missing ACLs, SQL injections, `self.env.cr.commit()`, and deprecated `<tree>` tags).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | yes | — | File or directory path to lint |

**Returns:**
```json
{
  "path": "addons/custom_sale",
  "tool": "pylint-odoo",
  "passed": false,
  "issues_count": 1,
  "issues": [
    {
      "file": "models/order.py",
      "line": 42,
      "symbol": "sql-injection",
      "message": "Possible SQL injection using string formatting"
    }
  ]
}
```

---

## 10. check_odoo_ls

Check if the official Odoo Language Server (`odoo-ls`) is installed, executable, and available in your environment.

**Parameters:** None

**Returns:**
```json
{
  "available": true,
  "path": "/usr/local/bin/odoo-ls",
  "version": "odoo-ls 0.1.0"
}
```

---

## 11. list_models

List available Odoo models with field counts.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filter_name` | str | no | `""` | Substring filter on model name |
| `filter_module` | str | no | `""` | Filter by source module name |
| `limit` | int | no | `200` | Max models to return |

---

## 12. list_views

List Odoo views (`ir.ui.view`), optionally filtered by model or type. Returns the full XML architecture.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | no | `""` | Filter by model name |
| `view_type` | str | no | `""` | Filter by type: `form`, `list`, `kanban`, `search`, etc. |
| `limit` | int | no | `50` | Max views to return |

---

## 13. list_menus

List Odoo menu items (`ir.ui.menu`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `parent_id` | int | no | `0` | `0` = root menus only, `-1` = all menus, or a specific parent ID |
| `limit` | int | no | `200` | Max menus to return |

---

## 14. list_routes

List website pages and known controller routes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filter_url` | str | no | `""` | Substring filter on URL |
| `limit` | int | no | `100` | Max routes to return |

---

## 15. list_access_rights

List access rights (`ir.model.access`) and record rules (`ir.rule`) for a model.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | no | `""` | Filter by model name. Empty for all |
| `limit` | int | no | `100` | Max entries per type |

---

## 16. get_config

Get Odoo system configuration parameters (`ir.config_parameter`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | no | `""` | Exact key or substring filter. Empty returns all |
| `limit` | int | no | `100` | Max parameters to return |

---

## 17. get_module_info

Get detailed information about an Odoo module including dependencies and defined models.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `module_name` | str | yes | — | Technical module name, e.g. `sale` |

---

## 18. search_records

Search and read records from any Odoo model with domain filtering and pagination (default limit 20).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | str | yes | — | Technical model name |
| `domain` | str | no | `"[]"` | Odoo domain as JSON string |
| `fields` | str | no | `"[]"` | JSON list of field names |
| `limit` | int | no | `20` | Max records to return |
| `offset` | int | no | `0` | Records to skip |
| `order` | str | no | `""` | Sort order |

---

## 19. execute_method

Execute an arbitrary ORM method on an Odoo model (similar to Laravel Tinker).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | str | yes | — | Technical model name |
| `method` | str | yes | — | Method name (e.g. `default_get`, `fields_get`) |
| `args` | str | no | `"[]"` | Positional arguments as JSON list |
| `kwargs` | str | no | `"{}"` | Keyword arguments as JSON object |

---

## 20. read_log_entries

Read Odoo log entries from `ir.logging`. Requires `log_db` to be configured in `odoo.conf`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `level` | str | no | `""` | Filter by level: `WARNING`, `ERROR`, `CRITICAL` |
| `func` | str | no | `""` | Filter by function name substring |
| `limit` | int | no | `50` | Max entries to return |

---

## 21. search_docs

Search Odoo documentation topics and return official documentation links.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | str | no | `""` | Topic keyword (e.g. `orm`, `views`, `owl`) |
| `version` | str | no | `""` | Odoo version, e.g. `18.0` |

---

## 22. list_workflows

List automated actions (`base.automation`) and server actions (`ir.actions.server`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | no | `""` | Filter by model name |
| `limit` | int | no | `50` | Max entries per type |

---

# MCP Resources Reference

Odoo Boost exposes native MCP resources that agents can query directly without making an active tool call round-trip.

| Resource URI | Description |
|---|---|
| `odoo://schema/{model_name}` | Dynamic template: returns the complete field schema for `{model_name}` (e.g. `odoo://schema/res.partner`). |
| `odoo://guidelines/oca` | Returns the composed OCA standards and best practices markdown document. |
| `odoo://skills/catalog` | Returns the `SKILLS_ROUTING.md` progressive skills catalog and intent index. |

---

# MCP Prompts Reference

Odoo Boost registers pre-engineered prompt workflows that users or agents can invoke to initiate structured development tasks.

### 1. `review_odoo_addon`
Pre-populates an architectural review prompt instructing the AI assistant to audit an Odoo addon at a specified path against OCA conventions, check `security/ir.model.access.csv`, and detect SQL injection or N+1 query patterns.

- **Arguments**:
  - `path` (string, required): Directory path of the addon to review.

### 2. `upgrade_odoo_addon`
Pre-populates an upgrade and migration analysis prompt instructing the AI assistant to check an addon for breaking changes, deprecated XML tags (e.g. `<tree>` vs `<list>`), obsolete `attrs`, and ORM updates for a target Odoo version.

- **Arguments**:
  - `path` (string, required): Directory path of the addon to analyze.
  - `target_version` (string, optional, default `"18.0"`): Target Odoo version (e.g. `"17.0"`, `"18.0"`, `"19.0"`).
