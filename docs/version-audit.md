# Systematic version audit of extracted guidance

Audit scope: Odoo 15, 17, 18, 19 and 20. This audits the book-derived skills and
guidelines plus central version metadata against official documentation and selected
official implementations. It is not a full review of every book, every package
tool, or every Odoo module. No live five-version Odoo test matrix was run.

## Outcome and before/after

| Area | Before | After |
|---|---|---|
| Access model | 20 unified access incorrectly described as master-only | 15–19 separate ACL/rules; audited 20 unified ir.access |
| Domain builder | Listed only for 20 | Documented 19 and 20 API; version profile fixed |
| Cron batching | Risks from inheriting newer progress APIs | 18 notify-progress versus 19/20 commit-progress; no unsupported older helper assumption |
| Frontend | Universal modern imports and pragma advice | 15 Owl/template conventions; 15/17 pragma opt-in; 18+ automatic standard paths |
| Hooks | Generic signature check | Cursor signatures in 15; environment signatures in 17–20 |
| Stock | A modern quantity/unit field could be copied to older versions | Version table for qty_done, quantity/picked, and 20 uom_id |
| Units | Category advice could be applied to 19/20 | Category model in 15/17/18, reference-chain implementation in 19/20 |
| Fiscal positions | Older mapping setup could be applied universally | Mapping configuration changes in 19/20 explicitly qualified |
| Compute/cache/testing | Generic examples omitted newer and older API differences | 15 cache invalidation, 20 SQL-backed computes, verified TransactionCase savepoints |
| Version notes | Broad inheritance and unsupported master-only claims | Explicit deltas and version-isolated generated metadata |

## Claim matrices

The three subject reports provide 52 claim rows across all five versions, with
verified, qualified, and unresolved statuses. A qualified cell is not a runtime
pass; unresolved claims are excluded or require target-source inspection.

- [Controllers, frontend, module lifecycle and views](version-audit-frontend.md): 16 rows.
- [ORM, security, testing, jobs and mail](version-audit-orm.md): 16 rows.
- [Accounting, stock and multi-company](version-audit-business.md): 20 rows.

## Pinned official evidence

Documentation and implementation repositories have separate revisions. A documentation
commit does not pin the source used to generate autodoc. Selected source files were
downloaded at the following commits and SHA-256 checked locally. The source archive
is evidence outside the package, not an Odoo checkout or runtime dependency.

| Series | Documentation commit | Source commit |
|---|---|---|
| 15.0 | `f6b84ed59624ba8f0db2b1d0f7097e435550bb7e` | `3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187` |
| 17.0 | `fbf3e3a6ef0bda7c30b28f213848deca17c2a872` | `6f00fdadb875342de2d14a179f25431f93cd63c9` |
| 18.0 | `ca129a822019682bd32552e4cbabba2520d1308e` | `55f9d29cd13c935226c2b6e48eb661bc89310e8b` |
| 19.0 | `de94dcddba224a1ece042792fa444e7ba0c31fdf` | `9dea17e805e1f513416b53c566895df26f0f560d` |
| 20.0 | `3efea922210a1451b0e48c58a33706b04c4786c1` | `006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754` |

Local evidence manifests:
- `references/odoo-official-docs/manifest.json`
- `references/odoo-official-source-audit/manifest.json` (73 selected files, including upstream licenses).

Reports link to immutable source commits; archived files are listed individually
in the manifest. Supplemental branch observations are labelled separately.

## Additional version-note and upgrade checks

| Claim | 15 | 17 | 18 | 19 | 20 | Evidence |
|---|---|---|---|---|---|---|
| Migration entry point and pre/post/end phases | Verified | Verified | Verified | Verified | Verified | Pinned odoo/modules/migration.py; 17+ upgrade_scripts.rst |
| Both migrations/ and upgrades/ directories | Verified | Verified | Verified | Verified | Verified | Same migration loader and corresponding docs |
| Installed/incoming version selection for scripts | Verified | Verified | Verified | Verified | Verified | Loader version comparison; not evidence that a particular migration ran |
| fields.Domain and models.Constraint | Not asserted | Not asserted | Not asserted | Verified | Verified | ORM docs and orm/domains.py, orm/table_objects.py |
| Runtime source-install baseline | Python3.7+/PG12+ | Python3.10+/PG12+ | Python3.10+/PG12+ | Python3.10+/PG13+ | Python3.12+/PG16+ | source.rst per snapshot; release.py for newer precise bounds |

Project deployments and dependency support may impose tighter runtime requirements.
The migration procedure now also records the source-verified 15 loader contract.

## Validation

- Full package test suite: **737 passed**.
- Focused version/guideline/skill tests: **83 passed**, including five new generated-guidance boundary cases.
- Ruff on modified Python registry/tests: passed; git diff whitespace check passed.
- Temporary installation: 90 skill files and each of the five version-note sets delivered; no local book paths required.
- Pinned source manifest: all 73 successful downloads verified against SHA-256 metadata.

These checks validate package behavior and delivery, not Odoo business operations.
No wheel was rebuilt in this pass. Versions 14 and 16 retain earlier support facts
and were not re-audited here.

## Remaining findings and limits

1. **Odoo 20 runtime access introspection: fixed in the follow-up.**
   `list_access_rights` now selects the connected server's registered security
   schema, queries `ir.access` permissions/restrictions separately on 20, and
   preserves operation/domain semantics and independent pagination. Older servers
   retain their ACL/rule response. Regression tests reproduce the removed-model
   query, stale configuration, operation mapping, compaction, empty pages and
   failure handling. This is a source-checked implementation with mocked RPC tests;
   it has not been exercised against a live Odoo 20 server.
2. Dynamic/inherited field settings, edition/localization behavior, tax rounding,
   reservation, payment delivery, and transaction scheduling still need tests on
   representative disposable databases. Private API signatures are not universally
   certified by a documentation example.
3. Exact numbercall removal, complete company-dependent storage migrations, and
   every provider/valuation override remain outside verified shared rules.
4. Some official prose is stale: the subject reports identify source conflicts.
   Use the pinned implementation for exact API facts and record the discrepancy,
   rather than treating the docs or a book as proof of unavailable fields.

The useful knowledge is retained in packaged skills, references, version notes,
and compatibility metadata. The local book/documentation/source corpora may be
kept or removed independently; full book extraction is a separate outstanding task.


## Access-introspection fix validation

The follow-up regression first failed because the 20 path queried
`ir.model.access`. The corrected tool selects the live registered server schema,
keeps permission/restriction domains, decodes all 15 operation selections and
retains per-list pagination/totals. RPC failures propagate rather than triggering
a legacy-model fallback. The 15/17/18/19 legacy paths were regression-tested,
including stale configuration in both directions.

Validation after the fix: **767 package tests passed**, including 30 dedicated
access-schema cases; Ruff passed, formatting passed for changed Python files,
and mypy passed for all 94 source files. Diff whitespace checks passed. The
query field names and semantics were compared with the pinned 20 official
`ir_access.py` implementation. No live Odoo 20 server was available for execution.
