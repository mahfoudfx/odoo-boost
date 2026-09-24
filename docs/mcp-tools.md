# MCP Tools Reference

Odoo Boost provides 23 MCP tools that give your AI agent deep introspection into a running Odoo instance as well as local addons.

All tools return JSON strings.

---

## Token efficiency (compact by default)

Broad listing tools return **compact** responses by default to keep agent
contexts small. Tools with `response_format` accept `"compact"` or `"full"`;
check the individual tool signature for full-output support.

| Tool | Compact (default) | Full |
|---|---|---|
| `list_views` | no `arch` XML; returns `arch_length`/`has_arch` | includes `arch` (use `view_id` for one view) |
| `inspect_local_addon` | manifest + counts + per-model field/method counts | full models, fields, methods, records, templates, menus |
| `application_info` | version + module count (no module list query) | module list (`include_modules=true`, paginated) |
| `database_schema` | name/type/relation/flags | adds label/help/indexed (`include_help=true`) |
| `execute_method` | capped by `max_response_chars` | uncapped result |
| `get_config` | values truncated (~200 chars), secrets redacted | full values (`reveal_secrets=true` for secrets) |
| `read_log_entries` | messages truncated (~500 chars) | full messages |
| `list_access_rights` | rule domains truncated when unfiltered | complete domains |
| `list_workflows` | code preview only | full server-action code |
| `get_module_info` | models capped (paginated) | all models |
| `search_records` | values verbatim (data fidelity) | — (opt-in `compact=true` to strip/truncate) |
| `list_models`, `list_menus` | paginated via `limit`/`offset` | same shape |

Targeted single-object queries (e.g. `list_views(view_id=…)`,
`inspect_local_addon(model=…)`) return full detail for the requested object.
`inspect_local_addon` accepts an exact addon directory by default and refuses a
recursive scan when that directory has no addon manifest. Broad collection or
Odoo-core audits require the explicit `allow_collection_scan=true` argument and
must still satisfy the configured filesystem boundary.

Global settings in `odoo-boost.json`: `compact_responses` (default `true`),
`max_response_chars` (default 40000, `0` disables), and `redact_config_secrets`
(default `true`). All 23 tools are registered; the agent client controls whether
tool definitions are loaded eagerly or discovered on demand; the MCP server
cannot require one behavior. Per-call `response_format` controls detail
where supported. Oversized responses are replaced by a bounded
`{ "truncated": true, "full_length": …, "preview": … }` envelope. Narrow the
query or increase `max_response_chars` to see more.

`cache_local_scans=true` reuses unchanged AST/XML addon scans. The cache key
tracks relevant paths, timestamps, and sizes, so edits invalidate it without a
manual refresh. `max_consecutive_identical_calls=2` blocks a third consecutive
call with the same tool and arguments; a different call resets the guard and
`0` disables it.

---

## Count-only queries

`count_records(model, domain="[]")` returns `{"model": ..., "count": ...}`
using one read-only ORM `search_count` call. Use it to check existence or size;
use `search_records` for actual records. Invalid JSON or a non-list domain
returns an error without calling Odoo. It respects Odoo access rules.

---

## 1. application_info

Get Odoo application info: server version, installed modules, database details. The module list is omitted in compact mode.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_modules` | bool | no | full mode | Include the installed module list |
| `module_filter` | str | no | `""` | Substring filter on module names |
| `limit` | int | no | `50` | Max modules to return |
| `offset` | int | no | `0` | Modules to skip |
| `response_format` | str | no | `"compact"` | `"compact"` or `"full"` |

**Returns (compact):**
```json
{
  "server_version": "18.0",
  "server_serie": "18.0",
  "protocol_version": 1,
  "installed_modules_count": 147
}
```

---

## 2. database_schema

Get the field definitions (schema) of an Odoo model.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | yes | — | Technical model name, e.g. `res.partner` |
| `field_name` | str | no | `""` | Substring filter on field name |
| `ttype` | str | no | `""` | Exact field type filter (e.g. `many2one`) |
| `limit` | int | no | `0` | Max fields (`0` = all) |
| `offset` | int | no | `0` | Fields to skip |
| `include_help` | bool | no | full mode | Include label/help/indexed metadata |
| `response_format` | str | no | `"compact"` | `"compact"` or `"full"` |

**Returns (compact):**
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

Compatibility alias for `search_records` with a default limit of 80 instead of 20. Both perform the same ORM `search_read`; use `search_records` for new calls. Odoo access rights apply.

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

Offline static scanner for uncommitted or local addon directories. It uses Python AST and hardened XML parsing without needing Docker or a live database.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `addon_path` | str | yes | — | Path to the local addon directory |
| `model` | str | no | `""` | Return one model in full detail |
| `xml_id` | str | no | `""` | Locate one XML ID declaration |
| `response_format` | str | no | `"compact"` | `"compact"` summary or `"full"` scan |

**Returns (compact):**
```json
{
  "addon_name": "custom_sales",
  "manifest": { "name": "Custom Sales", "version": "18.0.1.0.0", "depends": ["sale", "mail"] },
  "counts": { "models": 3, "records": 12, "templates": 2, "menuitems": 1 },
  "models": [
    { "_name": "custom.order", "field_count": 14, "method_count": 6, "file": "models/custom_order.py" }
  ]
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

Lint an Odoo module or file with `pylint-odoo` when installed. Its fallback AST scan reports Python syntax errors, direct cursor commits, and `name_get` definitions when the configured, registered Odoo version deprecates them. The fallback does not check ACL completeness, SQL injection, or XML view tags.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | yes | — | File or directory path to lint |

**Returns:**
```json
{
  "success": false,
  "engine": "ast-fallback",
  "total_issues": 1,
  "issues": [
    {
      "file": "models/order.py",
      "line": 42,
      "type": "error",
      "code": "E8102",
      "message": "Avoid calling cr.commit() directly."
    }
  ]
}
```

---

## 10. check_odoo_ls

Run the official `odoo_ls_server --parse` diagnostic mode on a local path and
return its JSON diagnostics. Odoo Boost detects the configured `odoo_ls_path`,
the executable on `PATH`, or its managed user-bin installation. Install the
latest stable binary directly from official `odoo/odoo-ls` release assets with:

```bash
odoo-boost odoo-ls install
odoo-boost odoo-ls status
```

Downloads happen only through this explicit command. The installer accepts
only the expected platform archive from the official GitHub repository and
installs it atomically. Use `--version 1.4.0` to pin a release and `--force` to
replace an existing managed binary.

Parameters: `path` (default `"."`) and `response_format` (`"compact"` or `"full"`).

**Returns:**
```json
{
  "installed": true,
  "binary": "/usr/local/bin/odoo-ls",
  "exit_code": 0,
  "diagnostic_count": 0,
  "diagnostics": [],
  "truncated": false,
  "response_format": "compact"
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

List Odoo views (`ir.ui.view`), optionally filtered by model or type. The XML `arch` is omitted by default.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | no | `""` | Filter by model name |
| `view_type` | str | no | `""` | Filter by type: `form`, `list`, `kanban`, `search`, etc. |
| `limit` | int | no | `20` | Max views to return |
| `offset` | int | no | `0` | Views to skip |
| `view_id` | int | no | `0` | Fetch exactly one view by ID |
| `include_arch` | bool | no | full mode | Include the XML `arch` |
| `response_format` | str | no | `"compact"` | `"compact"` or `"full"` |

---

## 13. list_menus

List Odoo menu items (`ir.ui.menu`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `parent_id` | int | no | `0` | `0` = root menus only, `-1` = all menus, or a specific parent ID |
| `limit` | int | no | `50` | Max menus to return |
| `offset` | int | no | `0` | Menus to skip |

---

## 14. list_routes

List `website.page` and `website.rewrite` ORM records. This does not enumerate Python controller routes. The result includes `complete` and `unavailable` fields when a model is missing or access is denied; connection failures surface as tool errors.

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
| `limit` | int | no | `50` | Max entries per type |
| `offset` | int | no | `0` | Entries to skip per type |
| `response_format` | str | no | `"compact"` | Unfiltered rule domains are truncated in compact mode |

---

## 16. get_config

Get Odoo system configuration parameters (`ir.config_parameter`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | no | `""` | Key filter. Empty returns all |
| `limit` | int | no | `20` | Max parameters to return |
| `offset` | int | no | `0` | Parameters to skip |
| `match` | str | no | `"ilike"` | `"ilike"` (substring) or `"exact"` |
| `reveal_secrets` | bool | no | `false` | Return secret values unredacted |
| `value_max_chars` | int | no | `0` in full | Truncate values (0 = no truncation) |
| `response_format` | str | no | `"compact"` | `"compact"` truncates values and redacts secrets |

---

## 17. get_module_info

Get detailed information about an Odoo module including dependencies and defined models.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `module_name` | str | yes | — | Technical module name, e.g. `sale` |
| `limit` | int | no | `50` | Max models to return |
| `offset` | int | no | `0` | Models to skip |
| `response_format` | str | no | `"compact"` | `"full"` returns all models |

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
| `compact` | bool | no | `false` | Strip empty values and truncate long strings |

---

## 19. execute_method

Execute a public ORM method on an Odoo model. With `readonly=true`, only known read and metadata methods are allowed; other public methods may mutate data when readonly is disabled. Odoo access rights still apply.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | str | yes | — | Technical model name |
| `method` | str | yes | — | Method name (e.g. `default_get`, `fields_get`) |
| `args` | str | no | `"[]"` | Positional arguments as JSON list |
| `kwargs` | str | no | `"{}"` | Keyword arguments as JSON object |
| `response_format` | str | no | `"compact"` | `"full"` bypasses the response budget |

---

## 20. read_log_entries

Read Odoo log entries from `ir.logging`. Requires `log_db` to be configured in `odoo.conf`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `level` | str | no | `""` | Filter by level: `WARNING`, `ERROR`, `CRITICAL` |
| `func` | str | no | `""` | Filter by function name substring |
| `limit` | int | no | `20` | Max entries to return |
| `offset` | int | no | `0` | Entries to skip |
| `entry_id` | int | no | `0` | Fetch a single entry by ID |
| `response_format` | str | no | `"compact"` | `"full"` returns untruncated messages |

---

## 21. search_docs

Look up curated official Odoo documentation links by topic and registered version, or search an installed offline text index. With `query` empty, this remains an offline link catalog. With `query` set, it returns up to three short excerpts from the configured, version-matched documentation cache, with local file/line and online page links; no network call occurs. See [offline documentation](offline-documentation.md) and [version support](versions.md).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | str | no | `""` | Topic keyword (e.g. `orm`, `views`, `owl`) |
| `version` | str | no | `""` | Odoo version, e.g. `18.0` |
| `query` | str | no | `""` | Search installed local documentation text; leaves link mode when empty. |
| `section` | str | no | `"all"` | `developer`, `administration`, `applications`, or `all`. |

---

## 22. list_workflows

List automated actions (`base.automation`) and server actions (`ir.actions.server`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | str | no | `""` | Filter by model name |
| `limit` | int | no | `25` | Max entries per type |
| `offset` | int | no | `0` | Entries to skip per type |
| `response_format` | str | no | `"compact"` | `"full"` returns complete server-action code |

---

# MCP Resources Reference

Odoo Boost exposes native MCP resources that agents can query directly without making an active tool call round-trip.

| Resource URI | Description |
|---|---|
| `odoo://schema/{model_name}` | Dynamic template: returns the complete field schema for `{model_name}` (e.g. `odoo://schema/res.partner`). |
| `odoo://guidelines/oca` | Returns the composed OCA standards and best practices markdown document. |
| `odoo://guidelines/oca/compact` | Returns only the guideline titles/headings as a compact index. |
| `odoo://skills/catalog` | Returns the `SKILLS_ROUTING.md` progressive skills catalog and intent index. |
| `odoo://project/context` | Returns a compact view of configured VENV, Odoo configuration, ordered addon roots, framework source, optional local docs, and MCP file-access status. Reads only `addons_path` from `odoo.conf`; no database call. |

---

# MCP Prompts Reference

Odoo Boost registers pre-engineered prompt workflows that users or agents can invoke to initiate structured development tasks.

### 1. `review_odoo_addon`
Pre-populates an architectural review prompt instructing the AI assistant to audit an Odoo addon at a specified path against OCA conventions, check `security/ir.model.access.csv`, and detect SQL injection or N+1 query patterns.

- **Arguments**:
  - `path` (string, required): Directory path of the addon to review.

### 2. `upgrade_odoo_addon`
Pre-populates a migration analysis prompt that asks the agent to verify view, ORM, and frontend changes against the target version.

- **Arguments**:
  - `path` (string, required): Directory path of the addon to analyze.
  - `target_version` (string, optional, defaults to configured `odoo_version`): Target Odoo version.
