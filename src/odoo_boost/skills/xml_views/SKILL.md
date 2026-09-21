---
name: xml-views
description: Create and customize Odoo XML views (form, list, kanban, search).
globs: ["views/**/*.xml", "__manifest__.py"]
---

# Creating XML Views

## Small edits to an existing view

For a label or title change, find the existing view and change its `string` attribute (or the action/menu `name` if that is the requested title). For column order, move the existing `<field>` elements within the list view. Keep their attributes and surrounding XPath inheritance intact. Use the configured version notes before changing root tags or dynamic attributes. Read the matching XML and inspect the diff; no database inspection or new view scaffold is needed unless the target cannot be identified from source.

The creation examples and checklist below apply when creating a new view, action, or menu. They are not requirements for a small edit to an existing view.

## Steps

### 1. Form View
```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.model.view.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <header>
                <button name="action_confirm" type="object" string="Confirm"
                        class="btn-primary" invisible="state != 'draft'"/>
                <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1><field name="name" placeholder="Name..."/></h1>
                </div>
                <group>
                    <group>
                        <field name="partner_id"/>
                        <field name="active"/>
                    </group>
                    <group>
                        <field name="total"/>
                    </group>
                </group>
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <list editable="bottom">
                                <field name="name"/>
                                <field name="amount"/>
                            </list>
                        </field>
                    </page>
                </notebook>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### 2. List View
```xml
<record id="my_model_view_list" model="ir.ui.view">
    <field name="name">my.model.view.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Models">
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state" decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"/>
            <field name="total" sum="Total"/>
        </list>
    </field>
</record>
```

### 3. Search View
```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">my.model.view.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="My Models">
            <field name="name"/>
            <field name="partner_id"/>
            <filter name="filter_draft" string="Draft" domain="[('state','=','draft')]"/>
            <filter name="filter_confirmed" string="Confirmed" domain="[('state','=','confirmed')]"/>
            <separator/>
            <filter name="group_state" string="Status" context="{'group_by': 'state'}"/>
        </search>
    </field>
</record>
```

### 4. Action + Menu
```xml
<record id="my_model_action" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form</field>
</record>

<menuitem id="my_model_menu_root" name="My App" sequence="10"/>
<menuitem id="my_model_menu" name="My Models" parent="my_model_menu_root"
          action="my_model_action" sequence="10"/>
```

### 5. View Inheritance
```xml
<record id="res_partner_view_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.view.form.inherit.my_module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='phone']" position="after">
            <field name="my_custom_field"/>
        </xpath>
    </field>
</record>
```

## Checklist
- [ ] Views registered in `__manifest__.py` `data` list
- [ ] XML IDs follow naming convention
- [ ] Form view has `<sheet>` wrapper
- [ ] Search view includes useful filters and group-by
- [ ] Action `view_mode` includes all relevant view types
- [ ] Menu item linked to action
