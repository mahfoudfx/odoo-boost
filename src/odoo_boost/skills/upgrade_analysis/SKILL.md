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
| List view tag | `<tree>` | `<tree>` (deprecated) | `<list>` (required) | `<list>` (strictly enforced) |
| Dynamic attributes | `attrs="{'invisible': ...}"` | `invisible="cond"` | `invisible="cond"` | `invisible="cond"` |
| Search view `<group>` | `expand="0" string="..."` | `expand="0"` | Attributes ignored | RNG failure if `expand` or `string` present |
| Relational commands | `[(0, 0, {...})]` tuple format | `Command.create({...})` | `Command.create({...})` | `Command.create({...})` |
| Python runtime | 3.8 - 3.10 | 3.10+ | 3.10+ | 3.12+ |
| Web client framework | OWL 1 / Legacy widgets | OWL 2 | OWL 2 | OWL 3 |

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
- **Eliminate `attrs`**:
  Convert `attrs="{'invisible': [('state', '=', 'done')], 'readonly': [('is_locked', '=', True)]}"`
  to direct inline expressions: `invisible="state == 'done'" readonly="is_locked"`.
- **Clean Search View `<group>` tags**:
  Remove `expand="..."` and `string="..."` from `<group>` tags inside `<search>` definitions.

### 2. Python & ORM Modernization
- **Use `Command` constants**:
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
- Verify external Python dependencies are supported under Python 3.12+.
- Check if upstream base modules have been merged, renamed, or deprecated.
