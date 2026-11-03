# Computed Field Patterns

Use this reference for derived values, custom searches, inverse methods, and
recomputation problems. Apply the configured version's ORM API.

## Choose persistence and dependencies

Use a non-stored field for values calculated on access. Use a stored field when
SQL sorting, indexing, or repeated reads justify recomputation and storage costs.
A custom `search` method enables domain searches without storing the value; it
must return a domain equivalent to the requested operator and value. There is no
field `order` callback for sorting a non-stored value. In Odoo 20, verified
source also supports `compute_sql`; that is a distinct SQL-backed computation
API, not a consequence of defining `search`. Inspect its access contract first.

Declare all field inputs, including dotted relational dependencies. A dependency
on `partner_id` alone does not describe changes to `partner_id.name`. Context
inputs to non-stored computes need `depends_context` where supported. Time and
external services require an explicit refresh strategy; an empty `depends()`
decorator does not make a cached value refresh continuously.

## Complete assignment

Assign every output on every branch, for every record. This original example
uses only the model's own fields and supports a batch recordset:

```python
from odoo import api, fields, models


class PlanningAllocation(models.Model):
    _name = "planning.allocation"
    _description = "Planning Allocation"

    hours = fields.Float()
    hourly_cost = fields.Float()
    estimated_cost = fields.Float(compute="_compute_estimated_cost", store=True)

    @api.depends("hours", "hourly_cost")
    def _compute_estimated_cost(self):
        for allocation in self:
            allocation.estimated_cost = allocation.hours * allocation.hourly_cost
```

Keep compute methods free of unrelated writes. For relational aggregates, include
child value changes and relation membership changes in verification. Batch
aggregation queries where profiling shows repeated queries per record.

## Search and inverse semantics

An inverse writes the source values needed to reproduce an edited result. Define
what happens for zero denominators, rounding, and ambiguous inversions. Separate
inverse methods avoid surprises from protected fields during inverse execution.
Computed fields can be editable through an inverse even when non-stored.

A search over concatenated text is not generally equivalent to OR-ing searches
on its component fields, especially for equality and negative operators. A tax
search cannot divide by a constant when each record has its own tax rate.
Implement the full supported semantics or reject unsupported operations; an
empty domain silently matches everything.

## Access and freshness

Review elevated computation and related fields for data exposure. User-specific
results must not become shared stored values. Stored currency conversions need a
policy for rate changes as well as dependencies on amount, currencies, company,
and conversion date. Age and overdue values need a day-boundary refresh policy.

## Verification

Check empty values, multiple records, each dependency edit, relation removal,
inverse round trips, and equivalent positive and negative searches. Repeat
permission-sensitive reads as the intended user and company. Reload records to
check persistence; inspect query counts before optimizing.

## Primary reference

The [Odoo 18 ORM reference](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/orm.rst)
describes computed fields, dependencies, inverse protection, and cache handling.
Use the matching branch for other Odoo versions. This file is an independently
written synthesis; it does not require local book files.


## Version boundaries

The compute/inverse/search contract was compared in official 15/17/18/19/20 ORM
references. SQL cache examples differ: Odoo 15 documents `invalidate_cache`, while
17/18/19/20 document `invalidate_recordset` plus `modified` for dependency
notification. Choose the target API before adapting low-level SQL examples.
`Field._get_attrs` in the five corresponding official source branches confirms
ordinary compute elevation defaults follow storage and related computes default
to elevated access. Set `compute_sudo` deliberately rather than copying a default
claim from prose.
