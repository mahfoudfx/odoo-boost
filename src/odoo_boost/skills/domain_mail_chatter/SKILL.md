---
name: domain-mail-chatter
description: Adding chatter, followers, activity scheduling, and field tracking using mail.thread and mail.activity.mixin.
globs: ["models/**/*.py", "views/**/*.xml", "__manifest__.py"]
---

# Mail & Chatter Integration

Integrate standard social messaging, audit trails, and activity schedules into any custom Odoo model.

## 1. Manifest Dependency
In `__manifest__.py`, add `'mail'` to `'depends'`:
```python
'depends': ['base', 'mail'],
```

## 2. Model Inheritance
Inherit `mail.thread` and optionally `mail.activity.mixin`:

```python
from odoo import fields, models


class ProjectMilestone(models.Model):
    _name = "project.milestone"
    _description = "Project Milestone"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("achieved", "Achieved"),
        ],
        default="planned",
        tracking=True,
    )
    target_date = fields.Date(tracking=True)
    responsible_id = fields.Many2one("res.users", tracking=True)
```
*Any field with `tracking=True` automatically creates an audit entry in chatter when its value changes.*

## 3. View Chatter Integration
Add the `<chatter/>` component inside the `<sheet>` sibling in the form view:

```xml
<record id="view_project_milestone_form" model="ir.ui.view">
    <field name="name">project.milestone.form</field>
    <field name="model">project.milestone</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <div class="oe_title">
                    <h1><field name="name"/></h1>
                </div>
                <group>
                    <field name="state"/>
                    <field name="target_date"/>
                    <field name="responsible_id"/>
                </group>
            </sheet>
            <chatter/>
        </form>
    </field>
</record>
```

## 4. Programmatic Message Posting & Notifications
```python
# Post an internal log note
record.message_post(
    body=_("Milestone marked as achieved."),
    message_type="comment",
    subtype_xmlid="mail.mt_note",
)

# Post a public message notified to followers
record.message_post(
    body=_("Milestone deadline updated to %s") % record.target_date,
    message_type="notification",
    subtype_xmlid="mail.mt_comment",
)
```
