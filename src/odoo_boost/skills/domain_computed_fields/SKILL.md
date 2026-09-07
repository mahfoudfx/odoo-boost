---
name: Computed Fields & Cache Invalidation
description: Writing robust computed fields, inversions, search methods, and cache-safe dependency trees.
globs: ["models/**/*.py"]
---

# Computed Fields & Cache Invalidation

Computed fields calculate their value dynamically via a Python method. Correct dependencies and complete assignment are essential to avoid cache misses and infinite recomputation loops.

## 1. Stored vs Non-Stored Compute Fields
- **Non-stored (`store=False` default)**:
  - Calculated on-demand when accessed by the view or code.
  - Cannot be searched or ordered in database queries unless a `search=` or `order=` method is defined.
- **Stored (`store=True`)**:
  - Saved in the PostgreSQL database table.
  - Recomputed automatically only when one of the fields declared in `@api.depends(...)` changes.
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
```python
class ResPartner(models.Model):
    _inherit = "res.partner"

    full_address = fields.Char(
        compute="_compute_full_address",
        inverse="_inverse_full_address",
        search="_search_full_address",
    )

    def _inverse_full_address(self):
        """Allows writing to a computed field."""
        for partner in self:
            if partner.full_address:
                parts = partner.full_address.split(",")
                partner.street = parts[0].strip() if parts else False

    def _search_full_address(self, operator, value):
        """Allows searching against non-stored compute fields."""
        return [
            "|",
            ("street", operator, value),
            ("city", operator, value),
        ]
```
