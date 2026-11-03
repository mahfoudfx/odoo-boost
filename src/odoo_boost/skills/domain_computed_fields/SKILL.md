---
name: domain-computed-fields
description: Writing robust computed fields, inversions, search methods, and cache-safe dependency trees.
globs: ["models/**/*.py"]
---

# Computed Fields & Cache Invalidation

Computed fields calculate their value dynamically via a Python method. Correct dependencies and complete assignment are essential to avoid cache misses and infinite recomputation loops.

## 1. Stored vs Non-Stored Compute Fields
- **Non-stored (`store=False` default)**:
  - Calculated on-demand when accessed by the view or code.
  - Can support domain searches through `search=`. A `search` method alone does not make the field SQL-sortable; there is no field `order=` callback. Odoo 20 source also supports SQL-backed computation (`compute_sql`), which requires a separate API/security review.
- **Stored (`store=True`)**:
  - Saved in the PostgreSQL database table.
  - Recomputed through ORM dependency tracking; creation and explicit recomputation also matter. Declare every source field, including relational paths.
  - Can be indexed and filtered in standard ORM search queries.

## 2. Complete Assignment Invariant
Every code path inside a compute method must assign a value to **every record** in `self`:

```python
from odoo import api, fields, models


class OrderLine(models.Model):
    _name = "order.line"
    _description = "Order Line"

    price_unit = fields.Float()
    quantity = fields.Float()
    discount = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal", store=True)

    @api.depends("price_unit", "quantity", "discount")
    def _compute_subtotal(self):
        for line in self:
            if line.quantity and line.price_unit:
                line.subtotal = (line.price_unit * line.quantity) * (
                    1 - (line.discount or 0.0) / 100.0
                )
            else:
                line.subtotal = 0.0  # MUST assign on else branch too!
```

## 3. Inverse and Search Methods

An inverse updates source fields so the computed result matches the edited value.
Define behavior for empty input, rounding and ambiguous inversions. A search method
must return the domain equivalent to the requested operation; OR-ing searches on
parts of a concatenated address does not implement exact or negative searches on
the full address. Implement supported operators explicitly and verify equivalence.
See the linked pattern reference for the decision procedure.

## 4. Cache, Access, and Verification
- For non-stored values that vary by user, company, or context, declare relevant
  `@api.depends_context` keys as supported by the target version.
- Empty `@api.depends()` does not provide a clock or external-event trigger.
  Decide how time-sensitive values refresh and test that boundary explicitly.
- Check `compute_sudo` and related-field access against the intended reader.
- Keep separate inverse methods when fields must not share inverse protection.
- Verify multi-record computation, empty relations, source-field edits, inverse
  round trips, and search-domain equivalence, including negative operators.
- For worked patterns and source links, read
  `../pattern-library/references/computed-field-patterns.md`.
