# What the book collection has contributed

Baseline audited on 2026-11-03. This report reconciles the earlier extraction
reports with the current packaged guidance. It describes retained contributions,
not a complete scan of the library. The original reports supply historical
provenance; current files were inspected to confirm the principal retained rules.
Historical test counts below are reported evidence, not tests rerun for this report.

Subsequent code intake: the [Essentials archive scan](essentials-examples-review.md)
adds 14 code-origin lesson groups and per-file coverage. The v15 companion examples
are now available; the new v17 Essentials ZIP contains metadata only. Historical
source attribution below describes the earlier extraction, before this intake.

## Source attribution

**Book** means explanatory prose in the named book or saved Cybrosys book page.
**Code** means a companion example file. **Both** means the extraction report
records both as input to that lesson. This classification identifies the stimulus;
official documentation and implementation establish the accepted technical rule.
Where the old reports only list a combined sample, attribution remains qualified
rather than guessing which individual sentence caused an edit.

| Collection | Observed useful contribution | Origin and coverage limit |
|---|---|---|
| Odoo 15 Development Essentials, fifth edition | Compute search/inverse choices, framework transaction ownership, manifest/data/portal and company-context questions | Book; selected sections reviewed. All 26 EPUB documents were inventoried, not all deeply read. No companion code contribution is established by the reports. |
| Odoo 17 Development Cookbook, fifth edition | Recordset-safe computes, security/test scenarios, controller inheritance and route trust boundaries, module data/dependencies, company consistency | Both; selected prose and examples. The 3,233-file example inventory contains repeated snapshots, not 3,233 distinct recipes. |
| Odoo 19 Development Cookbook, sixth edition | Prefetch, compute/constraint evolution, test-fixture review, controller APIs, website versus Owl lifecycle distinctions, data-upgrade correctness | Both; selected chapters/examples. The 2,503-file inventory is not full code review or execution. |
| Cybrosys Odoo 18 development book | Wizard validation, chatter delivery/tracking limits, sampled computed-field questions | Book; saved web-book text. No separate runnable companion repository is established here. |
| Cybrosys Odoo 18 accounting book | Invoice correction/payment separation and fiscal-position workflow | Book; selected financial-handling and fiscal-position pages. |
| Cybrosys Odoo 18 Community book | Inventory count/apply workflow and stock unit questions | Book; selected inventory operations. |
| Cybrosys Odoo 18 Enterprise book | Available for future functional extraction | Inventory only is established; no distinct implemented contribution can yet be attributed to this subset. |

The Cybrosys manifest records 761 successful entries mapping to 749 distinct
saved text paths, plus 47 failed URLs. Availability is incomplete and must remain
visible in coverage. Current inventory details are in the
[source register](source-learning-ledger.md).

## Implemented lessons and project value

Paths link to the actual delivery surface. These were mostly improvements to
existing skills and guidelines, rather than newly created skills or tools.

| ID | Origin | Retained addition | Where it helps the project | Official check / provenance |
|---|---|---|---|---|
| B01 | Both: v15 compute prose; v17/v19 room-model examples | Choose stored computes versus equivalent custom searches; assign per record, represent dependencies, distinguish inverse/search/sorting | [ORM guidance](../src/odoo_boost/guidelines/core/orm_best_practices.md), [compute skill](../src/odoo_boost/skills/domain_computed_fields/SKILL.md), [original compute patterns](../src/odoo_boost/skills/pattern_library/references/computed-field-patterns.md). Avoids unnecessary storage and misleading callback examples. | Official ORM compute contract; [first pass](book-reference-review.md), [version audit](version-audit-orm.md). |
| B02 | Book: v19 prefetch discussion | Preserve recordset prefetch; profile query counts and batch only where semantics permit | [ORM guidance](../src/odoo_boost/guidelines/core/orm_best_practices.md), [performance reference](../src/odoo_boost/skills/pattern_library/references/odoo-performance-guide.md). Removes the implication that ordinary record iteration requires explicit reads. | Official ORM/performance docs; first pass. |
| B03 | Book: v17/v19 record-rule sections; exact rule-example lineage not individually recorded | Explain additive ACLs, rule applicability and global/group composition for the older access schema; verify overlapping groups/companies | [Security guidance](../src/odoo_boost/guidelines/core/security.md), [security skill](../src/odoo_boost/skills/security_rules/SKILL.md). Prevents interpreting a false operation flag as a denial. | Official security docs; later audit explicitly scopes these rules to 15–19 and supplies the separate 20 model. |
| B04 | Book: v15 transaction section | Preserve framework transaction ownership; qualify explicit cursor/shell use and raw SQL cache/dependency protocol | [Performance reference](../src/odoo_boost/skills/pattern_library/references/odoo-performance-guide.md). Reduces partial-workflow and stale-cache risks. | Official coding/ORM docs. Cache APIs were subsequently checked by version. |
| B05 | Both: v17/v19 testing prose and v19 ordinary/tagged tests | Accurate TransactionCase savepoints, imports/tags, ORM invariant versus onchange tests, independently constructed fixtures | [Testing guidance](../src/odoo_boost/guidelines/core/testing.md). Better test discovery and isolation; examples are treated as review material. | Official testing docs and TransactionCase source; first pass and ORM audit. |
| B06 | Code: sampled v17/v19 room constraints | Preserve recordset iteration while selecting constraint declarations by target version | [Compute skill](../src/odoo_boost/skills/domain_computed_fields/SKILL.md), [version notes](../src/odoo_boost/guidelines/core/versions/v19.md). Prevents blindly porting singleton assumptions and newer declarations. | Official ORM/source; first pass. |
| B07 | Both: v17/v19 controller sections and Chapter13 path/override examples | Redecorate overridden routes; inherit/replace options deliberately; separate none/public authentication from permission to expose data; bounded queries and escaped output | [Controller guidance](../src/odoo_boost/guidelines/core/controllers.md), [route skill](../src/odoo_boost/skills/controllers_routes/SKILL.md). Retains the inheritance lesson while correcting unsafe production assumptions. | Official HTTP/security docs/source; [pass 2](book-reference-review-pass-2.md). |
| B08 | Both: controller prose/examples supplied the question; official source supplied dispatch details | Correct CSRF/callback trust boundaries and version-selected JSON-RPC spelling/authentication APIs | Same controller delivery surfaces. Supports safer browser writes and authenticated external integrations. | Official HTTP dispatch implementation; frontend version audit. This is not a validated payment-provider integration. |
| B09 | Code: v19 Chapter22 website snippets; corrections additionally driven by official docs | Separate website Interaction methods from Owl component hooks; select RPC/service/module conventions and asset bundles by version | [JavaScript guidance](../src/odoo_boost/guidelines/core/javascript_owl.md), [Owl skill](../src/odoo_boost/skills/owl_components/SKILL.md). Avoids mixing APIs from different component systems/series. | Official Owl/components/services/assets docs; pass 2 and frontend audit. No complete website-builder extraction is claimed. |
| B10 | Both: v15/v19 manifest/data prose and v17 manifests | Accurate manifest requirements, compatible license choice, dependency-driven data/asset order, stable external IDs and deliberate noupdate | [Module guidance](../src/odoo_boost/guidelines/core/module_structure.md). Improves installation/update reliability and dependency declarations. | Official module/data/assets docs; pass 2. |
| B11 | Book-led review; no precise companion-view example is credited | Select tree/list roots, modifiers and chatter markup by version; inspect actual inherited view; keep server authorization distinct from UI properties | [Views guidance](../src/odoo_boost/guidelines/core/views_and_ui.md), [XML view skill](../src/odoo_boost/skills/xml_views/SKILL.md). Prevents modern XML being presented as universal syntax. | Official view docs and 17 validation source; pass 2 and frontend audit. |
| B12 | Book: Cybrosys accounting financial-handling page | Separate posted invoice, credit/debit note, actual refund, reconciliation and stock return; compare balances using currency precision | [Accounting skill](../src/odoo_boost/skills/domain_accounting/SKILL.md). Models distinct business operations rather than implying one action completes all of them. | Official credit-note/payment docs; balance precision from official model source, not attributed to the book. [Pass 3](book-reference-review-pass-3.md). |
| B13 | Book: Cybrosys fiscal-position page | Use the standard fiscal-position/company/localization pipeline; remove unconditional product-tax copying and unverified private mapping calls | Same accounting skill. Produces better invoice design and avoids incomplete generic tax templates. | Official fiscal-position docs and later five-version business audit. |
| B14 | Book: Cybrosys inventory operations page | Distinguish demand, reservation, execution and count/apply adjustments; verify units, tracked goods, partial transfers and backorders | [Stock skill](../src/odoo_boost/skills/domain_stock/SKILL.md). Replaces automatic full-completion advice with business workflow decisions. | Official inventory/UoM docs; exact field/unit/valuation differences came from official source follow-up. |
| B15 | Book: v17/v19 field sections and v15 environment discussion | Correct active-company evaluation, company context dependencies, explicit document scope, relational consistency, shared versus restricted domains | [Multi-company skill](../src/odoo_boost/skills/domain_multi_company/SKILL.md). Separates visibility, active company and data consistency; adds A/B/A+B verification scenarios. | Official multi-company guidance in all five audited versions. No complete company-dependent storage audit is claimed. |
| B16 | Official-doc-led; books are a general automation stimulus, no exact cron book/code input is recorded | Version-selected scheduler progress APIs, bounded batches, transaction recovery with savepoints | [Cron skill](../src/odoo_boost/skills/domain_crons_automation/SKILL.md). Improves long-running job design without inventing universal fields/helpers. | Official actions/coding docs; [automation pass](book-reference-review-automation.md). Exact numbercall removal remains unresolved. |
| B17 | Book: Cybrosys wizard page | Validate caller context, target permissions/company/state; implement a verified business operation behind a structural wizard template | [Wizard skill](../src/odoo_boost/skills/domain_wizards/SKILL.md). Avoids a generic direct-state write being mistaken for a finished workflow. | Official security/ORM contract; automation pass. |
| B18 | Both: Cybrosys chatter prose and v19 Chapter20 model sample | Distinguish tracking, internal notes, subscriptions and actual notification delivery; tracking can be suppressed and is not immutable audit | [Mail/chatter skill](../src/odoo_boost/skills/domain_mail_chatter/SKILL.md). Sets realistic audit/delivery expectations. | Official mixins/security docs establish the guarantees; the example only supplied model/dependency patterns. |
| B19 | Code: v19 Chapter06/05_data_migrations | Verify migration version/phase selection, row identifiers/counts, invalid conversions and separate install/upgrade paths | [Upgrade reference](../src/odoo_boost/skills/upgrade_analysis/references/data-upgrades.md), linked from [upgrade skill](../src/odoo_boost/skills/upgrade_analysis/SKILL.md). Adds an original procedure for preserving existing data. | Official upgrade scripts/custom database upgrade docs and loaders; [upgrade pass](book-reference-review-upgrades.md). |

## Concrete value from reviewing faulty examples

The code contributed counterexamples as well as positive patterns:

- The v19 ordinary/tagged Python test defines `partner_liam` and
  `partner_amelia` but asserts on `partner_nikul`. The current review directly
  reconfirmed this in Chapter16 test files. It supports independent fixture
  construction and actual execution before trusting an example.
- The v19 data-migration report records a loop retrieving each row ID while its
  UPDATE targets a fixed `id=1`. The retained upgrade procedure explicitly calls
  for parameterized row identifiers, affected-row counts and multi-row checks.
- The sampled public/none controller routes use sudo searches and interpolate
  names into HTML. The extracted skill retains route mechanics with stronger
  authorization, bounding and escaping requirements.

None of these findings claims the complete companion repositories were executed.
No book addon was installed or copied into the package as part of these passes.
The compute/performance references contain independently written guidance and
illustrative patterns; they are not certified production cookbook implementations.
The pre-existing pattern library as a whole must not be attributed to these books.

## Official-source follow-up: useful additions with separate provenance

The [five-version audit](version-audit.md) expanded questions raised by the books
into 52 documented claim rows for 15, 17, 18, 19 and 20. Its contributions belong
to **official documentation/source**, even when a book prompted the investigation:

- Version boundaries for HTTP dispatch/authentication, Owl/module conventions,
  view syntax, hook signatures, cache invalidation and scheduler progress APIs.
- Stock execution quantity/unit names, UoM/reference-chain and valuation changes,
  fiscal-position configuration, and qualified payment states.
- Compatibility metadata and isolated generated version guidance in
  [versions.py](../src/odoo_boost/versions.py) and
  [version notes](../src/odoo_boost/guidelines/core/versions/v20.md).
- A concrete [access-introspection tool correction](../src/odoo_boost/mcp_server/tools/list_access_rights.py)
  to select the connected server's legacy ACL/rule or audited unified-access
  schema. This is a later implementation fix found through official-source
  verification, not code imported from a book.
- Pinned documentation revisions and a 73-file official-source manifest with
  SHA-256 evidence; distinct documentation/source commits preserve reproducibility.

The audit reports 767 passing package tests after the access fix, plus Ruff,
formatting and mypy checks. Earlier extraction passes reported 50 composition/
installation tests and temporary delivery of 90 skill files and 14 guideline
files. These establish package behavior/delivery, not live Odoo accounting,
stock, scheduler, browser or migration correctness. No rebuilt-wheel or live
five-version Odoo certification is established by those reports.

## Official verification for this reconciliation

The current check reread the pinned local 18 ORM compute/search/inverse section,
18 multi-company guidance, and 19 upgrade-script contract and matched their
principal rules to current package files. Evidence lives under the revisions in
[the audit](version-audit.md), with original paths recorded in the extraction
reports. Representative public references are:

- [ORM compute/search/inverse, 18](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/developer/reference/backend/orm.rst).
- [Multi-company, 18](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/developer/howtos/company.rst).
- [Upgrade scripts, 19](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/upgrades/upgrade_scripts.rst).

Live requests to the generated odoo.com pages timed out during this reconciliation;
the local pinned official files supplied the actual verification. This report
does not present an unsuccessful request as a fresh online check. Full technical
claim-by-claim verification remains in the linked audit matrices.

## What remains

Coverage still requires chapter/page and distinct-recipe tracking. Website
builders, payment providers, reporting, translations, POS, IoT, advanced stock
reservation/valuation, reconciliation internals and edition/localization behavior
need focused review. Inventoried content is still pending unless a specific
reviewed unit and disposition is recorded. Existing tests, links and a broad
subject summary cannot establish that every useful lesson was extracted.
