# Open source-learning gaps

Updated 2026-11-03. The [systematic execution report](source-learning-current-run.md)
records deeper reviews, two independent runtime tests and acquisition recovery.
The original broad coverage gaps remain open. The new
[Essentials scan](essentials-examples-review.md) adds partial reporting, report-language,
portal and backend coverage; it establishes no runtime results. The contribution report establishes
useful selected extraction; neither it nor the workflow closes these gaps. Use
the [scan plan](source-scan-plan.md) for execution and the
[ledger](source-learning-ledger.md) for batch outcomes.

## Topic closure criteria

For every row, read the relevant book sections and companion recipes, register
exact units and dispositions, and verify retained claims against official docs
and matching source for each claimed version. The table specifies the additional
evidence needed beyond that common review. Useful findings may require only a
research note or confirmation of existing guidance.

| Gap ID | Open topic | Scan workstream | Additional evidence needed |
|---|---|---|---|
| G01 | Website builder | 5 | Separate versioned builder/Interaction APIs from Owl; inspect snippet options, assets, editor versus published behavior and inherited templates. Browser verification remains a separate runtime result. |
| G02 | Payment integration | 4 | Trace provider/transaction state, callback authentication, duplicate and out-of-order notifications, refund and reconciliation boundaries; separate sandbox results from live payment evidence. |
| G03 | Reporting | 5 | Trace report actions, QWeb context, access checks, multi-company/language output and rendering dependencies; exercise representative HTML/PDF output when available. |
| G04 | Translation | 6 | Review extraction/import/update, Python/XML/JS interpolation and language context; verify visible output in at least two languages for runtime claims. |
| G05 | POS | 9 | Inspect loading, frontend/backend extension points, order/payment synchronization and recovery; test claimed offline behavior in a matching browser/server setup. |
| G06 | IoT | 9 | Review device registration, driver/protocol boundaries, connection/authentication and failure recovery; keep simulated tests separate from results on physical hardware. |
| G07 | Stock reservation | 7 | Trace assignment/unreservation and competing demand, tracked goods, partial availability/backorders; retain exact versioned APIs and database scenarios. |
| G08 | Valuation | 7 | Separate costing method, automated/manual valuation, returns and version-specific accounting effects; verify scenarios with expected quantities/values and currency rounding. |
| G09 | Reconciliation | 7 | Trace partial/full matching, refunds, currency differences and write-offs; document invariants and validate representative accounting scenarios. |
| G10 | Localization and edition differences | 7–8 | Identify the exact module, country/chart, edition and release. Qualify technical behavior by installed configuration; avoid universal rules from one localization. |

Official reference starting points exist in the pinned 18 documentation under
`content/`: `developer/reference/backend/reports.rst`,
`developer/howtos/translations.rst`, `developer/howtos/accounting_localization.rst`,
`developer/reference/standard_modules/payment/`,
`applications/sales/point_of_sale/` and `applications/general/iot/`.
Their presence was checked in this batch; it is not technical verification of the
unreviewed topics. Consult the corresponding version and official implementation
when executing each topic. Documentation revisions are in the existing audit.

## G11 — Every distinct code example

Status: systematic review in progress. The full inventory now includes 6,157
example files across four extracted roots, plus every EPUB document, heading and
asset. New chapter-family reviews and content lineage are recorded in the current
execution report and shared coverage. The earlier reconnaissance found 1,955 selected
text/code paths with 467 distinct contents in v17 and 2,357 paths with 618 distinct
contents in v19. These are file hashes within each collection, not independent
recipes or completed reviews. Assets and other extensions still need full inventory.

The v15 Essentials archive has a complete file inventory of 419 units; 106 paths
have been directly read, covering representatives of all 96 distinct contents.
The other paths retain pending contextual review. The v17 Essentials ZIP contains only metadata, so actual
examples remain an acquisition gap. Neither is the existing v17 Cookbook.

Closure requires every recipe and file to have a review outcome, including tests,
permissions, manifests, XML, frontend code and supporting configuration. Hash-identical
files can share reading evidence only after their recipe context is checked.
Compare changed versions and chapter snapshots. Record no-addition outcomes and
defective examples alongside useful patterns. A percentage of reviewed examples
is unavailable until that denominator exists.

## G12 — Runtime validation

Status: no original book addon or migration execution established. Deeper local
discovery found an Odoo 18 Community checkout and PostgreSQL server tools, despite
the earlier PATH/import probe. Two independently authored report/security tests
have now passed against that checkout in a disposable database, with the private
cluster stopped. See [runtime evidence](source-learning/runtime-validation.json).
Matching v15/v17/v19 original-addon execution, PDF/browser tests, provider sandboxes,
localization matrices and IoT hardware remain unverified.

Prepare isolated matching-version addon paths and disposable databases, then record
installation/update commands, module versions/dependencies, fixture inputs, expected
and actual outcomes, logs and cleanup. Repeated chapter snapshots must run in
separate addon paths so same-name modules do not mask one another. For migrations,
test fresh install separately from an upgrade of existing data, including multiple
rows and invalid/empty conversion inputs. Record original-example failures separately
from outcomes after corrections. Browser, provider-sandbox, Enterprise/localization
and hardware prerequisites are scenario-specific exceptions, not blanket passes.

Closure is per claimed scenario/version; reading code, mocked RPC tests and package
installation tests cannot substitute for running the addon or migration. Full
runtime coverage can remain open while independently verified documentation
extraction continues.

## G13 — Cybrosys acquisition failures

Status: all 47 original entries have been retried. **23 now have fetched usable
text, 19 resolve through corrected publisher navigation to already saved text,
and five remain unresolved.** [failed-urls.json](source-learning/failed-urls.json)
retains original errors and subsequent evidence. The original failures split into:

| Original error category | Entries | Recovery approach |
|---|---|---|
| HTTP 404 | 24 | Follow the publisher's current book navigation, check malformed/obsolete paths and confirm a replacement's title, content and Odoo version. |
| Missing book content container | 18 | Refetch and inspect the actual document structure; distinguish a changed selector from a placeholder or unavailable chapter. |
| Missing chapter content | 5 | Refetch and inspect chapter structure/content before classifying as unavailable. |

Original entries by collection: development 15, Enterprise 31, accounting 1, Community 0. Failures
are URL entries, not necessarily 47 distinct missing chapters: slash variants,
malformed paths and extraction errors require reconciliation. Keep the original
URL/error and append retry date/result, confirmed replacement, saved path and hash.
Mark recovered only after usable chapter content is saved. Where recovery fails,
retain the exception and optionally learn the topic from official references with
official-only provenance; that does not recover the missing book content.

## Next bounded action

Complete the full unit inventory, including these acquisition-gap IDs, before
claiming comprehensive coverage. Source reading can proceed on available topics
while URL recovery and runtime preparation remain separately tracked. The existing
scan order prioritizes ORM/security foundations before these deeper topic batches.
