---
name: Transient Models & Wizards
description: Creating modal dialog wizards using TransientModel, action buttons, and active_id context.
globs: ["wizard/**/*.py", "wizard/**/*.xml", "views/**/*.xml"]
---

# Transient Models & Wizards

Wizards are interactive dialog popups used for user confirmation, parameter collection, or batch actions. They inherit from `models.TransientModel` and their records are automatically pruned periodically by an Odoo vacuum cron.

## 1. Transient Model Definition
Create under `wizard/my_wizard.py`:

```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BatchUpdateWizard(models.TransientModel):
    _name = "batch.update.wizard"
    _description = "Batch Update Wizard"

    reason = fields.Text(string="Reason", required=True)
    new_state = fields.Selection(
        [
            ("confirmed", "Confirm"),
            ("cancel", "Cancel"),
        ],
        default="confirmed",
        required=True,
    )

    def action_apply(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids", [])
        records = self.env["my.model"].browse(active_ids)
        if not records:
            raise UserError(_("No records selected."))

        records.write(
            {
                "state": self.new_state,
            }
        )
        for rec in records:
            rec.message_post(body=_("Batch update applied: %s") % self.reason)

        return {"type": "ir.actions.act_window_close"}
```

## 2. Wizard View Definition
Define under `wizard/my_wizard_views.xml`:

```xml
<record id="view_batch_update_wizard_form" model="ir.ui.view">
    <field name="name">batch.update.wizard.form</field>
    <field name="model">batch.update.wizard</field>
    <field name="arch" type="xml">
        <form string="Batch Update">
            <group>
                <field name="new_state"/>
                <field name="reason"/>
            </group>
            <footer>
                <button name="action_apply" string="Apply" type="object" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

## 3. Window Action & Action Binding
To make the wizard triggerable from the "Action" menu on list or form views:

```xml
<record id="action_batch_update_wizard" model="ir.actions.act_window">
    <field name="name">Batch Update</field>
    <field name="res_model">batch.update.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list,form</field>
</record>
```
Notice `target="new"` opens the view as a modal dialog.
