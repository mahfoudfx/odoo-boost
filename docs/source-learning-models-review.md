# Source extraction: fields, inheritance and environment workflows

Reviewed 2026-11-03. This final batch for the current consolidation covers the
selected Python/XML/CSV/JS/SCSS/Markdown files in Chapters 4 and 8 of both the v17
and v19 cookbook companions. It complements the model-method/security review;
it does not claim that all EPUB explanations or all installed application behavior
were reviewed.

## Coverage

The selected families contain **914 paths / 210 distinct contents**. **190 new
representative contents** were read as complete files or complete diffs against
already-read contents; **20 contents** have prior exact-hash reading lineage.
The review compared **50 addon contexts** for imports, declared data/demo/assets,
dependencies and hooks. All selected Python and XML files parse, including files
whose framework contracts are nevertheless wrong or incomplete.

The evidence supplied for consolidation is `/tmp/source-models-evidence.json`.
It lists exact new representative files, all selected mappings, prior evidence
and addon contexts. Repeated paths remain pending contextual completion; none is
automatically certified by hash equality. Origins of retained lessons below are
**code examples**, not new book prose.

## Experience retained

| ID | Source stimulus and senior development decision | Project value / disposition |
|---|---|---|
| SM-01 | The decimal-precision and monetary recipes separate a scalar precision choice from a currency-bearing amount. A rent `Monetary` field uses a currency relation; choose and populate that currency deliberately rather than treating the amount as an unqualified float. Keep comparison/rounding aligned with the business currency or unit precision. Defaults and `required` in the form are not substitutes for a server invariant. | Positive field-design scenario; confirms existing accounting/model guidance without imposing one precision on every domain. Note-only. |
| SM-02 | Hierarchy recipes use parent/inverse fields, cycle checks and optional indexed `parent_path` storage. `_parent_store` accelerates hierarchy queries; it does not replace cycle policy. V17 enables it; the v19 Chapter4 recipe comments it out but still checks cycles. Use the target-series recursion/cycle API. | Explains the tradeoff between simple adjacency and maintained hierarchy paths; test cycles, reparenting and subtree queries. `models.ValidationError` in v17 is unconventional but not an undefined name: pinned17 models imports that exception. Note-only. |
| SM-03 | Constraint declarations and Python checks solve different invariants. Unique room numbers belong to a database constraint; a negative-rent checker is a recordset callback. The v17 callback reads scalar `self.rent_amount`, while the v19 Chapter4 recipe correctly iterates records; v19 Chapter8 later regresses to the scalar form. Changes must be compared per snapshot, not inferred from edition labels. | Confirms database and server validation boundaries; new batch regression scenario with one negative record among multiple creates/writes. Tests must use ordinary ORM calls, not only form widgets. Note-only. |
| SM-04 | Compute/inverse/onchange must represent the same business quantity. The duration compute initially subtracts dates in days; later onchange computes calendar-month difference, but inverse still adds `timedelta(days=duration)`. The v19 label says months even where the initial compute yields days. Several computes assign only when both dates are present, and display-name computes read name/code but declare only code dependencies. | Concrete semantic/freshness scenarios: missing dates, input removal, month boundaries, editing name, inverse roundtrip and multi-record recompute. Define the quantity and invalid-input policy before changing code. Existing compute/testing guidance confirmed; note-only. |
| SM-05 | Related fields are projections with a dependency and access contract. The student hostel relation traverses room→hostel; the v19 Chapter8 room-number projection is stored with `precompute=True`. Choose storage/precomputation from search needs and creation/batch behavior rather than assuming precompute is always faster. Related fields default to readonly/nonstored and superuser computation, so review field groups and what a projection exposes. | Adds concrete projection/recompute/access review scenarios. Official Field docs warn that explicit/default values can disable precomputation and single-record creates can make it counterproductive. Note-only. |
| SM-06 | Distinguish in-place extension, new-model inheritance, delegation and an abstract mixin actually consumed. V19 adds student fields through `_inherit`; room-copy uses a new `_name` with `_inherit`; delegation uses `_inherits` plus partner link. V17 delegation removes name/active but never enables `_inherits` or `delegate=True`; its commented alternative does not execute. Both archive examples define `base.archive` but the room model never includes it in `_inherit`, so its behavior is not automatically mixed in. | New concrete architecture/import-contract counterexamples; test field/method availability, delegated record ownership/access and lifecycle. Delegation carries fields, not parent methods. Note-only. |
| SM-07 | A polymorphic Reference trades database foreign-key enforcement for heterogeneous targets. The v19 complaint model limits choices to room/student; v17 builds a model list from metadata. Neither choice list establishes authorization to disclose or operate on the referenced record. Relational table/column names also form schema history: v19 changes an explicit many-to-many column spelling in Chapter4, while Chapter8 carries the older spelling. | Adds target-model/access/deletion and upgrade-schema checks. Avoid casually renaming relation columns or replacing a Many2one with Reference as though only UI changed. No existing-database relation migration is certified. Note-only. |
| SM-08 | Context, effective user, elevation and company scope are separate. `is_hostel_room` context controls whether a public removal method writes; callers can supply that flag, so it is flow metadata, not authorization. Assignment creates a room with sudo after checking paid status; that does not by itself validate caller permission, company ownership or the supplied student. The sampled models largely omit company policy. | Confirms existing security/multi-company rules with exact examples. Preserve current context unless replacement is deliberate; `sudo` keeps user identity while bypassing rights, `with_user` changes actor, and `with_company` selects company-dependent evaluation rather than a document-domain filter. Explicitly choose shared versus company-restricted domain policy. Note-only. |
| SM-09 | A wizard is an input adapter to a business operation. The sample trusts `active_id` and updates student room/hostel/date directly, without repeating the paid-state check from the earlier assignment method. The v17 “server onchange” recipe imports test helper Form into business code and references demo room data; the v19 recipe instead simply clears room_id despite its carried recipe title. | New design/testing scenarios: missing/wrong-model/nonexistent/denied selection, unavailable room, company mismatch, state transitions and installation without demo data. Keep reusable server logic in a deliberate method; use Form to test UI semantics rather than assuming an onchange establishes ORM invariants. Note-only. |
| SM-10 | Parameterized SQL prevents value interpolation but does not restore record rules or cache coherence. The v17 category query is parameterized; v19 wraps it with SQL and loops records, but both queries select every room in the chosen category, not only selected record IDs. Neither sample flushes relevant pending values or supplies a separate row-visibility policy. | Useful exact query-review case: intended scope, access/company policy, targeted flush and number of repeated queries. SQL writes additionally require invalidation/dependency notification. Existing performance/security guidance confirmed; note-only. |
| SM-11 | A SQL report model has its own access and measure contract. `_auto=False` availability model explicitly creates a view, uses room-based IDs and aliases columns to fields. It declares the rent amount as Integer and grants managers CRUD although exposed as an analytical pivot. Match field/currency semantics, intended read-only access, row policy and aggregation to the view; test joins for duplication. Parent-model rules are not automatically an SQL predicate. | Extends reporting extraction with a concrete model/view/ACL review scenario. Do not infer that a readonly field attribute prevents direct server writes, or that a SQL-backed model is automatically safe because its menu is analytical. Whether this view accepts database writes was not tested. Note-only. |
| SM-12 | Lifecycle hooks require narrow ownership and reversible intent. Both editions' hook recipe registers pre/post/uninstall functions. The pre hook deletes ir.model.data by model name without module ownership scope; the uninstall hook performs an unfiltered user search and attempts to archive every returned user. This is unrelated-account side effect intent, not valid module cleanup. Constraints may stop it; no successful execution is claimed. | Strong source-selection/operational lesson: inspect hooks before installing or uninstalling teaching addons; retain originals as evidence, construct a scoped replacement only for an actual requirement. Test install/update/uninstall independently on disposable databases. Note-only; no hooks executed. |

## Official verification

Documentation commits: 17 `fbf3e3a6ef0bda7c30b28f213848deca17c2a872`,
19 `de94dcddba224a1ece042792fa444e7ba0c31fdf`. Separate implementation commits:
17 `6f00fdadb875342de2d14a179f25431f93cd63c9`,
19 `9dea17e805e1f513416b53c566895df26f0f560d`.

- [19 ORM reference](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/orm.rst): assignments/dependencies/inverses, stored/groupable computes, related defaults, inheritance variants, hierarchy paths and SQL coherence.
- [17 fields implementation](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/fields.py): Monetary currency semantics, Reference without a database FK, compute/related defaults and precompute tradeoffs.
- [19 Field base](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/orm/fields.py): current precompute and compute_sudo defaults. The stored/related defaults differ from a blanket claim that every computed field always runs as superuser.
- [17 decorators](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/api.py): constraint field triggers and onchange pseudo-record contract.
- [19 environment operations](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/orm/models.py): `sudo`, `with_user`, `with_company`, `with_context`, recordset and model behavior.
- [19 company guidance](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/company.rst): active-company evaluation, company context dependencies, consistency and scope.
- [19 security](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/security.rst): caller-controlled public methods, field groups, direct ORM and SQL boundaries.
- [19 SQL report how-to](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/create_reports.rst): `_auto=False`, readonly field design, model ACLs, column aliases and join-duplication tests.
- [19 manifest/hook contract](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/module.rst): environment hook arguments and module-specific setup/cleanup purpose.
- [17 testing](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/testing.rst): Form is a testing utility; this does not establish production wizard/business behavior.

Official checks used local pinned files. Autodoc-only entries were supplemented
with implementation where the exact default/API mattered. No new claim that
company-dependent storage is the same across versions was introduced.

## Deferred candidates and validation

The settings examples were read, including v19 XML `company_dependent="1"` on
a setting whose Python field is only a group toggle. Markup alone does not prove
company-dependent persistence. Exact res.config.settings behavior, legacy XPath
compatibility and the v19 security file's `implied_by_ids` target-model choices
need matching implementation/schema checks before promotion into guidance.

All selected Python/XML parsers passed; representative hashes, prior lineage and
context counts were checked. No model was imported into a live registry, no schema
or data was changed, no test or SQL query ran in Odoo, and no hook was executed.
The useful additions are source-backed decisions, tradeoffs and counterexamples
for existing model/compute/security/upgrade/report skills. Existing correct rules
did not require rewriting. Runtime reproduction and contextual completion of
remaining repeated paths remain separate work.
