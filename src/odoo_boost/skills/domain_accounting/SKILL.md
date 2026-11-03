---
name: domain-accounting
description: Core patterns for working with Odoo accounting models (account.move, account.move.line, taxes, reconciliation).
globs: ["**/account*.py", "**/models/*.py"]
---

# Odoo Accounting Domain Patterns

Working with financial data in Odoo requires adhering to double-entry bookkeeping invariants, balanced debits/credits, and currency rounding rules.

## Core Models Architecture
- `account.move`: The journal entry header (represents invoices, bills, manual journal entries).
  - `move_type`: `'entry'`, `'out_invoice'`, `'out_refund'`, `'in_invoice'`, `'in_refund'`, `'out_receipt'`, `'in_receipt'`.
- `account.move.line`: Journal items belonging to a move (`move_id`).
  - Posted entries must balance in company currency using its rounding precision;
    binary float equality is not the validation rule.
- `account.journal`: The journal container (`type`: `'sale'`, `'purchase'`, `'cash'`, `'bank'`, `'general'`).

## 1. Creating Programmatic Journal Entries
For Python-side relation values in the audited 15/17/18/19/20 series, prefer
`Command` helpers. RPC payloads use the serialized command protocol. Let the
standard accounting workflow compute balances and rates where possible. The
example is structural: validate inputs and permissions before exposing its public
method to callers, and verify configuration in the target database:

```python
from odoo import fields, models
from odoo.fields import Command


class MyModel(models.Model):
    _name = "my.financial.model"
    _description = "Financial Model"

    def create_journal_entry(self, partner, journal, debit_account, credit_account, amount):
        move = self.env["account.move"].create(
            {
                "journal_id": journal.id,
                "partner_id": partner.id,
                "move_type": "entry",
                "line_ids": [
                    Command.create(
                        {
                            "name": "Debit Line Description",
                            "account_id": debit_account.id,
                            "debit": amount,
                            "credit": 0.0,
                            "partner_id": partner.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Credit Line Description",
                            "account_id": credit_account.id,
                            "debit": 0.0,
                            "credit": amount,
                            "partner_id": partner.id,
                        }
                    ),
                ],
            }
        )
        move.action_post()
        return move
```

## 2. Invoicing Patterns
When creating customer invoices or vendor bills programmatically:
- Set `move_type='out_invoice'` or `'in_invoice'`.
- Specify `invoice_line_ids` (not raw `line_ids`). Odoo's compute methods will generate the balancing receivable/payable line and tax lines automatically:
```python
invoice = self.env["account.move"].create(
    {
        "move_type": "out_invoice",
        "partner_id": partner.id,
        "invoice_date": fields.Date.context_today(self),
        "invoice_line_ids": [
            Command.create(
                {
                    "product_id": product.id,
                    "quantity": 2.0,
                    "price_unit": 100.0,
                }
            ),
        ],
    }
)
```

## 3. Best Practices & Invariants
- **Correct validated invoices through credit/debit notes**: Follow the standard
  reversal/correction workflow and the localization's lock and audit rules. A reset
  to draft is not a universal repair procedure. Inspect reversal method signatures
  in the target version before calling private APIs.
- **Rounding & Monetary Fields**: Associate each monetary amount with the correct
  currency; an explicit `currency_field` makes this association clear. It is not
  universally required when the standard `currency_id` field is present:
  ```python
  amount = fields.Monetary(currency_field="currency_id")
  currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
  ```
- **Fiscal positions**: Resolve the effective fiscal position through the target
  invoice workflow, including company and delivery context. Map both taxes and
  accounts; do not assume copying product taxes applies fiscal-position rules.


## Workflow Verification

The examples above illustrate creation inputs; they are not complete accounting
configuration or authorization procedures. Confirm company, journal, accounts,
localization, currencies, taxes and effective fiscal position before creating an
entry. Prefer the existing invoicing flow over rebuilding computed journal lines.

Keep draft, posted, payment-registered, and reconciled states distinct. A credit
note does not alone prove cash was refunded or returned goods were received.
Verify residual amounts, partial payments, exchange differences, rounding, lock
dates, and reconciliation through the matching standard workflows. Test as the
intended accounting user in the intended company.

## Verified version boundaries

Credit/debit-note correction and the distinction among posting, payment and
reconciliation were checked in official 15/17/18/19/20 documentation. Exact
payment-state transitions depend on journal/outstanding-account configuration;
registering a payment does not universally require the same subsequent step.

Fiscal-position setup differs: 15/17/18 show tax mapping on fiscal-position
records; 19/20 configure tax mapping on the taxes themselves, still using fiscal
positions. Account mapping remains part of the workflow. Use the matching
configuration and invoice pipeline rather than copying an older `map_tax` call.

The balance/rounding invariant is supported by each branch's `account_move.py`;
private balancing, reversal and tax methods are not stable cross-version APIs.
A generic example is not evidence that every localization or configured journal
will accept its values.

Official references (select the matching branch for 15/17/18/19/20):
- [Credit notes and refunds](https://github.com/odoo/documentation/blob/18.0/content/applications/finance/accounting/customer_invoices/credit_notes.rst)
- [Fiscal positions](https://github.com/odoo/documentation/blob/18.0/content/applications/finance/accounting/taxes/fiscal_positions.rst)
- [Payments](https://github.com/odoo/documentation/blob/18.0/content/applications/finance/accounting/payments.rst)
- [Fiscal positions, 19](https://github.com/odoo/documentation/blob/19.0/content/applications/finance/accounting/taxes/fiscal_positions.rst)
- [Move model, 19](https://github.com/odoo/odoo/blob/19.0/addons/account/models/account_move.py)

Choose the matching version's workflow and localization before applying these
principles; book examples are not authoritative API contracts.
