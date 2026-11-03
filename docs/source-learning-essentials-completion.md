# Essentials: remaining distinct file contents

Batch `LEARN-2026-11-03-04`, 2026-11-03. Origin: **code example**. This pass
read the remaining 24 distinct text contents and visually inspected the single
distinct application icon after the earlier 81-file review. Together the two
passes have inspected representatives of all 96 distinct byte contents in the
419-file v15 Essentials archive. This is content coverage, not completion of every
chapter snapshot's integration context. Repeated paths retain their own pending
status until their context is reviewed.

## New lessons

| ID | Exact locator within the v15 example root | Retained experience | Project usefulness |
|---|---|---|---|
| SR-01 | `ch03/library_app/views/book_view.xml` | The filter labelled Inactive selects `active=True`; Active selects `active=False`. Validate the user-facing label against the actual domain, including archived-record scenarios. XML parsing cannot establish semantic agreement. | Concrete acceptance scenario for existing view/testing guidance; note-only. |
| SR-02 | `ch11/library_checkout/views/checkout_kanban_view.xml` | Legacy kanban fields are objects carrying `value` and `raw_value`. Comparing `record.num_books` directly to zero or `record.state` directly to a string compares the field wrapper, unlike the file's correct `record.num_books.raw_value` branches. Match value access to the renderer contract. | Precise old-version review example; avoid copying legacy snippets into modern kanban/Owl without checking the configured version. Note-only. |
| SR-03 | `ch05/library_app/data/res.partner.csv`, `library.book.csv`, `book_demo.xml`; `ch08/library_checkout/data/stage_data.xml`; snapshot menus and wizard XML | Stable external IDs and file-order dependencies connect records and actions. `noupdate` makes seed values an upgrade policy decision. Review view/action/data together; the chapter snapshots demonstrate increasing dependencies and UI surface rather than interchangeable standalone files. | Confirms the existing dependency-order and install/update guidance; no rewrite needed. |

Official evidence: pinned Odoo 15 documentation revision
`f6b84ed59624ba8f0db2b1d0f7097e435550bb7e`:

- [Views](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/views.rst): filter domains and the kanban rendering context's field `value`/`raw_value` contract.
- [Data files](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/data.rst): sequential loading, external references and `noupdate`.

The remaining simple templates, menus, imports, metadata and icon added no distinct
new rule beyond the recorded findings. Their reading is still recorded. Actual
browser behavior and installation/update of these v15 addons remain unexecuted.
Per-file coverage and lesson dispositions are in the shared JSONL ledger.
