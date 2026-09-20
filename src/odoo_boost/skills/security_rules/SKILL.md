---
name: Security Rules
description: Set up access rights (ACLs) and record rules for Odoo models.
globs: ["security/**/*", "__manifest__.py"]
---

# Setting Up Security Rules

## Steps

### 1. Define Security Groups (`security/security.xml`)
```xml
<odoo>
    <data noupdate="0">
        <!-- User group -->
        <record id="group_my_model_user" model="res.groups">
            <field name="name">My Model User</field>
            <field name="category_id" ref="base.module_category_services"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- Manager group (implies User) -->
        <record id="group_my_model_manager" model="res.groups">
            <field name="name">My Model Manager</field>
            <field name="category_id" ref="base.module_category_services"/>
            <field name="implied_ids" eval="[(4, ref('group_my_model_user'))]"/>
        </record>
    </data>
</odoo>
```

### 2. Create ACL File (`security/ir.model.access.csv`)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,group_my_model_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_my_model_manager,1,1,1,1
```

### 3. Add Record Rules (`security/security.xml`)
```xml
<odoo>
    <data noupdate="1">
        <!-- Users can only see their own records -->
        <record id="rule_my_model_user" model="ir.rule">
            <field name="name">My Model: User sees own records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('create_uid', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('group_my_model_user'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- Managers see all records (no domain) -->
        <record id="rule_my_model_manager" model="ir.rule">
            <field name="name">My Model: Manager sees all</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('group_my_model_manager'))]"/>
        </record>
    </data>
</odoo>
```

### 4. Update Manifest
Ensure security files are listed before view files:
```python
'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/my_model_views.xml',
],
```

## Checklist
- [ ] Each persistent business model has the required ACL entries; transient and abstract
  models are reviewed according to the active Odoo version
- [ ] Security groups defined with proper hierarchy (`implied_ids`)
- [ ] Record rules use `noupdate="1"` (customizable by admin)
- [ ] ACL file listed in manifest before views
- [ ] Tested with non-admin user
- [ ] Wizard/transient models also have ACLs
