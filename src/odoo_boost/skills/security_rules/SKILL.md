---
name: security-rules
description: Set up access rights (ACLs) and record rules for Odoo models.
globs: ["security/**/*", "__manifest__.py"]
---

# Setting Up Security Rules

## Select the access model first

The examples below use the separate ACL/record-rule model documented for Odoo
15/17/18/19. For audited Odoo 20, use the unified `ir.access` model instead:
`operation` selects CRUD operations, group-bound entries grant permission, and
entries without a group impose global restrictions through their domains.
Inspect the target source and migrate existing metadata deliberately; applying
old no-group ACL semantics to a new no-group restriction changes its meaning.
See [official 20 security documentation](https://github.com/odoo/documentation/blob/20.0/content/developer/reference/backend/security.rst)
and [implementation](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_access.py).
Optional group organization is omitted from the shared example below. Odoo 19
uses `privilege_id` on `res.groups`, rather than the older `category_id`; inspect
the target schema when adding group organization. See the
[official Odoo 19 group model](https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/models/res_groups.py).

## Odoo 15/17/18/19 examples

### 1. Define Security Groups (`security/security.xml`)
```xml
<odoo>
    <data noupdate="0">
        <!-- User group -->
        <record id="group_my_model_user" model="res.groups">
            <field name="name">My Model User</field>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- Manager group (implies User) -->
        <record id="group_my_model_manager" model="res.groups">
            <field name="name">My Model Manager</field>
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

## Effective Permission Checks

Read the core security guidance for the configured access model: ACL addition
and rule flags in 15/17/18/19, unified permission/restriction operations in 20. Verify read, create, write, and unlink separately as
an ordinary user, a user in multiple groups, and a manager. Include another
user's records and another company. Hidden menus and readonly form fields do
not replace server-side access checks.

## Checklist
- [ ] Each persistent business model has the required ACL entries; transient and abstract
  models are reviewed according to the active Odoo version
- [ ] Security groups defined with proper hierarchy (`implied_ids`)
- [ ] Record rules use `noupdate="1"` (customizable by admin)
- [ ] ACL file listed in manifest before views
- [ ] Tested with non-admin user
- [ ] Wizard/transient access follows the target version and checks target-record permissions
- [ ] Public model methods validate attacker-controlled recordsets and arguments
- [ ] Sensitive fields use `groups`; sensitive related chains review `compute_sudo`
- [ ] Every `sudo()`, user/company switch, raw SQL query, and dynamic domain has a
      narrow, documented trust boundary
- [ ] Controller writes whitelist fields and nested x2many commands; state changes
      use POST and HTTP routes retain CSRF protection
- [ ] Dynamic field access uses `record[name]` after allowlisting; secrets use
      constant-time comparison; addon file reads use `odoo.tools.file_open`

For a security audit, also inspect `Markup`/`markup`, HTML sinks, `eval`/`safe_eval`,
`pickle`, mutable default arguments, and model methods returning rich backend objects.
Judge each hit by its data flow rather than reporting string matches mechanically.
On Odoo 20, load the version note for `fields.Domain`, `@api.private`, related-field,
and controller-specific guidance.

## Executable validation

Use `plan_changed_checks` for changes spanning multiple technical surfaces. Run
`diagnose_odoo_code` on the exact addon or file for relevant static checks; enable
Odoo LS when framework diagnostics are needed. Use `trace_odoo_source` and
`list_controller_routes` for source relationships. Run `run_odoo_tests` only with
the explicitly configured disposable test database. Report executed checks,
review-required findings and unavailable checks separately. Reading this skill
is not a successful audit or test run. For tiny presentation edits, run the
smallest relevant syntax check instead of a broad scan.
