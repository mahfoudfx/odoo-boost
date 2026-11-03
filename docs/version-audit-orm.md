# Version audit: ORM, security, testing, jobs and mail

Audit date: 2026-11-03. Scope: the book-extracted guidance in the assigned core
files, computed-field/performance references, and security, compute, cron, mail
and wizard skills. This audits claims and version boundaries; it does not execute
Odoo or certify every installed-module override.

## Evidence baseline

Official documentation snapshots, all under
`references/odoo-official-docs/<series>/<revision>/content/` outside the package:

| Series | Pinned documentation revision |
| --- | --- |
| 15.0 | `f6b84ed59624ba8f0db2b1d0f7097e435550bb7e` |
| 17.0 | `fbf3e3a6ef0bda7c30b28f213848deca17c2a872` |
| 18.0 | `ca129a822019682bd32552e4cbabba2520d1308e` |
| 19.0 | `de94dcddba224a1ece042792fa444e7ba0c31fdf` |
| 20.0 | `3efea922210a1451b0e48c58a33706b04c4786c1` |

Each series' `developer/reference/backend/{orm,security,testing,actions,mixins}.rst`
was inspected for the claims below. Some APIs are included only by autodoc in
these text snapshots. For those gaps the official `odoo/odoo` branch source was
inspected on the audit date. Source references are branch URLs unless a pinned
source manifest is provided by the overall audit; do not mistake a documentation
revision for a source-code revision.

## Five-version matrix

V = verified in explicit documentation or source; Q = qualified API/version rule;
U = exact claim not established and deliberately excluded.

| Claim | 15 | 17 | 18 | 19 | 20 | Evidence and disposition |
| --- | --- | --- | --- | --- | --- | --- |
| Compute assigns all outputs; depends may follow relation paths; inverse enables editing; custom search returns equivalent domain | V | V | V | V | V | `orm.rst`, Computed fields; retain shared contract |
| Ordinary computed-field elevation defaults follow `store`; related computes default elevated | V | V | V | V | V | `Field._get_attrs` in official fields sources; prose in newer ORM docs says default True without this distinction, so source determines actual default |
| `related_sudo` compatibility fallback is supported | V | V | V | V | V | Same field-attribute implementation; explicit `compute_sudo` wins. Prefer explicit `compute_sudo=False` when intended |
| A search method alone enables SQL sorting | Q | Q | Q | Q | Q | False; do not invent an `order` field callback. The 20 source additionally supports `compute_sql`, a separate reviewed API |
| SQL cache handling uses one universal invalidation snippet | Q | Q | Q | Q | Q | 15 ORM docs name `invalidate_cache`; 17/18/19/20 show `invalidate_recordset` and `modified`. Target-specific selection required |
| Separate `ir.model.access` grants plus `ir.rule` filtering | V | V | V | V | Q | 15–19 security docs; 20 has unified `ir.access`, confirmed in actual 20 implementation |
| No-group ACL grants apply to all users | V | V | V | V | Q | 15–19 ACL semantics. In 20, no-group `ir.access` is a global restriction; never reuse old meaning |
| ACL grants add; rule `perm_*` False means inapplicable, not explicit denial | V | V | V | V | Q | Older access model only. 20 operation/domain permission/restriction model has different metadata |
| TransactionCase shares class transaction, isolates test methods with savepoints, closes without commit | V | V | V | V | V | Official `odoo/tests/common.py`, class TransactionCase docstring in each series |
| Test modules must be imported and tags choose installation phase | V | V | V | V | V | `testing.rst`; retain discovery/tag rules |
| `Form` lives at the same old helper path in every series | Q | Q | Q | Q | Q | 15 defines Form in common; 17/18/19/20 explicitly export Form from `odoo.tests` via `.form`. Select import rather than assert old path remains |
| Scheduler progress API can be copied between all versions | Q | Q | Q | Q | Q | 15/17 docs do not establish newer progress helpers; 18 documents `_notify_progress`; 19/20 document `_commit_progress` contract |
| Exact removal version for `numbercall` | U | U | U | U | U | Absence from prose is insufficient proof; skill tells agents to inspect model fields rather than assert removal |
| Mail tracking flags may suppress tracking; discussion is not immutable audit | V | V | V | V | V | `mixins.rst`, tracking context flags in each series |
| Chatter view markup | Q | Q | Q | Q | Q | 15/17 mixins show `oe_chatter` + fields; 18/19/20 show `<chatter/>`; skill labels modern example accordingly |
| Wizard context and public-method recordsets require server validation | V | V | V | V | V | security public-method trust boundary; transient ownership is not permission to mutate target records |

## Concrete corrections

1. Shared security guidance and skill examples now explicitly select the old
   separate access model for 15/17/18/19 versus unified access rights for audited
   20. This supersedes the earlier extraction's incorrect master-only assumption.
2. Removed the incomplete full-address compute example: it lacked its compute
   method and OR-ed component searches, which does not implement full-address
   equality or negative-operator semantics.
3. Qualified SQL sorting and invalidation by version. Added the distinct 20
   SQL-backed compute boundary rather than claiming all non-stored values have
   identical capabilities.
4. Confirmed TransactionCase isolation across all five, including 15. Public
   test-helper imports are distinguished from reorganized implementation modules.
5. Labelled mail form markup by version and retained explicit cron API selection.
6. Removed unsupported blanket claims that `_description` is a universally
   enforced post-v12 requirement and that recordset helpers/search_read should
   mechanically replace all loops/recordset reads.

## Official implementation references

- Fields/defaults in [15](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/odoo/fields.py),
  [17](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/fields.py),
  [18](https://github.com/odoo/odoo/blob/55f9d29cd13c935226c2b6e48eb661bc89310e8b/odoo/fields.py),
  [19](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/orm/fields.py),
  [20](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/odoo/orm/fields.py).
- [20 unified access implementation](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/odoo/addons/base/models/ir_access.py)
  and [official documentation](https://github.com/odoo/documentation/blob/20.0/content/developer/reference/backend/security.rst).
- TransactionCase source: `odoo/tests/common.py` in each of the five official
  branches. Test helper exports: `odoo/tests/__init__.py` in 17/18/19/20.
- [15 ORM/cache reference](https://github.com/odoo/documentation/blob/15.0/content/developer/reference/backend/orm.rst),
  [17 ORM/cache reference](https://github.com/odoo/documentation/blob/17.0/content/developer/reference/backend/orm.rst).
- Scheduled action progress: `developer/reference/backend/actions.rst` in
  18/19/20; no unsupported inference about missing older APIs.

## Limits and verification

This is a static evidence audit of the extracted guidance, not a five-version
runtime test matrix. No stock, accounting, wizard, mail delivery, cron or schema
operation was executed. Source-level defaults do not override explicit field
settings in installed addons. Legacy 14/16 are not part of this requested audit;
new guidance must not claim they were checked. Persistent access migration to
20 requires its own data and behavior tests.

Validation: 50 guideline-composition/skill-installation tests passed after these
changes; `git diff --check` passed. Local corpora remain evidence, not runtime
package dependencies.


## Reproducible source follow-up

Selected implementation files were subsequently downloaded at fixed commits; see
[central audit](version-audit.md) for the source revision table and local manifest.
Links above now use those commits. Only files listed in that manifest were
archived; a branch observation is not proof that unarchived files were compared.
