---
name: translation-edits
description: Edit Odoo addon PO translations for specified labels, report text, or messages in requested languages, including when the exact source strings must be located.
metadata:
  globs: "**/i18n/*.po, **/i18n/*.pot"
---

# Edit specific translations

Use this path for a bounded translation request. If the source string is built at runtime or the user asks to change extraction behavior, inspect that source before editing the catalog.

1. Locate the exact source text and its Odoo occurrence, such as a QWeb template or view XML ID. Search the requested locale catalogs for its `msgid`, `msgctxt` when present, and reference comments. Check nearby entries to preserve the module's catalog conventions. A shared `msgid` may cover several source occurrences; inspect those references before changing its `msgstr`.
2. Update the matching translation in each requested locale. Add a missing entry only after matching it to the source occurrence and existing catalog format. Preserve headers, plural forms, flags, and unrelated entries. If the source text itself changes, determine whether the module's POT and locale catalogs need extraction or merging; a translation-only change does not require catalog regeneration.
3. Validate the changed PO files with an available PO parser or `msgfmt -c`; verify every requested term and locale, then review the diff. If no parser is available, check stanza syntax and report that limitation. Stop when the requested strings and focused check agree.

Use the project's normal deployment process for loading translations. A local catalog edit does not itself call for a database upgrade or an investigation of Odoo's translation engine.
