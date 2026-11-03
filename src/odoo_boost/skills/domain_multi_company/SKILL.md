---
name: domain-multi-company
description: Patterns and best practices for building multi-company aware models, record rules, and company-dependent fields.
globs: ["models/**/*.py", "security/**/*.xml"]
---

# Multi-Company Domain Patterns

Odoo supports single databases hosting multiple autonomous companies, sister subsidiaries, and branch entities.

## 1. Model Definition
When an entity belongs to a company, define `company_id` and enforce company consistency:

```python
from odoo import api, fields, models


class CustomRecord(models.Model):
    _name = "custom.record"
    _description = "Custom Record"
    _check_company_auto = True

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        check_company=True,  # Validates partner company matches this company
    )
```

## 2. Multi-Company Access Restriction
For 15/17/18/19, define an `ir.rule` so users only see records from their
currently enabled companies. The following XML is limited to those series:

```xml
<record id="custom_record_comp_rule" model="ir.rule">
    <field name="name">Custom Record Multi-Company</field>
    <field name="model_id" ref="model_custom_record"/>
    <field name="domain_force">
        [('company_id', 'in', company_ids)]
    </field>
</record>
```
*This model requires a company, so its rule is company-restricted. For an
intentionally shared model with optional `company_id`, allow both unset company
and enabled companies. A rule without groups is global. `company_ids` represents
the enabled companies, not just the main company.*

For the audited 20 branch, access declarations use `ir.access`. An equivalent
global restriction uses the enabled-company domain in the target access CSV:

```csv
id,name,model_id,group_id/id,operation,domain
custom_record_company,Custom Record company restriction,custom.record,,crud,"[('company_id', 'in', company_ids)]"
```

This restriction does not itself grant access. Define the intended group
permissions separately using the target version's access system. Read the
configured version's security guide before migrating declarations.

## 3. Company-Dependent Properties
For settings or configurations that vary by company without duplicating models:

```python
class ResPartner(models.Model):
    _inherit = "res.partner"

    custom_credit_limit = fields.Float(
        string="Credit Limit",
        company_dependent=True,
    )
```

## 4. Execution Context Switching
When operating across multiple companies in crons or automated actions:
```python
# Switch context to a specific company
# company is selected and authorized by the calling workflow.
model = self.env["custom.record"].with_company(company)
records = model.search([("company_id", "=", company.id)])
```


## 5. Consistency, Cache, and Verification

`with_company()` selects the main company for company-sensitive values; it does
not replace an explicit company domain when work must be confined to one company.
Keep normal access checks and validate the chosen company. `sudo()` can conceal
invalid cross-company relationships.

Use `check_company=True` on appropriate relations, together with
`_check_company_auto`; keep it off `company_id` itself. Review the strict behavior
for shared records before enabling it. Consistency checks and record rules serve
different purposes and both need verification.

For non-stored computes reading company-dependent values, declare the relevant
field dependencies and `@api.depends_context("company")`. Access such values under
the record's intended company. Use the ORM for company-dependent values; verify storage internals before
writing migrations that assume `ir.property` rows.

Test with company A as main, A and B enabled, a user restricted to A, and shared
records where supported. Check reads, creates, writes, defaults, and rejected
cross-company relations. Switch the main company and read the same record again
to catch cache/context mistakes.

## Version audit and sources

The context, company-consistency and shared/restricted-domain principles above
were checked in the official company howto for 15/17/18/19/20. The access
*declaration* differs in 20; domain semantics alone do not make an older XML
record portable. Company-dependent storage internals remain outside this skill's
verified contract; use public ORM behavior and verify migration assumptions.

- [Multi-company guidelines, 18](https://github.com/odoo/documentation/blob/18.0/content/developer/howtos/company.rst)
- [Multi-company guidelines, 20](https://github.com/odoo/documentation/blob/20.0/content/developer/howtos/company.rst)
- [Unified access model, 20](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_access.py)

Inspect the exact installed revision for overrides and storage/API details.
