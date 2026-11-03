## ORM Best Practices

### Model Definition
- Inherit from `models.Model` for persistent models, `models.TransientModel` for wizards, `models.AbstractModel` for mixins.
- Set `_name` for new models, `_inherit` for extending existing ones.
- Set a meaningful `_description` on new models; do not treat a missing value as
  a universally enforced version-specific error.
- Set `_order` to define default sort order.
- Use `_rec_name` to specify the display name field if it's not `name`.

### Field Definitions
- Always provide a `string` (label) for fields, or use a self-explanatory field name.
- Use `required=True` for mandatory values and server-side constraints for business invariants. Onchange improves form behavior; imports and RPC calls can bypass it.
- Choose indexes from measured query patterns; account for write overhead and selectivity.
- For searchable computed fields, choose `store=True` or a `search` method that returns an equivalent domain. Weigh stored recomputation cost.
- Define `inverse` when computed fields should be writable.
- Use `related` fields for simple delegated access to related model fields.
- Use `tracking=True` on fields that should be logged in the chatter.

### CRUD and Recordsets
- `self` in model methods is always a recordset (zero or more records).
- Use `self.ensure_one()` when the method expects exactly one record.
- Use recordset operations when they express the intended result; preserve
  batching and profile query behavior rather than rewriting loops mechanically.
- Prefer `create()`, `write()`, and `unlink()` to raw SQL. If raw SQL is necessary,
  parameterize it and preserve ORM cache and security considerations.
- Override `create()` / `write()` for custom logic, always calling `super()`.
- When overriding `unlink()`, handle cascading cleanup before `super().unlink()`.

### Domains
- Domains are lists of tuples: `[('field', 'operator', value)]`.
- Use `|` and `&` prefix operators for OR/AND: `['|', ('a', '=', 1), ('b', '=', 2)]`.
- Common operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not in`, `like`, `ilike`, `=like`, `=ilike`, `child_of`, `parent_of`.

### Performance Tips
- Use `search_read()` for dictionary results; retain a recordset when later
  operations need ORM behavior.
- Use `sudo()` only when necessary — it bypasses access rights.
- Avoid looping over large recordsets with individual `write()` calls — batch them.
- Use `with_context()` to pass flags, not to store state.
- Preserve recordset prefetching: browse IDs together before iterating. Profile queries before adding explicit reads.
- Use `@api.model_create_multi` for batched `create()` calls.
