---
name: domain-wizards
description: Creating modal dialog wizards using TransientModel, action buttons, and active_id context.
globs: ["wizard/**/*.py", "wizard/**/*.xml", "views/**/*.xml"]
---

# Transient Models & Wizards

Wizards are interactive dialog popups used for user confirmation, parameter collection, or batch actions. They inherit from `models.TransientModel` and their records are automatically pruned periodically by an Odoo vacuum cron.

## 1. Transient Model Definition
Create under `wizard/my_wizard.py`:

```python
from odoo import fields, models


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


## Trust boundary and verification

`active_model`, `active_id`, `active_ids`, default context values, and readonly
wizard fields can be supplied by a caller. Validate the expected model and target
selection, existence, eligibility, company consistency, and allowed transitions
on the server. Keep target operations under the intended user's access checks;
transient ownership does not authorize writes to persistent records.

Use the target model's business method rather than writing its state directly.
Keep the operation atomic unless its documented workflow requires otherwise.
Test empty selections, stale/deleted records, another user's IDs, cross-company
records, and a disallowed transition. A cancelled dialog must not mutate records.

The model/view examples above are structural templates. Implement `action_apply`
with the verified business operation before using the view button. Add chatter only if the
persistent model inherits the appropriate mixin.

Official references: [public method security](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/security.rst),
[window actions](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/actions.rst),
and [ORM model types](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/orm.rst).
