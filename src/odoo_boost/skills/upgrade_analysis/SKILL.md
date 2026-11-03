---
name: upgrade-analysis
description: Systematic migration and upgrade analysis for Odoo addons between versions (v14 to v20).
globs: ["**/*.py", "**/*.xml", "__manifest__.py"]
---

# Odoo Upgrade & Migration Analysis

This skill guides migration analysis and refactoring across Odoo versions from v14 through v20.

## Common Upgrade Patterns Matrix

| Feature / Pattern | v14 - v16 | v17 | v18 | v19 | v20 |
|---|---|---|---|---|---|
| List view tag | `<tree>` | `<tree>` | `<list>` | `<list>` | `<list>` |
| Dynamic attributes | `attrs` / `states` | Inline expressions | Inline expressions | Inline expressions | Inline expressions |
| Search view `<group>` | `expand` / `string` | Supported | Supported | Removed | Removed |
| Relational commands | Tuples; `Command` from v15 | `Command` | `Command` | `Command` | `Command` |
| Dynamic domain composition | Verify target | Verify target | Verify target | `fields.Domain` | `fields.Domain` |
| Python runtime | Check deployment | 3.10+ | 3.10+ | 3.10+ | 3.12–3.14 |
| Web client framework | Legacy/Owl mix | Owl 2 | Inspect target source | Inspect target source | Inspect target source |
| Access metadata | Separate ACL/rules | Separate ACL/rules | Separate ACL/rules | Separate ACL/rules | Unified `ir.access` |
| Cron progress | Verify target | Verify target | `_notify_progress` | `_commit_progress` | `_commit_progress` |

## Migration Steps Checklist

### 1. Views & XML Refactoring
- **Replace `<tree>` with `<list>`**:
  ```xml
  <!-- OLD (<= 17) -->
  <record id="view_partner_tree" model="ir.ui.view">
      <field name="arch" type="xml">
          <tree string="Partners">...</tree>
      </field>
  </record>

  <!-- NEW (>= 18) -->
  <record id="view_partner_tree" model="ir.ui.view">
      <field name="arch" type="xml">
          <list string="Partners">...</list>
      </field>
  </record>
  ```
- **Eliminate `attrs` when migrating to Odoo 17+**:
  Convert `attrs="{'invisible': [('state', '=', 'done')], 'readonly': [('is_locked', '=', True)]}"`
  to direct inline expressions: `invisible="state == 'done'" readonly="is_locked"`.
- **Clean Search View `<group>` tags when migrating to Odoo 19**:
  Remove `expand="..."` and `string="..."` from `<group>` tags inside `<search>` definitions.

### 2. Python & ORM Modernization
- **Use `Command` constants in Python on Odoo 15+**:
  ```python
  from odoo.fields import Command

  # Replace [(0, 0, vals)] -> Command.create(vals)
  # Replace [(4, id)]        -> Command.link(id)
  # Replace [(5, 0, 0)]      -> Command.clear()
  # Replace [(6, 0, ids)]    -> Command.set(ids)
  ```
- **Audit `self.env.cr`**:
  - Replace `cr.commit()` or manual cursor management.
  - Flush the relevant fields before SQL reads in any supported series where
    pending ORM writes affect the query; use the target API and narrow the flush
    where practical. SQL writes also need cache/dependency handling.

### 3. Manifest Upgrades
- Update version prefix for the target series, for example `20.0.1.0.0`.
- Verify external Python dependencies support the deployment Python version.
- Check if upstream base modules have been merged, renamed, or deprecated.

For unregistered versions, verify the target source and documentation instead of extrapolating this matrix. JSON-RPC controller routes change from `type="json"` to `type="jsonrpc"` in Odoo 19. Odoo 20 bearer routes require `bearer_scope`; load the v20 note before applying its newer APIs.

## OCA addon migration

When porting an OCA addon, record the source and target series, repository,
module, target branch, and any existing migration issue or PR before changing
files. Apply the relevant compatibility notes for **each** intervening Odoo
major version; a direct jump can miss an intermediate API removal. Follow the
repository's migration conventions and preserve original authorship and
copyright notices. Keep compatibility changes separate from unrelated feature
work where practical. Check the manifest version and dependencies, data/XML
load order, security files, tests, and OCA metadata against the target branch.
Use the repository's documented test command and database setup before any
live install or upgrade; the operating rules require explicit authorization
for database-touching commands.


## Existing-data upgrades

For field conversions, renamed records/external IDs, `noupdate` changes, or data
upgrade scripts, read [data upgrade procedure](references/data-upgrades.md).
Record the installed/target module versions, phase, selected scripts, conversion
policy, and validation on representative existing rows. Clean-install success
and syntax changes alone do not establish data-upgrade correctness.


The systematic audit covers 15, 17, 18, 19 and 20. Matrix entries for 14/16
retain prior guidance and are not a new certification for those versions. For
20 access migration, translate group grants and global restrictions deliberately;
old CSV columns and rule `perm_*` flags are not interchangeable with `ir.access`.
For stock/UoM, fiscal positions and chatter, load the corresponding domain skill
version table before porting. Changes to data semantics need regression checks
beyond replacing API names.
