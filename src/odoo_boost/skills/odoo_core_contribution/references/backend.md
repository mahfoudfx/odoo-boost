# Backend contribution checks

Read only the sections relevant to the changed files.

## Structure and Python

- Match the official addon's existing layout. Keep one principal model class per
  file, use conventional model-derived filenames, and list every direct module
  dependency in the manifest.
- Keep imports grouped and sorted. Translate static literals with named
  placeholders; do not construct a dynamic source string before translation.
- Treat public model methods as RPC surface. Put real extension points in small,
  override-friendly methods and keep internal helpers private.

## ORM and transactions

- Make `create` overrides batch-compatible and decorate them with
  `@api.model_create_multi`. Declare every dependency read by computed fields.
- Enforce invariants in constraints or CRUD logic; onchange is a UI convenience.
- Batch searches, aggregates, creates, and writes. Put selective conditions in
  domains and use indexed fields where justified by measured access patterns.
- Never commit or roll back a cursor owned by Odoo. Catch specific exceptions
  around the smallest operation that can recover.
- Do not depend on `odoo.http.request` in model logic; it is absent in jobs,
  tests, and ordinary RPC calls.

## XML, reports, and tests

- Anchor inherited views on stable names or attributes, not positional XPath.
  Preserve existing XML IDs on stable branches.
- A custom report context must retain the standard document values expected by
  report templates.
- Ensure every `test_*.py` is imported. Use `TransactionCase` for business
  behavior and `HttpCase` where HTTP/browser behavior is essential. Verify that
  a regression test fails before the fix.
