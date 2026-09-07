---
name: Multi-Company Domain Patterns
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

## 2. Multi-Company Record Rule
Define a record rule so users only see records from their currently active allowed companies:

```xml
<record id="custom_record_comp_rule" model="ir.rule">
    <field name="name">Custom Record Multi-Company</field>
    <field name="model_id" ref="model_custom_record"/>
    <field name="global" eval="True"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
</record>
```
*Note: `company_ids` is evaluated by Odoo at runtime against `self.env.companies.ids`.*

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
company = self.env["res.company"].browse(1)
records = self.with_company(company).env["custom.record"].search([])
```
