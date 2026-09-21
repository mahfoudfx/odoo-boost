---
name: domain-stock
description: Core patterns for warehouse management, pickings, moves, quants, and reservation logic.
globs: ["**/stock*.py", "**/models/*.py"]
---

# Odoo Stock & Inventory Domain Patterns

Odoo inventory tracks the physical and virtual movement of goods across internal, supplier, customer, and virtual locations.

## Core Hierarchy
1. `stock.warehouse`: Physical facility containing locations.
2. `stock.location`: Physical or virtual storage node (`usage`: `'internal'`, `'customer'`, `'supplier'`, `'inventory'`, `'transit'`).
3. `stock.picking`: The document/action transfer (e.g. Receipt, Internal Transfer, Delivery Order).
4. `stock.move`: Planned quantity transfer of a product between locations (`product_uom_qty`).
5. `stock.move.line`: Detailed execution lines with specific lot/serial numbers and tracked quantities (`quantity`).
6. `stock.quant`: Physical stock balances at a specific location for a product/lot.

## 1. Creating and Processing a Transfer
```python
from odoo import Command, models


class StockHelper(models.TransientModel):
    _name = "stock.helper"
    _description = "Stock Helper"

    def create_internal_transfer(self, product, qty, src_location, dest_location):
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "internal"),
                ("warehouse_id.company_id", "=", self.env.company.id),
            ],
            limit=1,
        )

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src_location.id,
                "location_dest_id": dest_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.display_name,
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                            "location_id": src_location.id,
                            "location_dest_id": dest_location.id,
                        }
                    ),
                ],
            }
        )

        # Confirm and reserve stock
        picking.action_confirm()
        picking.action_assign()

        # Set done quantities and validate
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True  # v17/v18 picking flow

        picking.button_validate()
        return picking
```

## 2. Invariants & Rules
- **Never write directly to `stock.quant`**:
  - Quants are updated automatically via confirmed and validated moves or inventory adjustment wizards. Manual edits to `quantity` in quants corrupt stock valuations.
- **Always respect `uom_id` vs `uom_po_id`**:
  - Inventory movements must use the base unit of measure (`product.uom_id`).
- **Valuation Integrity**:
  - In automated inventory valuation (`valuation == 'real_time'`), stock moves trigger automated journal entries in accounting upon validation. Never bypass the standard picking lifecycle.
