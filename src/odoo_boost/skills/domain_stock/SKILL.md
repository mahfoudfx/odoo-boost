---
name: domain-stock
description: Core patterns for warehouse management, pickings, moves, quants, and reservation logic.
globs: ["**/stock*.py", "**/models/*.py"]
---

# Stock and Inventory Workflows

## Identify the operation

Distinguish a receipt, delivery, internal transfer, return, and inventory count.
Read the configured version's model and standard flow before selecting fields or
methods. `stock.picking` groups transfers, `stock.move` expresses demand,
`stock.move.line` carries execution detail, and `stock.quant` represents on-hand
balances by stock dimensions. Warehouses and locations define the physical and
virtual route; company, lot/serial, package and owner may affect the operation.

## Process transfers through standard behavior

1. Confirm operation type, company, source and destination, product, quantity and
   unit. Select an operation type explicitly; an arbitrary first search result
   need not represent the intended warehouse.
2. Create demand using the target version's supported relations and methods.
   Preserve standard confirmation and reservation behavior. Planned quantity,
   reserved quantity and actual movement are distinct facts.
3. Record what actually moved. Gather required lot/serial and package information.
   Inspect execution quantity fields in the target source; names and semantics
   differ across versions. Setting every planned quantity as completed is not a
   general-purpose automation strategy.
4. Validate through the normal workflow. Handle any required confirmation or
   backorder action and confirm the final transfer state; a method call alone
   does not establish completed movement.

## Counts, units and valuation

Use the supported inventory count/apply workflow for adjustments. A recorded count
is staged until applied; application produces traceable stock movement. Directly
mutating on-hand balances bypasses that workflow. Distinguish supported adjustment
inputs from internal quant maintenance APIs.

Know the unit associated with every quantity. Inventory tracking uses the product's
inventory unit; other documents may use a compatible unit. Use the configured
version's conversion and rounding helpers rather than treating purchase quantities
as stock quantities. Apply the version boundaries below before copying old fields.

Stock changes can affect valuation and accounting according to configuration and
version. Preserve the standard lifecycle and verify resulting valuation evidence;
do not infer a universal journal-entry timing rule across all versions from an
older example.

## Verified version boundaries

| API or workflow | 15 | 17 / 18 | 19 | 20 |
|---|---|---|---|---|
| Move-line execution fields | `qty_done`, separate reserved `product_uom_qty` | `quantity`, `picked` | `quantity`, `picked` | `quantity`, `picked` |
| Move-line unit relation | `product_uom_id` | `product_uom_id` | `product_uom_id` | `uom_id` |
| UoM structure | Categories and per-unit rounding | Categories and per-unit rounding | Reference-unit chain; Product Unit precision | Reference-unit chain; Product Unit precision |

The category restriction is verified for 15/17/18. The 19/20 source instead uses
`relative_uom_id` and `relative_factor`; stock lines restrict units through
`allowed_uom_ids`. Some 19/20 application text still mentions categories. Use the
matching model source for technical compatibility, including allowed-unit policy;
conversion arithmetic alone is not proof that two units suit a product.

Do not copy a 19 `uom.rounding` lookup into 20: the checked 20 source rounds through
Product Unit decimal precision. These field names identify porting boundaries,
not a recipe for marking all demand completed.

Count/apply adjustment remains documented in all five series, but labels and
technical methods differ. For valuation, 15/17/18 document automated movement
accounting; 19/20 document accounting valuation at invoicing/closing. Inspect the
company/category configuration and standard flow for the target series instead
of asserting that every validated movement immediately posts a journal entry.

## Verification

For competing orders, packaging reservations, removal strategies or landed-cost
changes, use the [reservation and valuation decision guide](references/reservation-and-valuation.md).

Check sufficient and insufficient availability, partial movement and backorder,
required tracking, return, unit conversion/rounding, and cross-company rejection.
For adjustments, compare count, applied movement, on-hand result and audit trail.
Use a disposable database with representative valuation configuration for runtime
checks; static parsing cannot prove reservation or valuation correctness.

## Official sources

Workflow principles were checked against local official 15/17/18/19/20
documentation; field and unit boundaries were checked in each official branch's
`addons/stock/models/stock_move_line.py` and `addons/uom/models/uom_uom.py`.
Inspect the exact deployed revision before executing technical operations.

- [Units of measure](https://github.com/odoo/documentation/blob/18.0/content/applications/inventory_and_mrp/inventory/product_management/configure/uom.rst)
- [Inventory counts and adjustments](https://github.com/odoo/documentation/blob/18.0/content/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.rst)
- [Lots](https://github.com/odoo/documentation/blob/18.0/content/applications/inventory_and_mrp/inventory/product_management/product_tracking/lots.rst)

Additional official sources:
- [UoM source, 19](https://github.com/odoo/odoo/blob/19.0/addons/uom/models/uom_uom.py)
- [UoM source, 20](https://github.com/odoo/odoo/blob/20.0/addons/uom/models/uom_uom.py)
- [Move-line source, 20](https://github.com/odoo/odoo/blob/20.0/addons/stock/models/stock_move_line.py)
- [Accounting valuation, 19](https://github.com/odoo/documentation/blob/19.0/content/applications/finance/accounting/get_started/inventory_valuation.rst)

Independently authored from verified workflow lessons; book files and example
addons are not required by this skill.
