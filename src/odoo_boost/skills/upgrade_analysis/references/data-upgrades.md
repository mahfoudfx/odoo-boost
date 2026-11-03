# Upgrading existing module data

Use when a field changes type or name, records or external IDs are renamed, or
an existing installation must retain settings during an update.

## Plan the transformation

Record installed and target module versions, schema before/after, affected rows,
and the invariant the conversion must preserve. Distinguish an Odoo major upgrade
from updating an addon within one series. Installation hooks do not replace data
upgrade scripts. Preserve user-managed data and plan changes to `noupdate` records.

## Choose the phase and version

Use the configured version's supported `upgrades/` or `migrations/` layout with
a version directory and `pre-`, `post-`, or `end-` filenames. The usual entry
point is `migrate(cr, version)`, where `version` is the installed module version.
The upgrade directory must be newer than that installed version and no newer
than the incoming module version. A successful clean install does not demonstrate
that an upgrade script was selected or ran.

Perform old-schema preparation before loading the changed model. Use post-phase
work when the updated model and dependencies are available, and end-phase work
when other upgraded modules must already be loaded. Confirm the exact loader
ordering in the configured series before coupling scripts across modules.

## Transform safely

Keep source values recoverable until conversion checks pass. Define how empty,
invalid, duplicate, ambiguous, and locale-dependent values are handled. Reject
unexpected formats or report them for an explicit resolution; silently skipping
rows is not evidence of successful conversion.

Use stable identifiers to update each intended row. Parameterize both converted
values and row identifiers; a hard-coded ID in a loop repeatedly updates the
same row. Check affected-row counts and compare source and destination values.
For large datasets, bound memory and preserve transaction ownership. See the
performance reference for ORM flush, cache invalidation, and dependency updates
when combining ORM and SQL. Use rename helpers only after verifying their
availability and handling of external references in the target environment.

## Verify two paths

Check a clean installation on an empty disposable database, then an upgrade of a
representative existing database separately. Verify script selection, migrated
row counts, preserved links and external IDs, user settings, and invalid-data
handling. Test multi-row data so a hard-coded identifier cannot pass unnoticed.
Rehearse restore and retry from a known backup; avoid assuming scripts can be
arbitrarily rerun after partially completed manual operations.

Database execution follows the project's authorization and disposable-database
rules. This reference does not authorize a production upgrade.

## Official evidence

Checked against local snapshots of the official 17, 18, 19, and 20 branches:
`content/developer/reference/upgrades/upgrade_scripts.rst` and
`content/developer/howtos/upgrade_custom_db.rst`. The 15 documentation layout differs, so its pinned official migration loader
was also checked: `migrate(cr, installed_version)`, pre/post/end phases, both
directory names, and installed-to-incoming version selection are present.
Matching loader files were reviewed for the other four series as well.

- [Upgrade scripts, Odoo 19](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/upgrades/upgrade_scripts.rst)
- [Customized database upgrade, Odoo 19](https://github.com/odoo/documentation/blob/19.0/content/developer/howtos/upgrade_custom_db.rst)

Independently authored guidance; local books and their examples are not package
dependencies.
