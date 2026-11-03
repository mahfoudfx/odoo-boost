# Comprehensive source scan plan

Status: automated inventory complete; systematic reading remains in progress.
The [current run](source-learning-current-run.md) records coverage and retained
results, including the [Essentials intake](essentials-examples-review.md). Follow the
[workflow](source-learning-workflow.md) and update the [ledger](source-learning-ledger.md)
after each batch. Existing focused extraction is a baseline, not completed coverage.

The [open-gap tracker](source-learning-gaps.md) gives explicit closure criteria
for the deeper topics, every distinct example, runtime validation and acquisition.
Of the 47 original URL failures, five remain unresolved; the tracker records the
recovery and alias evidence. Full reading and original-addon runtime coverage remain open.

## Stage 1 — Establish the coverage denominator

Enumerate EPUB documents and section headings, Cybrosys manifest URLs and physical
pages, and every companion recipe/file. Record hashes and source versions in the
unit records defined by the workflow. Include non-code assets as contextual units.
Read EPUB navigation/spine to distinguish chapters from front matter; the HTML
document counts in the register are not chapter counts.

Group exact-content duplicates without discarding paths. Compare chapter snapshots
and recipe deltas, then map equivalent v17/v19 recipes. Byte deduplication reduces
reading effort; contextual review is still needed. Match by topic rather than
assuming chapter numbers or names are stable. Reconcile the 761 Cybrosys successful
manifest entries with 749 distinct saved text paths; classify repeated mappings
and the 47 retrieval failures. Attempt failed inputs through their official source
URLs during execution and retain persistent failures as gaps.

Exit: every available unit has a stable ID and initial status; every missing input
is listed; per-source totals reconcile. Migrate known historical locators as partial
coverage only when their exact scope is supported by a report.

## Stage 2 — Read by topic and compare implementation

Use the order below to tackle safety and high reuse first, then finish the entire
inventory. Each row is a workstream split into chapter/recipe batches, not a single
unbounded review. Revisit sampled topics to close untouched sections and files.

| Order | Workstream | Experience to extract and challenge |
|---|---|---|
| 1 | ORM, fields, inheritance, security, transactions | Batch semantics, dependencies, compute/search/inverse tradeoffs, extension contracts, company scope, access escalation, SQL/cache coherence and atomicity |
| 2 | Module structure, data, views, upgrades | Dependency order, identifiers, install versus update, hooks, XPath resilience, schema/data conversion, invalid data and recovery |
| 3 | Testing, debugging and performance | Test discovery/isolation, fixture quality, query-count measurement, profiler use, realistic regressions, logs and reproducible diagnosis |
| 4 | Controllers, RPC, integrations and payments | Trust boundaries, authentication, CSRF, validation, pagination, idempotency, callbacks, retry/reconciliation and external failures |
| 5 | OWL, web client, website and reporting | Lifecycle/state, services, assets, extension mechanisms, builder behavior, QWeb, report security, accessibility and browser tests |
| 6 | Automation, wizards, mail and translations | Scheduler budgets, retry boundaries, transient inputs, recipient policy, delivery assumptions, extraction and translation lifecycle |
| 7 | Stock, accounting and multi-company | Supported business operations, rounding/UoM, partial moves, reservation, valuation, fiscal positions, reconciliation and cross-company consistency |
| 8 | Functional domains across Community/Enterprise | Sales, purchasing, CRM, manufacturing, HR, projects, subscriptions and other inventoried modules: states, invariants, extension points and edition/localization limits |
| 9 | POS, IoT, deployment and operations | Frontend/offline boundaries, device protocols, configuration, backups/restores, workers, secrets, upgrades and troubleshooting |
| 10 | Residual inventory sweep | Every remaining setup chapter, appendix, recipe, configuration, test and asset; record useful lessons or an explicit no-addition disposition |

For each workstream, pair prose with code and tests where available. Trace a
representative operation from entry point through ORM/business operation, permissions,
side effects and failure handling. Compare the author's intent with what the code
actually does. Record maintainability choices and the limits of each approach.

Exit per batch: exact units reviewed, lessons/dispositions logged, official checks
recorded, justified additions integrated and appropriately checked. Remaining units
stay pending. A topic title alone never establishes complete topic coverage.

## Stage 3 — Verify and retain useful outcomes

Verification happens inside every reading batch, not after the library is read.
Consult the local pinned official docs first, and matching official implementation
for exact API behavior or contradictions. Browse official sources when local
evidence is missing or a current release/revision is requested. Record source and
documentation revisions separately; treat moving development branches as snapshots.

Use original, minimal examples when a concept benefits from executable demonstration.
State the Odoo series, addon dependencies, setup, expected behavior and failure
case. Execute against a disposable matching server where available. Otherwise keep
the example labelled unexecuted and avoid claiming runtime correctness. Use package
tests for implemented tools or guidance delivery, with their narrower evidence scope.

Prefer concise decision guidance in existing skills when it fits; use a linked
reference for detailed patterns. A new independent capability can justify a new
skill or tool. Already-correct guidance needs only a confirmation record. Interesting
but unsupported claims remain research questions, not developer instructions.

## Stage 4 — Close coverage and sustain learning

Audit the unit ledger for unread units, unresolved lessons, missing official
evidence, broken project links and context-free duplicate decisions. Publish totals
for inventoried/read/duplicate-reviewed/missing units separately from verified
lessons, integrated outcomes and executed examples. Close a source only with these
counts and explicit exceptions. Runtime validation has its own completion status.

For a new book or code repository, register its revision, inventory it and feed its
units through the same stages. Changed sources reopen affected units and linked
lessons. Keep additions proportionate to their value; the goal is better developer
judgment and project capabilities, not a quota of edits or new tools.

Next execution batch: choose one remaining recipe family or book section from
pending coverage. Existing inventory and review evidence should be reused;
the current run lists completed families. Keep the next review explicitly bounded.
