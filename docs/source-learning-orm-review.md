# Source extraction: model methods, overrides and security

Reviewed 2026-11-03. This bounded pass covers all selected text/code files in
Chapter 5 and Chapter 10 of both v17/v19 cookbooks. It supplements the earlier
compute, company, transaction and test reviews; it does not establish full review
of Chapter 4 field modeling or Chapter 8 advanced ORM/workflow recipes.

## Coverage and method

The selected families contain **545** Python/XML/CSV/JS/SCSS/Markdown paths and
**136 distinct contents**. **103 new representative contents** were read as complete
files or complete diffs; **33 contents** already had exact-hash reading evidence
from prior reviews. Existing content evidence was reused without marking every
new path contextually complete. **45 addon contexts** were compared for manifest
version/dependencies, data/demo/assets and root/model imports.

The evidence file supplied to the consolidating reviewer is
`/tmp/source-orm-evidence.json`, with exact new fully read paths, all selected
path/hash/representative mappings, prior-content lineage and addon context records.
Hashes support reading reuse, not runtime compatibility or access correctness.

All retained lessons below originate from **code examples**. No new EPUB chapter
reading is claimed in this pass. Paths below are relative to each edition's
nested `*-Examples` root.

## Useful decisions and tradeoffs

| ID | Experience extracted from the examples | Project benefit and disposition |
|---|---|---|
| SO-01 | Make state-transition failure semantics explicit. `Chapter05/01_model_methods` silently continues when a transition is disallowed; `02_error_messages` raises a translated `UserError`. Both iterate records. Decide whether a multi-record action is all-or-nothing, a validated subset operation or a per-record report; an ordinary propagated framework error rolls back the request rather than preserving earlier writes. | Adds a concrete decision pair for action design. Test mixed valid/invalid records and repeat actions, not only a valid singleton. Existing ORM/transaction rules confirmed; note-only. |
| SO-02 | Choose `search` for a database scope and `filtered`/`mapped`/`sorted` for a recordset already selected under a known policy. The filter/traverse/sort recipes show these roles but first search all visible records. That can be appropriate for a small demo, not a default query strategy. Mapping relational fields returns a union of records; mapping scalar names returns values, and mapping is not a guaranteed business ordering. | Preserves the convenience of recordset operations while prompting bounded database queries, stable explicit ordering and representative query/latency checks when volume matters. Note-only. |
| SO-03 | Nested relational commands express creation of an aggregate. `04_creating_new_record` creates a parent and two child categories in one operation, using relational commands. Keep the comodel and inverse relationship correct, allow normal authorization/constraints to run, and test that all children belong to the intended parent. Use the target-version Command API or serialized triples appropriate to the boundary. | Positive original scenario for relational modeling; no need to copy the whole teaching addon or introduce another helper. Existing pattern guidance confirmed; note-only. |
| SO-04 | Override a business operation through `super` while preserving its return contract and batch semantics. The termination extension sets/clears dates before calling the parent. Its scalar `category_id`/category settings access can be ambiguous for mixed-category batches; zero values are replaced by `or 10`, which needs a defined business meaning. The v17 extension still labels itself `16.0.0`. | Useful seam/contract lesson: decide singleton versus recordset API, test category-dependent values and rollback after parent rejection, and select source versions deliberately. Note-only, not an automatic rewrite of the date policy. |
| SO-05 | A decorator change is a calling-contract change. V19 `Chapter05/12_extend_create_and_write` uses `@api.model_create_multi` but calls `vals_list.get`, although that parameter is a list of dictionaries. The branch is entered only for nonmanagers, so manager/admin happy paths hide it. Both versions' write checks use `values.get('remarks')`, allowing an explicit false/empty update to pass the intended “cannot modify” policy. | Concrete batch and actor test scenarios: one dict, list, empty input, restricted field absent/present/cleared, ordinary user and manager. Test key presence when the business policy forbids all changes; use field-level groups when that is the intended read/write policy. Note-only. |
| SO-06 | Name-search customization must preserve caller domain, result shape, limit and target-release method signature. The v17 example's `_name_search` accepts old `args`/`name_get_uid` parameters, while pinned17 caller passes `order=` and base expects `domain`/`order`. It also adds three binary OR operators for only three leaves, an invalid domain fragment. V19 uses a different `name_search(domain=...)` surface and display-name hooks. | Adds exact migration counterexamples; test empty search, negative operator, existing caller restrictions, limit and access. Prefer supported display-name/search extension points for the actual series rather than carrying a legacy override forward. Note-only. |
| SO-07 | Aggregation is a data contract, not merely a faster loop. `14_read_group` groups average room cost/rent by category. Decide whether zero values are excluded, what unassigned categories mean, and whether category fields are stored/groupable. Distinguish the dict-return `read_group` sample from tuple-return `_read_group` APIs. Preserve access/company/domain semantics when changing implementation. | Adds concrete aggregation acceptance criteria to performance guidance. Query count improvements alone cannot prove equivalent results; note-only. |
| SO-08 | Validate the full access matrix: model ACL grant, applicable record rules, field groups and caller identity. Chapter10 manager implies user; the user rule matches `is_public`, while the manager rule allows all. Their group rules union, so manager inheritance does not accidentally restrict the manager to public records. The rule label says “own hostel” although the actual domain is public status, illustrating why policy comes from expressions rather than labels. | Positive effective-policy example and test matrix: ordinary internal user, application user, manager, overlapping groups, public/private records and restricted fields. Existing security guidance confirmed; note-only. These rules describe the inspected17/19 schemas, not the separately audited20 schema. |
| SO-09 | Model field groups and UI visibility are different boundaries. The examples restrict `notes` and other fields with ORM groups; later recipes restrict menus/buttons in XML. Explicit reads/writes to a restricted ORM field must still be denied to unauthorized users even if they call the model directly. A broad ACL for category records is not narrowed merely by hiding its menu. | Adds direct-RPC acceptance scenarios and confirms existing field/security guidance. Test the child/auxiliary models as well as the main screen. Note-only. |
| SO-10 | Public methods that sudo-write require their own authorization and record/state/company checks. V19 `Chapter10/06_superuser_access` exposes `add_details`, which calls `self.sudo().write` on a manager-restricted field without checking the caller or selected records. The next recipe hides the button with XML groups but keeps the Python method, so direct method access remains the review boundary. | Concrete privilege-escalation counterexample, conditional on installed routes/model policy. Do the permission decision before a narrow elevation; a button group is not the implementation of that decision. Note-only; no live exploit is claimed. |

These conclusions retain both good design choices and defects. They do not
require modifying already-correct project rules. The examples remain intact as
evidence; no runtime lookup of the corpus or copied implementation was added.

## Official verification

Relevant official files were read locally at pinned documentation commits
17 `fbf3e3a6ef0bda7c30b28f213848deca17c2a872` and
19 `de94dcddba224a1ece042792fa444e7ba0c31fdf`; exact APIs were checked against
implementation17 `6f00fdadb875342de2d14a179f25431f93cd63c9` and
19 `9dea17e805e1f513416b53c566895df26f0f560d`.

- [17 model implementation](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/models.py): `name_get` deprecation, `name_search`/`_name_search` signatures and caller, create/read/write contracts.
- [17 create adapters](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/api.py): single versus multi-create adaptation and list-of-dictionaries contract.
- [19 model implementation](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/orm/models.py): current `name_search`, display-name search, `mapped`, `filtered`, `grouped`, `sorted` and recordset access. `mapped` of records is not an ordering guarantee.
- [19 ORM reference](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/orm.rst): relations/commands, API decorators, binary prefix domain composition and recordset operations.
- [19 security reference](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/security.rst): additive ACLs, global/group rule composition, ORM field groups, untrusted public method arguments and explicit elevation.
- [19 coding guidelines](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/contributing/development/coding_guidelines.rst): framework-owned transactions and appropriate extension practices.

The activation-feature/settings recipes were also read for context. Their legacy
settings XPaths and exact `res.config.settings` persistence internals were not
verified against the matching base_setup implementation, so they are retained as
unresolved candidates rather than promoted into version-specific instructions.

## Validation and limits

All selected Python/XML files parse in the current parser; that does not validate
runtime method/decorator contracts, Odoo view schema, external-ID resolution or
installed effective access policy. The new findings specifically show why parsing
is insufficient. Context and content mapping counts were checked for consistency;
no duplicate path was automatically declared contextually complete.

No addon installation, RPC, record mutation, domain execution or security test ran.
Remaining Chapter4/8 contents, settings implementation checks, actual ordinary-user
matrix tests and mixed-record business cases remain open. These research notes
provide new traceable scenarios for existing ORM, security and testing guidance.
