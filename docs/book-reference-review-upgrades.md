# Book extraction: existing-data upgrades

## Evidence reviewed

Local book/code root: `references/odoo-books/`.
The Odoo 19 cookbook's `Chapter06/05_data_migrations/my_hostel/` example
contains a manifest at `19.0.1.0.1`, several migration version directories,
pre-phase column preparation, and post-phase date conversion. In
`migrations/19.0.1/post-migrate.py`, the loop retrieves a record ID but its
UPDATE uses a fixed `where id=1`. This illustrates why examples require review,
not wholesale copying. The conversion's invalid/empty-value policy also needs
explicit treatment before production use.

Official comparisons used local 17, 18, 19 and 20 snapshots:
`content/developer/reference/upgrades/upgrade_scripts.rst`. All four confirm
version selection, phase naming, and the update-only execution contract.
The 19 `content/developer/howtos/upgrade_custom_db.rst` was read for separate
empty-database and existing-database checks. Snapshot revisions are recorded in
`references/odoo-official-docs/manifest.json`. These local paths provide audit
evidence only; installed skills do not access them.

## Before and after

Before, the upgrade skill focused on syntax and compatibility matrices. It did
not give a procedure for selecting data-upgrade phases, handling conversion
failures or proving that existing rows were transformed.

After, `upgrade_analysis/references/data-upgrades.md` records the procedure and
verification criteria. The main skill links to it specifically for data changes.
The procedure requires installed/target version evidence, phase selection,
stable identifiers, conversion policy, row checks and separate installation and
upgrade tests. The broad flush-all suggestion was narrowed to relevant pending
fields and cache/dependency handling.

Official citations:
- https://github.com/odoo/documentation/blob/19.0/content/developer/reference/upgrades/upgrade_scripts.rst
- https://github.com/odoo/documentation/blob/19.0/content/developer/howtos/upgrade_custom_db.rst

This was a focused code and documentation review, not execution of the example
migrations or complete coverage of all data-loading chapters.
