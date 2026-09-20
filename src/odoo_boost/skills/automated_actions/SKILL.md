---
name: Automated Actions
description: Create record-triggered base.automation and reusable server actions in Odoo.
globs: ["data/**/*.xml", "__manifest__.py"]
---

# Creating Automated Actions

Use this skill for server actions and actions triggered by record events or automation
rules. Use **Crons & Scheduled Actions** for recurring background jobs implemented with
`ir.cron`; do not duplicate a scheduled job as a time-based automation without a clear
business reason.

## Steps

### 1. Server Action (`data/server_actions.xml`)
```xml
<odoo>
    <data noupdate="1">
        <!-- Server action that runs Python code -->
        <record id="action_auto_confirm_order" model="ir.actions.server">
            <field name="name">Auto Confirm Order</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="state">code</field>
            <field name="code">
for record in records:
    if record.state == 'draft' and record.total > 0:
        record.action_confirm()
            </field>
        </record>

        <!-- Server action that sends email -->
        <record id="action_send_notification" model="ir.actions.server">
            <field name="name">Send Notification Email</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="state">email</field>
            <field name="template_id" ref="email_template_my_model"/>
        </record>

        <!-- Server action that creates a record -->
        <record id="action_create_task" model="ir.actions.server">
            <field name="name">Create Follow-up Task</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="state">object_create</field>
            <field name="crud_model_id" ref="project.model_project_task"/>
            <field name="value">My follow-up for {{object.name}}</field>
        </record>
    </data>
</odoo>
```

### 2. Automated Action / Base Automation (`data/automated_actions.xml`)
```xml
<odoo>
    <data noupdate="1">
        <!-- Trigger on record creation -->
        <record id="auto_action_on_create" model="base.automation">
            <field name="name">Auto-assign on Create</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="trigger">on_create</field>
            <field name="action_server_ids" eval="[(4, ref('action_auto_confirm_order'))]"/>
        </record>

        <!-- Trigger on field change -->
        <record id="auto_action_on_state_change" model="base.automation">
            <field name="name">Notify on Confirmation</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="trigger">on_write</field>
            <field name="trigger_field_ids" eval="[(4, ref('field_my_model__state'))]"/>
            <field name="filter_domain">[('state', '=', 'confirmed')]</field>
            <field name="action_server_ids" eval="[(4, ref('action_send_notification'))]"/>
        </record>

        <!-- Trigger on time condition -->
        <record id="auto_action_timed" model="base.automation">
            <field name="name">Auto-close after 30 days</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="trigger">on_time</field>
            <field name="trg_date_id" ref="field_my_model__create_date"/>
            <field name="trg_date_range">30</field>
            <field name="trg_date_range_type">day</field>
            <field name="filter_domain">[('state', '=', 'confirmed')]</field>
            <field name="action_server_ids" eval="[(4, ref('action_auto_confirm_order'))]"/>
        </record>
    </data>
</odoo>
```

### 3. Add Dependency
Ensure `base_automation` is in your module's `depends`:
```python
'depends': ['base_automation', ...],
```

### 4. Update Manifest
```python
'data': [
    'data/server_actions.xml',
    'data/automated_actions.xml',
],
```

## Trigger Types Reference
| Trigger | Description |
|---------|-------------|
| `on_create` | When a record is created |
| `on_write` | When specified fields are updated |
| `on_create_or_write` | On both creation and update |
| `on_unlink` | When a record is deleted |
| `on_time` | Time-based condition |

## Checklist
- [ ] `base_automation` in module dependencies
- [ ] `noupdate="1"` for customizable automation records
- [ ] Server action code references `records` (the triggered recordset)
- [ ] Time-based triggers have `trg_date_id` and range configured
- [ ] Filter domains validated
- [ ] Data files listed in manifest
