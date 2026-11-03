# Source extraction: testing, debugging, performance and data upgrades

Reviewed 2026-11-03. This pass reads all distinct selected text/code contents in
the two Chapter 6 data families, v17 Chapter 18 testing, v19 Chapter 16 testing,
and v19 Chapter 7 debugger example, with selected performance prose. The available
v17 companion repository has no Chapter 7 or performance Chapter 21 directory;
the v19 repository has no performance Chapter 18 directory. Their EPUB performance
chapters supply prose and inline examples instead.

## Coverage method

The selected families contain **483** Python, XML, CSV, JS, SCSS and Markdown file
paths with **114 distinct byte contents** across both series. One representative
of each distinct content was read in full, or as a complete diff against an
already-read representative. Diffs retained whitespace and comments, so no changed
code was discarded by normalization. The remaining repeated paths are content
matches, not automatically completed contextual reviews.

The review compared all **35 addon contexts** in the selected families: manifest
version, dependencies, declared data/demo/assets and root/model/test imports.
This identifies which files are active and what each snapshot actually adds.
The integrating evidence file lists 114 representative paths and all 483 mappings;
it does not label every repeated path runtime-verified or contextually complete.

EPUB scope is partial: v17 `OEBPS/B20997_21.xhtml`, selected SQL/transaction and
profiling material; v19 `OEBPS/Text/Chapter_18.xhtml`, selected grouped/batch/SQL
and profiler material. The v17/v19 debugger chapter EPUBs were inventoried but
not deeply read in this pass. No book prose or sample implementation is copied
into the package.

## Useful experience and concrete counterexamples

| ID / origin | Source stimulus and lesson | Practical project benefit / disposition |
|---|---|---|
| SQ-01 — code example | Test discovery, fixture setup and assertions are separate checks. The ordinary/tagged v17 tests reference fixtures they create. V19 setup renames partners to Liam/Amelia but retains `partner_nikul` in the assertion; its debugger-test snapshot changes that to undefined `partner_vandan`. Both methods test valid transitions only. | Confirms testing guidance; adds edition-diff fixture validation and negative-transition/multi-record scenarios. Notes retained; no Odoo pass claimed. |
| SQ-02 — code example | Compare the behavior tested, not just QUnit→HOOT syntax. V17 color test clicks a pill and checks the active state; v19 HOOT test only counts ten pills. V19 widget now reads `dataset.value`, a string, and stores it without numeric conversion, while the template compares color values loosely. Test persisted field type/value, readonly handling and click result rather than treating rendering as full behavior coverage. | New concrete regression-review scenario. Syntax migration can reduce behavioral coverage. Framework conversion behavior remains to be checked at runtime; a type mismatch is a review question, not a claimed browser failure. |
| SQ-03 — code example | A registered tour is not an executed integration test. Neither selected testing family supplies a Python `HttpCase.start_tour` wrapper. V19 tour clicks New then Save without entering the required `name`/`room_no`; its fixture creates a tour registration, not defaults for those required fields. V17 tour likewise does not constitute a CI result merely by loading in backend assets. | Confirms distinction among onboarding tours, unit tests and end-to-end checks. Useful acceptance criteria: complete required inputs, assert persisted result, run through a test wrapper. Notes retained. |
| SQ-04 — code example | Stable external IDs still have model types. V17 Chapter6 demo creates author IDs as `res.partner` and uses their integer IDs in a `member_ids` command whose comodel is `hostel.room.member`; matching integer values do not make these the same record. This demo file is not in the sampled v17 manifests' demo list, so it is an unloaded example defect rather than proof the active install fails on that file. V19 uses proper `hostel.student` references in its corresponding demo. | Adds a concrete typed-fixture review rule and reinforces checking manifest reachability before reporting an installation defect. Notes retained. |
| SQ-05 — code example | Prove the migration is selected before reviewing its transformation. V17 sample manifest stays at `17.0.1.0.0` and uses `migrations/17.0.1`; v19 has older `17.0.1`, `19.0.1` and full `19.0.1.0.0` directories while the incoming manifest is `19.0.1.0.1`. Pinned loaders treat names with at most two dots as major-less module versions, prefixing the server series. For an ordinary `19.0.1.0.0`→`19.0.1.0.1` update, the full `19.0.1.0.0` script is not newer than installed, while `19.0.1` expands to `19.0.19.0.1`, outside the incoming range. | Extends the existing upgrade procedure with concrete directory-selection counterexamples. Record installed/incoming versions and expected selected scripts explicitly; a fresh install does not execute update-only scripts. No actual migration ran. |
| SQ-06 — code example | Schema, SQL columns and registered fields are distinct migration interfaces. V17 model declares `fields.date` rather than official `fields.Date`; both old post scripts ignore the fetched row ID and update fixed `id=1`. V19 newer pre script adds/copies `admission_date_old` as a SQL column, but its post script searches/accesses that name through ORM without a matching declared field in the inspected model. Empty/invalid/ambiguous dates need policy, and transformed rows need count/value checks. | Adds failure scenarios to data-preservation review. Under the inspected model definition, a raw SQL column is not automatically an ORM field. Keep conversion against legacy columns in SQL or deliberately expose a verified field/migration interface. Notes retained; exact installed overrides remain relevant. |
| SQ-07 — both | Flush is not commit. V19 performance prose uses `self.flush()`/`recordset.flush()`; pinned ORM exposes `flush_model` and `flush_recordset` for this use. Flush relevant pending values before SQL reads; after SQL writes invalidate affected fields and notify dependency changes. V17 prose's “commit only if sure” must be replaced by framework transaction ownership, with explicit exceptions only for owned cursors/framework job contracts. | Confirms existing SQL/cache/atomicity guidance with exact obsolete-call counterexamples. Avoid introducing per-record commits as a performance technique. Recoverable exception continuation needs bounded savepoints; normal errors can propagate atomically. Notes retained. |
| SQ-08 — code example | XML operations have installation/update and argument-shape semantics. Both data families demonstrate external-ID updates, `noupdate`, deletion and function calls. V17 `<function>` passes `ref('room_category_all')`, an integer, while its method accesses `category.id` and searches a `category_id` absent from that model. V19 no-argument function increments every room's rent and is inside `noupdate`, so it is not a reliable recurring update migration. | Adds concrete function-call and side-effect review scenarios; distinguish data initialization, repeatable corrections and versioned upgrades. Existing module/upgrade guidance confirmed; notes retained. |
| SQ-09 — both | Measure performance against representative data, user/company scope and cache state. The v17 populate recipe declares dependent models/sizes and uses population factories; it is useful for larger data but not an assertion of realistic distributions. Both performance chapters describe profiler overhead and cache effects. SQL collector helps count/find queries; repeated timing after disabling profiling measures the real change. | Provides a reproducible measurement checklist: baseline and candidate, cold/warm distinction, query count plus latency, flush inside the measured scope and unchanged business/access results. Official17 places `self.profile()` outside `assertQueryCount` to include exit/flush queries. Notes retained; no benchmark executed. |
| SQ-10 — book prose and inline code | Avoid universal query-count promises. V19 prose claims batch create internally inserts once per record; pinned19 `_create` batches rows into multi-row INSERT statements up to `INSERT_BATCH_SIZE`. Nor does that prove a whole business create is one query: defaults, recomputes, inheritance and hooks may add work. Its grouping discussion uses tuple-return `_read_group`, unlike dict-return examples carried in other chapters. | Retains the decision to batch while rejecting the book's overly broad implementation claim. Verify exact series/result shape and measure total business operation costs instead of deriving performance from API call count. Notes retained. |
| SQ-11 — code example | Diagnose from observable boundaries. The v19 debugger recipe actually exports visible available rooms to an attachment and logs start/count/record/result/error; its broad exception handler logs then raises `UserError`, so it does not continue issuing ORM queries after an error. The method uses `self.id` when nonempty without an explicit singleton contract and builds a whole text payload in memory from an unbounded search. | Useful diagnosis and scale-review example: define accepted recordset shape, keep failure cause observable, consider serialization/escaping and large result size, and distinguish inspected logging from an actual PDB session. No export or attachment was created. Notes retained. |

## Official evidence

Pinned documentation revisions are 17
`fbf3e3a6ef0bda7c30b28f213848deca17c2a872` and 19
`de94dcddba224a1ece042792fa444e7ba0c31fdf`. Implementation revisions are separate:
17 `6f00fdadb875342de2d14a179f25431f93cd63c9`, 19
`9dea17e805e1f513416b53c566895df26f0f560d`. Local pinned copies supplied verification.

- [19 testing](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/testing.rst): explicit test imports, class tags and Python tour wrapper. Its older PhantomJS prose is not treated as current runner evidence.
- [19 HOOT](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/frontend/unit_testing/hoot.rst): unit-test assets, DOM interaction and test helpers.
- [17 data files](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/data.rst): sequential operations, `noupdate`, `forcecreate`, external IDs and function evaluation.
- [19 upgrade scripts](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/upgrades/upgrade_scripts.rst) and [17 loader](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/modules/migration.py), [19 loader](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/modules/migration.py): update-only selection, version conversion/comparison and pre/post/end phases.
- [17 Date field](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/fields.py) and [19 ORM implementation](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/orm/models.py): field API, `_fields` metadata, multi-row `_create`, flush APIs and singleton field access.
- [19 SQL contract](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/orm.rst): targeted flush/invalidation/dependency protocol.
- [19 coding guidelines](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/contributing/development/coding_guidelines.rst): framework transactions, specific exceptions and savepoint boundaries.
- [17 performance](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/performance.rst): profiler/query-count context, collectors, warm caches, population and qualified batching.

## Validation and remaining work

Read 114 representative contents and complete differences, compared 35 addon
contexts and recorded every selected path/hash mapping. Findings above are code
and documentation conclusions, not results from installing/updating addons or
running Python/browser tests. No benchmarking, SQL/data changes, export, migration
or PDB session occurred.

These notes add useful scenarios to existing testing, ORM, performance, module
and upgrade guidance. No new tool or automatic correction of the source corpus is
needed. Remaining work includes contextual completion of repeated paths, source
families outside this scope, the unreviewed parts of the EPUB chapters, and
runtime reproduction with disposable matching-version databases/browsers.
