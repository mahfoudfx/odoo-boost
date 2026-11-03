## Security

### Odoo 15/17/18/19: ACLs and Record Rules

#### Access Rights (ir.model.access)
- Give each persistent business model the ACLs it needs in `ir.model.access.csv`.
  Check transient and abstract model behavior in the configured Odoo version instead of
  copying persistent-model ACLs mechanically.
- Format: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`.
- Use `base.group_user` for internal users, `base.group_portal` for portal, `base.group_public` for public.
- Grant minimum necessary permissions — follow the principle of least privilege.
- If no `group_id` is set, the rule applies to all users (global ACL).

#### Record Rules (ir.rule)
- ACL grants are additive across groups; a zero permission does not revoke another grant.
- Record rules filter records after ACL checks. If no applicable rule restricts an
  operation, record-rule evaluation allows it.
- Rule `perm_*` flags select which operations the rule applies to; False does not
  deny that operation. Test the effective permissions across all user groups.
- Global rules (no group) apply to ALL users and are combined with AND.
- Group rules are combined with OR between groups, then AND with global rules.
- Define in `security/security.xml`.
- Use `noupdate="1"` for rules that admins may want to customize.

### Odoo 20: Unified Access Rights

The audited 20.0 documentation and source use `ir.access`: a group-bound entry
is a permission, an entry without a group is a global restriction. `operation`
selects CRUD operations and `domain` selects records. Permissions combine by
union and global restrictions by intersection. Do not copy the older ACL CSV
and `ir.rule` examples into 20 without a migration to the target access model.

### Security Groups
- Define groups in XML: `<record model="res.groups">`.
- Use `implied_ids` for group inheritance (e.g. Manager implies User).
- Inspect the target group schema before setting application/category metadata;
  group organization fields changed across these series.
- Reference groups in views with `groups="module.group_xml_id"`.

### Common Pitfalls
- Never use `sudo()` to work around access rights bugs — fix the ACLs instead.
- Treat every public model method as an RPC entry point. Validate its recordset and
  arguments, and keep internal helpers private. On versions that provide it,
  `@api.private` can protect a name that cannot safely be renamed.
- Restrict sensitive fields with `groups`; review cross-model related fields because
  their compute may use elevated access. Set `compute_sudo=False` explicitly
  when normal access checks must apply; inspect inherited field overrides too.
- Never concatenate an untrusted domain onto an access restriction. Use the target
  version's domain-composition API (`fields.Domain` on Odoo 19/20) or construct a fixed,
  validated domain.
- Under `sudo()`, validate x2many commands as carefully as ordinary values: they can
  write records on another model with the elevated environment.
- Parameterize unavoidable SQL and validate identifiers. Prefer ORM queries that keep
  record rules, active filtering, translations, and cache invalidation intact.
- Use `odoo.tools.file_open` for addon resources, `odoo.tools.consteq` for secrets,
  JSON for serialized data, and `record[name]` for a validated dynamic field name.
- Never use `pickle`, `eval`, or `exec` on untrusted data. Treat `safe_eval` as a
  privileged facility, not a general parser.
- Always test as a non-admin user to verify access rules.
- Review wizard actions and their target records under the intended user; a wizard must
  not become a way to bypass permissions on persistent models.
- Sanitize user input in controllers — Odoo's ORM handles SQL injection but not XSS.
- Use `fields.Html` with `sanitize=True` for user-provided HTML content.


### Official Version Evidence
The 15/17/18/19 security references document separate ACLs and record rules.
The 20 reference documents unified access rights, confirmed in its implementation:
[Odoo 20 access model](https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/models/ir_access.py).
For computed/related access defaults, inspect the matching `Field._get_attrs`
implementation; ordinary computes default `compute_sudo` according to storage,
while related fields default to elevated computation. Read the configured version
notes before changing persistent access metadata.
