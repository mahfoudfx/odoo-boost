---
name: domain-mail-chatter
description: Adding chatter, followers, activity scheduling, and field tracking using mail.thread and mail.activity.mixin.
globs: ["models/**/*.py", "views/**/*.xml", "__manifest__.py"]
---

# Mail & Chatter Integration

Integrate record discussions, field-change tracking, and activity schedules into a custom Odoo model.

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
Tracking on a `mail.thread` model records supported field changes during normal ORM operations. Context flags such as `mail_notrack` and `tracking_disable` can suppress it; chatter is not a complete or immutable audit trail.

## 3. View Chatter Integration
Official mixin examples use legacy `oe_chatter` with mail fields in Odoo 15/17,
and `<chatter/>` in 18/19/20. The following example targets 18/19/20; place it as a
sibling of `<sheet>`. Follow the matching series when porting a form:

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

# Post a discussion message; delivery depends on recipients and subscriptions
record.message_post(
    body=_("Milestone deadline updated to %s") % record.target_date,
    message_type="comment",
    subtype_xmlid="mail.mt_comment",
)
```


## Recipients, privacy, and verification

Choose the message subtype and recipients deliberately. Follower subscription
preferences affect notification delivery; a discussion comment is not a promise
that every follower receives email. Internal subtypes restrict visibility to
employees; verify portal/public behavior and attachment access as well.

Pass user content as escaped text. If constructing HTML, use the framework's
safe markup and escaping rules rather than interpolating untrusted values into
trusted markup. Keep message posting under the record's intended access boundary.

For activities, use `mail.activity.mixin` and verify the responsible user, due date,
and completion behavior. Test retries so automation does not create duplicate
activities or notifications. Check tracking enabled/disabled and internal versus
external recipients in the configured version.

Official sources: [mail mixins, tracking flags, and subtypes](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/mixins.rst)
and [escaped content security](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/security.rst).
