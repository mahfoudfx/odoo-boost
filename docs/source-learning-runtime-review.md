# Executed runtime validation of extracted contracts

Executed 2026-11-03. These are **independently authored Odoo 18 framework contract
tests**, prompted by the report-context and portal child-model lessons. They are
not installation or execution of the original v15/v17/v19 book addons, nor tests
of book migrations. Their coverage and execution statuses remain unchanged.

## Environment established

An existing Community source checkout was found at
`/home/mahfoud/dev/web/odoo/sources/odoo18ce`, commit
`df8a3fb0ccfc69fdc612b69e0a22ef1b1b37b779`. Its `odoo-bin --version` reports
`Odoo Server 18.0`. The shallow checkout exposes only 18.0 local/remote refs.
The sibling sources directory contains no 15/17/19 checkout. Python 3.12 and the
needed installed dependencies can load this Odoo checkout. PostgreSQL binaries
report version 18.6; `wkhtmltopdf` exists but was not used for these HTML tests.

This corrects the narrower earlier PATH/import probe: absence of an installed
`odoo` module or executable on PATH did not mean no usable source checkout existed.
No project connection settings, credentials, existing Odoo service or user database
were read or used. A large source download was not needed for this bounded test.

## What actually ran

The retained [harness](../tools/validate_source_contracts.py) creates a new temporary
addon, PostgreSQL cluster, private Unix socket, database, filestore/data directory
and logs below a new `/tmp/odoo-boost-learning-*` directory. It loads `/dev/null`
as configuration, disables HTTP and workers, enables only the test addon tag,
uses `PYTHONDONTWRITEBYTECODE=1` for the existing source checkout, and stops its
own PostgreSQL server in a `finally` block. PostgreSQL has no TCP listener.

The sandbox initially rejected creation of the PostgreSQL Unix socket. Execution
therefore used the required escalated command approval. The initial harness had
two authoring issues (generated Python quoting and the ACL CSV filename); these
were corrected before the successful runs. Those failures are not book-example
failures. Temporary artifacts and logs were retained for inspection.

| Test | Real framework behavior exercised | Result |
|---|---|---|
| `LearningContracts.test_parent_rule_does_not_restrict_child_query` | Creates two documents owned by different users and two child records. An ordinary user's parent rule yields one document, while direct child search initially yields both children. Installing an explicit child ownership rule reduces that same user's child query to one. | Passed on the recorded Odoo 18 source commit. |
| `LearningContracts.test_custom_report_context_and_escaped_html` | Calls the actual report engine's rendering-context method for a custom provider and verifies that `docs`, `doc_ids` and `doc_model` are not injected. Renders HTML through QWeb for two records and verifies that an angle-bracket record name is escaped. | Passed on the recorded Odoo 18 source commit. |

Odoo reports **0 failed, 0 errors out of 2 tests**. The harness also verifies the
expected executed-test count, so a successful process with zero matching tests
does not qualify as a pass. Compact reproducible evidence, source version, exact
argument vector, log hashes, fixture semantics and cluster-stop result are in
[runtime-validation.json](source-learning/runtime-validation.json).

## Official contract comparison

Runtime evidence establishes these two contracts on the exact implementation used:

- [Actual Odoo report engine](https://github.com/odoo/odoo/blob/df8a3fb0ccfc69fdc612b69e0a22ef1b1b37b779/odoo/addons/base/models/ir_actions_report.py): `_get_rendering_context` and `_render_qweb_html`.
- [Official 18 report documentation](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/developer/reference/backend/reports.rst): custom providers must supply document defaults if their template requires them.
- [Official 18 security documentation](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/developer/reference/backend/security.rst): ACLs grant model access; record rules are default-allow when no applicable rule exists.
- [Official 18 QWeb documentation](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/developer/reference/frontend/qweb.rst): ordinary `t-out` escapes output.

The independently authored fixtures are retained in the harness. They turn selected
source-review lessons into repeatable runtime checks without importing copyrighted
book implementation into the package. Their provenance is official-contract-led;
the books supplied the motivating scenarios.

## Practical limits and next validation

The test addon does not implement a portal page; it tests underlying record-rule
scope directly as a non-admin user. Report verification covers custom rendering
context and HTML escaping, not PDF generation, translated field values, paper
format, multiple companies or browser/editor behavior. Installed automatic Odoo
dependencies are recorded in the full log and are not a certification of their
features. PostgreSQL 18.6 was the available local server, not a full deployment
compatibility matrix.

Matching v15/v17/v19 runtimes are still needed to execute their original examples
without conflating a migration/port with original behavior. Original-addon and
migration execution remain open. Further scenarios should be added only when
they verify a retained behavioral claim; provider sandboxes, Enterprise modules
and physical IoT devices have separate prerequisites.
