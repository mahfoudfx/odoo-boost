## Security

### Access Rights (ir.model.access)
- Give each persistent business model the ACLs it needs in `ir.model.access.csv`.
  Check transient and abstract model behavior in the configured Odoo version instead of
  copying persistent-model ACLs mechanically.
- Format: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`.
- Use `base.group_user` for internal users, `base.group_portal` for portal, `base.group_public` for public.
- Grant minimum necessary permissions — follow the principle of least privilege.
- If no `group_id` is set, the rule applies to all users (global ACL).

### Record Rules (ir.rule)
- Record rules filter which records a group can access via domains.
- Global rules (no group) apply to ALL users and are combined with AND.
- Group rules are combined with OR between groups, then AND with global rules.
- Define in `security/security.xml`.
- Use `noupdate="1"` for rules that admins may want to customize.

### Security Groups
- Define groups in XML: `<record model="res.groups">`.
- Use `implied_ids` for group inheritance (e.g. Manager implies User).
- Use `category_id` to organize groups under application categories.
- Reference groups in views with `groups="module.group_xml_id"`.

### Common Pitfalls
- Never use `sudo()` to work around access rights bugs — fix the ACLs instead.
- Treat every public model method as an RPC entry point. Validate its recordset and
  arguments, and keep internal helpers private. On versions that provide it,
  `@api.private` can protect a name that cannot safely be renamed.
- Restrict sensitive fields with `groups`; review cross-model related fields because
  their compute may use elevated access. Use `related_sudo=False` when normal access
  checks must apply.
- Never concatenate an untrusted domain onto an access restriction. Use the target
  version's domain-composition API (`fields.Domain` on Odoo 20) or construct a fixed,
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
