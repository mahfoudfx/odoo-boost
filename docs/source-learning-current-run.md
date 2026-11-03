# Systematic scan: retained results and remaining work

Batch `LEARN-2026-11-03-04`, 2026-11-03. Scope expansion stopped after the user's
token-usage concern. This is a substantial partial review, not full-library extraction.

## Done

- Complete automated inventory: 6,157 example files, 87 EPUB documents, 4,242
  heading sections, 696 EPUB assets, 772 saved text pages and 47 acquisition entries.
  These are separate denominators, not independent recipes or completed readings.
- Coverage: 758 units directly read, 28 partially read and 11,215 pending.
  Duplicate content evidence is retained without pretending its context is complete.
- Retained 79 new lesson groups: 53 code example, 14 both prose/code, 9 book prose
  and 3 official-only. Together with the earlier 14 code-intake lessons, the
  machine-readable ledger has 93 lessons. Historical B01–B19 remain separately indexed.
- V15 Essentials: representatives of all 96 distinct file contents reviewed;
  repeated chapter context and original-addon runtime validation remain open.
- Acquisition: 23 original failures now have fetched usable text, 19 map to saved
  content through corrected publisher links, five remain unresolved.
- Added two original packaged references: stock reservation/valuation decisions
  and translation extraction/loading, conditionally linked from existing skills.
- Added reusable inventory, recovery, review-recording and isolated runtime tools.
- Two independent Odoo 18 report/security contract tests passed. Their private
  PostgreSQL cluster stopped successfully. No original book addon/migration ran.
- Validation: full package suite 783 passed before final inventory refinements;
  all 15 maintainer-tool tests passed after those refinements. Earlier focused
  guidance/skill/tool checks: 66 passed; Ruff and formatting passed at that point.
  Broad static scan: 2,510 Python and 1,735 XML parse passes; four empty XML
  placeholders; 335 manifests; no missing local declared files; six asset-set warnings.

## Findings and project value

| Review | Retained value |
|---|---|
| [Website/reports/translations](source-learning-web-review.md) | Builder version conflicts, active asset/import paths, publication scope and translation/report language contracts |
| [Business](source-learning-business-review.md) | Reservation timing, packaging versus availability, physical removal versus costing, reconciliation sequence/tolerance and localization qualifications |
| [Integrations](source-learning-integrations-review.md) | POS import/data loading, offline RPC boundaries, payment callback/amount validation and layered IoT diagnosis |
| [Quality](source-learning-quality-review.md) | Migration selection and conversion defects, meaningful tests, query-count claims and test-framework transitions |
| [ORM/security](source-learning-orm-review.md) | Batch-create contracts, transition policy, return-preserving extension, name-search compatibility and effective-access tests |
| [Fields/environment](source-learning-models-review.md) | Compute/inverse units, dependencies, delegation, context/company boundaries, SQL semantics and dangerous teaching hooks |
| [UI](source-learning-ui-review.md) | Action scope versus security, ordered views, XPath/search semantics and field-widget contracts |
| [Controllers/mail](source-learning-controllers-mail-review.md) | Route/signature mismatches, address parsing, activity lifecycle and digest semantics |
| [Remaining Essentials contents](source-learning-essentials-completion.md) | Filter labels versus domains, legacy kanban field wrappers and seed-data dependencies |
| [Runtime](source-learning-runtime-review.md) | Actual Odoo 18 evidence for custom report contexts/escaping and independent child-model ownership rules |

Retained claims were checked against matching pinned official docs and selected
official implementations. Unresolved conflicts remain qualified, including v19
builder API compatibility and some edition/configuration claims. Most findings
confirm existing guidance or add research scenarios rather than justify code edits.

## Missing

- Most prose sections and EPUB assets, remaining distinct cookbook contents and
  contextual verification of repeated recipe snapshots still need review.
- Deeper reviewed topics remain partial: browser/website builder, payments, POS,
  IoT, reporting/translation, reservation/valuation, reconciliation/localization.
- Original addons/migrations need matching v15/v17/v19 runtime tests; current
  Odoo 18 tests do not certify those sources. PDF, browser, payment-provider,
  localization and physical-device scenarios were not executed.
- Five unresolved original URL entries: cohort-style, Employees root, Maintenance
  overview-menu, sitemap, Discuss meetings configuration-menu. Their exact URLs
  and attempts remain in `source-learning/failed-urls.json`.
- V17 Essentials ZIP still contains only README/LICENSE; no examples were supplied.

Continue with one explicitly bounded topic and a small evidence set. Read summary
records first, reuse recorded hash lineage, and avoid spawning agents with the
full conversation. No new review should start merely because a slot is available.
