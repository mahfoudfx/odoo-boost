---
name: Odoo Code Review
description: Comprehensive code review checklist covering OCA standards, SQL safety, ORM anti-patterns, security, and performance.
globs: ["**/*.py", "**/*.xml", "security/*.csv"]
---

# Odoo Code Review Checklist

This skill provides a rigorous review methodology for Odoo addons, ensuring compliance with OCA guidelines, performance best practices, and security safeguards.

## 1. Security & Access Rights
- **Missing ACLs**: Every non-transient model (`models.Model`) must have read/write/create/unlink permissions defined in `security/ir.model.access.csv`.
- **`sudo()` Misuse**:
  - Flag any unbounded `self.sudo()`.
  - Ensure `sudo()` is restricted in scope: prefer `self.sudo().read(...)` or `self.env['model'].sudo().search(...)` only when bypassing user restrictions is strictly justified.
  - Never let client input dictate `sudo()` execution without authentication/authorization checks.
- **Direct SQL & Injection**:
  - Forbid `self.env.cr.execute(f"SELECT ... {variable}")`.
  - All SQL parameters must use parameterized tuples: `self.env.cr.execute("SELECT ... WHERE id = %s", (record_id,))`.
- **Transaction Tampering**:
  - Forbid `self.env.cr.commit()` or `self.env.cr.rollback()` in module logic unless running standalone batch background scripts.

## 2. ORM Performance & Efficiency
- **N+1 Query Detection**:
  - Avoid searches or queries inside loops:
    ```python
    # BAD: N queries
    for partner in partners:
        orders = self.env["sale.order"].search([("partner_id", "=", partner.id)])

    # GOOD: 1 batched query
    orders = self.env["sale.order"].search([("partner_id", "in", partners.ids)])
    ```
- **Mapped and Filtered**:
  - Use recordset operations: `records.mapped('field')`, `records.filtered(lambda r: r.state == 'done')`.
- **Batch Processing**:
  - `write()`, `create()`, and `unlink()` should be called on recordsets, not iteratively in a `for` loop.

## 3. Method Conventions & Decorators
- **`@api.depends` Completeness**:
  - All relational sub-fields traversed must be explicitly listed in `@api.depends('order_id.partner_id.country_id')`.
  - Ensure **every branch** in compute methods sets the target field to avoid `CacheMiss` errors:
    ```python
    @api.depends("value")
    def _compute_result(self):
        for rec in self:
            rec.result = rec.value * 2 if rec.value else 0
    ```
- **`@api.constrains`**:
  - Always raise `odoo.exceptions.ValidationError` with translated string `_("...")`.
- **`@api.onchange`**:
  - Check if `@api.depends` with stored/non-stored compute should be used instead. Onchange does not trigger during RPC/automated operations.

## 4. Multi-Company Compliance
- **Company Field Consistency**:
  - Ensure models with company dependencies have `company_id = fields.Many2one('res.company', ...)` and `check_company=True` on relational fields.
- **Record Rules**:
  - Verify multi-company record rule domain format: `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]`.

## 5. Views and XML
- **List vs Tree**: For Odoo 18+, ensure `<list>` is used instead of deprecated `<tree>`.
- **Search View Attributes**: Ensure no `string` or `expand` attributes on `<group>` inside search views (v18+).
- **Inline Expressions**: Ensure `invisible="state != 'draft'"` instead of `attrs="{'invisible': ...}"`.
