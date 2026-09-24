---
name: extending-models
description: Add a new field to an existing Odoo model, optionally showing it in a view; use when no new model is needed.
metadata:
  globs: "**/models/**/*.py"
---

# Extend an existing model

Find the target model and its nearest local extension. Reuse its module and conventions. For a plain field, check the field type, label, default, required and storage settings against the requested behavior. If the field is added to a new Python file, register that file through the module's `__init__.py` chain. If a view is requested, locate the exact view and inheritance anchor, place the field, and check XML and field references.

Before making a field required or changing a default, account for existing records and the behavior of newly created records. For relational fields, confirm the comodel and deletion behavior. For computed or related fields, use the computed-field guidance and verify dependencies, storage, and search behavior. Check access implications if the field exposes data that users could not previously see.

Finish with a focused syntax or behavior check and the diff. If the extension needs a new action, smart button, workflow, or migration, inspect that affected boundary as a bounded feature rather than treating it as a plain field addition.
