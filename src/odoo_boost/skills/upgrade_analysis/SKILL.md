---
name: Upgrade Analysis & Migration
description: Systematic migration and upgrade analysis for Odoo addons between versions (v14 to v19).
globs: ["**/*.py", "**/*.xml", "__manifest__.py"]
---

# Odoo Upgrade & Migration Analysis

This skill guides migration analysis and refactoring across Odoo versions from v14 through v19.

## Common Upgrade Patterns Matrix

| Feature / Pattern | v14 - v16 | v17 | v18 | v19 |
|---|---|---|---|---|
| List view tag | `<tree>` | `<tree>` (required) | `<list>` (required) | `<list>` (strictly enforced) |
| Dynamic attributes | `attrs="{'invisible': ...}"` | `invisible="cond"` | `invisible="cond"` | `invisible="cond"` |
| Search view `<group>` | `expand="0" string="..."` | Attributes supported | Attributes supported | RNG failure if `expand` or `string` present |
| Relational commands | Tuples in v14; `Command` available in v15–16 | `Command.create({...})` | `Command.create({...})` | `Command.create({...})` |
| Python runtime | Check target installation | 3.10+ | 3.10+ | 3.10+ |
| Web client framework | Legacy/Owl mix; Owl 2 web client in v16 | Owl 2 | Inspect target source | Inspect target source |

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
  from odoo import Command

  # Replace [(0, 0, vals)] -> Command.create(vals)
  # Replace [(4, id)]        -> Command.link(id)
  # Replace [(5, 0, 0)]      -> Command.clear()
  # Replace [(6, 0, ids)]    -> Command.set(ids)
  ```
- **Audit `self.env.cr`**:
  - Replace `cr.commit()` or manual cursor management.
  - In v19, use `self.env.flush_all()` prior to raw SQL reads if needed.

### 3. Manifest Upgrades
- Update version prefix: `18.0.1.0.0` or `19.0.1.0.0`.
- Verify external Python dependencies support the deployment Python version.
- Check if upstream base modules have been merged, renamed, or deprecated.

For unregistered versions, verify the target source and documentation instead of extrapolating this matrix. JSON-RPC controller routes change from `type="json"` to `type="jsonrpc"` in Odoo 19.
