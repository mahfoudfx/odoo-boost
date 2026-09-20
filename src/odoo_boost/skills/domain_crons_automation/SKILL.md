---
name: Crons & Scheduled Actions
description: Implement reliable, batch-safe recurring background jobs with ir.cron.
globs: ["models/**/*.py", "data/**/*.xml"]
---

# Crons & Scheduled Actions (`ir.cron`)

Scheduled actions run recurring background operations in Odoo, such as email dispatch,
synchronizations, invoice generation, or maintenance jobs. This skill covers `ir.cron`;
use **Automated Actions** for `base.automation` and server actions tied to record events.

## 1. Defining the Cron in Data XML
Define the XML record in `data/ir_cron_data.xml` with `noupdate="1"` so administrators can customize the schedule without module upgrades resetting it:

```xml
<odoo noupdate="1">
    <record id="ir_cron_sync_external_orders" model="ir.cron">
        <field name="name">Sync External Orders</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="state">code</field>
        <field name="code">model._cron_sync_external_orders()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">hours</field>
        <field name="numbercall">-1</field>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

## 2. Model Method Implementation & Batch Safety
Cron tasks often process large datasets. Methods must be batch-friendly and avoid memory exhaustion or long database lockups:

```python
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _cron_sync_external_orders(self, batch_size=100):
        """Processes pending orders in chunks."""
        pending_records = self.search(
            [
                ("state", "=", "draft"),
                ("needs_sync", "=", True),
            ],
            limit=batch_size,
        )

        _logger.info("Starting order sync cron: %d orders to process", len(pending_records))
        for order in pending_records:
            try:
                order._process_single_sync()
            except Exception as exc:
                _logger.exception("Failed to sync order %s: %s", order.name, exc)
                # Continue processing other records rather than failing entire cron
                continue
```

## 3. Best Practices
- **Never rely on UI context**: Cron jobs run as `base.user_root` (or the user specified in `user_id`) without browser session context. Never expect `self.env.user` to be a normal interactive user.
- **Log Meaningfully**: Use Python's standard `logging` with module prefixes (`_logger.info`, `_logger.warning`).
- **Use `limit`**: Never do an unconstrained `.search([])` inside a cron if the table grows continuously over time.
