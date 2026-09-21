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
  - Strict invariant: For any posted entry (`state == 'posted'`), `sum(debit) == sum(credit)`.
- `account.journal`: The journal container (`type`: `'sale'`, `'purchase'`, `'cash'`, `'bank'`, `'general'`).

## 1. Creating Programmatic Journal Entries
Always use `Command` operations and let the ORM compute balances and currency rates where possible:

```python
from odoo import Command, models


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
                    "tax_ids": [Command.set(product.taxes_id.ids)],
                }
            ),
        ],
    }
)
```

## 3. Best Practices & Invariants
- **Never modify posted lines**: An entry with `state == 'posted'` should not have amounts directly written; call `button_draft()` first if permitted, or create a reversal entry (`_reverse_moves()`).
- **Rounding & Monetary Fields**: Always specify `currency_field` on `fields.Monetary`:
  ```python
  amount = fields.Monetary(currency_field="currency_id")
  currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
  ```
- **Fiscal Position Translation**: Apply partner fiscal positions to map accounts and taxes automatically (`partner.property_account_position_id.map_tax(taxes)`).
