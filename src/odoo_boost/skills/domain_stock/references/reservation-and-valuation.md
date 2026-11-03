# Reservation and valuation decisions

The concrete configuration examples below were checked against Odoo 18 official
documentation. Select matching implementation and configuration before using them
on another release. These are design and verification criteria, not an executable
stock-processing recipe.

## Reservation timing is an operation policy

Read the operation type's reservation method before treating an unreserved
transfer as a defect. Odoo 18 documents reservation at confirmation, manually,
or before the scheduled date. On-hand availability alone does not establish that
stock has been reserved for an order. Scheduled reservation also has a separate
lead window for starred transfers; test time boundaries with controlled dates.

For competing orders, verify allocation before and after unreservation and
reassignment. Record company, location, tracking, packaging and priority policy.
Preserve standard assignment behavior instead of manufacturing reservations with
arbitrary quant writes. Concurrency correctness requires database tests.

## Packaging and removal answer different questions

In the documented full-packaging example, an order for 24 units in 12-unit
packagings with only 22 units available reserves 12 units under full-only policy
and 22 under partial policy. A mismatch between available and reserved quantities
can therefore be intentional. Backorder handling remains a separate decision.

Removal strategy chooses physical stock: incoming date, expiry/removal date,
location sequence or package selection. Costing method determines valuation.
Inspect these independently even when both settings use the label FIFO. Odoo 18
documents that category force-removal policy takes priority over location policy.
Its closest-location strategy uses location ordering; do not assume measured
physical travel distance from the name.

## Valuation, accounting and selling price are separate outcomes

Record costing method, valuation policy, company, accounting mode and relevant
accounts before changing the standard flow. Measure moved quantities, valuation
evidence and accounting entries separately. Newer releases can change the timing
of accounting valuation; use the parent skill's version boundaries.

Landed costs allocate additional costs to product valuation. They are not a
general instruction to modify the sales price. The Odoo 18 docs describe split
methods by quantity, current cost, weight, volume or equal allocation, each with
different business meaning. Verify input dimensions and rounding, and compare
the allocated total with the charge before validation.

The reviewed book requires automated valuation for landed costs, while the pinned
Odoo 18 landed-cost documentation says manual or automatic valuation is possible
with AVCO/FIFO. Treat eligibility as a target-source question and inspect the
installed landed-cost module before imposing or removing a restriction. This
reference does not certify that configuration combination by runtime execution.

## Runtime scenarios to record

| Scenario | Evidence to compare |
|---|---|
| Two orders competing for limited stock | Allocation by order; unreserve/reassign; no over-allocation |
| Full versus partial packaging | Available, reserved, moved and backordered quantities |
| Category versus location removal | Selected lots/packages/locations and effective policy |
| FIFO/AVCO receipts, delivery and return | Quantity, value, costing evidence and configured accounting effect |
| Landed-cost allocation | Charge, split inputs, allocated sum, valuation adjustment and unchanged/explicitly managed pricing policy |

## Official evidence

Pinned Odoo 18 documentation revision: `ca129a822019682bd32552e4cbabba2520d1308e`.

- [Reservation methods](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/shipping_receiving/reservation_methods.rst)
- [Packaging and partial reservation](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/product_management/configure/packaging.rst)
- [Removal strategies](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/shipping_receiving/removal_strategies.rst)
- [Landed costs](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/landed_costs.rst)
