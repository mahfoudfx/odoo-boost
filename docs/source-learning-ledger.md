# Source learning ledger

Updated 2026-11-03. This is the internal source register, historical extraction
index and batch log. Use the [workflow](source-learning-workflow.md) for each
batch and the [plan](source-scan-plan.md) to close library coverage. The
[contribution report](source-contribution-report.md) holds the detailed retained
lessons B01–B19 and package destinations.

## Source register

Locations are relative to the workspace's `references/odoo-books/`, outside the
distributable project. These are local source identifiers, not runtime paths.
Hashes below identify the inspected EPUB bytes. Original publishers retain rights;
no permission to redistribute book prose or example code is assumed.

| Source ID | Source / version | Local location | Inventory observed now | Coverage |
|---|---|---|---|---|
| B15 | Packt Odoo 15 Development Essentials, fifth edition | `Odoo 15 Development Essentials/` | 26 HTML/XHTML EPUB documents; examples now registered as B15-CODE | Selected prose; full unit reading pending |
| B15-CODE | Packt Odoo 15 Development Essentials companion examples | `Odoo 15 Development Essentials/Odoo-15-Development-Essentials-Examples/` | 419 files / 96 distinct contents; 106 paths read, covering all distinct contents; 313 pending context | Full file inventory/static scan; intake and subsequent lessons in current run |
| E17-CODE | Packt Odoo 17 Development Essentials archive; distinct from B17 Cookbook | `Odoo-17-Development-Essentials/Odoo-17-Development-Essentials-Examples/` | 2 files: README and LICENSE, both read | Metadata only; no examples in supplied ZIP |
| B17 | Packt Odoo 17 Development Cookbook, fifth edition | `Odoo-17-Development-Cookbook-5E/` | 32 HTML/XHTML documents; historical 3,233 total example files; current selected text/code extensions: 1,955 paths / 467 distinct contents | Selected prose and code; contextual deduplication pending |
| B19 | Packt Odoo 19 Development Cookbook, sixth edition | `Odoo-19-Development-Cookbook-6E/` | 29 HTML/XHTML documents; historical 2,503 total example files; current selected text/code extensions: 2,357 paths / 618 distinct contents | Selected prose and code; contextual deduplication pending |
| CY18-DEV | Cybrosys Odoo 18 development book | `cybrosys/development/` | 151 successful manifest entries / 148 physical text files | Selected prose only |
| CY18-COM | Cybrosys Odoo 18 Community book | `cybrosys/community/` | 195 successful entries / 195 physical text files | Selected inventory prose only |
| CY18-ENT | Cybrosys Odoo 18 Enterprise book | `cybrosys/enterprise/` | 363 successful entries / 354 physical text files | Inventory only; no separately attributable implemented contribution |
| CY18-ACC | Cybrosys Odoo 18 accounting book | `cybrosys/accounting/` | 52 successful entries / 52 physical text files | Selected accounting prose only |
| OFF-DOC | Official Odoo documentation, 15/17/18/19/20 | `references/odoo-official-docs/manifest.json` relative to workspace | Five pinned documentation snapshots | Verification corpus; not a claim of full reading |
| OFF-SRC | Official Odoo implementation, 15/17/18/19/20 | `references/odoo-official-source-audit/manifest.json` relative to workspace | Historical audit: 73 selected files with checksums | Targeted API evidence; no live-server certification |

EPUB SHA-256:

```text
B15 2b4784a112012b71743ba2883c6e3e836c5539cb838fd6d2050344b169b0c6b9
B17 a06bed6415f46b2d99f8ebb347b77852f43bc63f9cf253805458a2c30cf8fe4b
B19 d723e41f29bd24ec8a9b5d308995874189b36a6410aadc0aeef412ce5716e2d6
```

The text/code count includes `.py`, `.xml`, `.js`, `.scss`, `.css`, `.csv`, `.po`,
`.pot`, `.rst`, `.md`, `.yml`, `.yaml`, `.sh`, `.html`, `.txt`, `.json`, `.sql`
under each cookbook directory. Distinct contents means SHA-256 identity within
that directory. It is reconnaissance, not a complete asset inventory or count of
independent recipes. EPUB document counts include front matter.

Cybrosys manifest: 808 URL entries, 761 successful entries mapping to 749 distinct
existing text paths, plus 47 failed URLs. Every successful recorded path exists;
repeated path mappings account for the difference, so it is not evidence of 12
missing files. Full URL/path collision analysis and per-unit hashes remain pending.
Use the manifest as the starting URL list and preserve failed entries.

## Historical extraction index

These batches predate systematic unit tracking. Their selected locators and
validation are in the reports; they are not retroactive whole-chapter completion.

| Batch | What was extracted | Origin | Project benefit / retained outcome | Evidence and limits |
|---|---|---|---|---|
| HIST-01 | B01–B06: computes, prefetch, rules, transactions, tests, constraints | Book / both / code as classified per lesson | More accurate ORM/security/testing guidance and original compute/performance patterns | [First pass](book-reference-review.md); reported 50 delivery tests; examples unexecuted |
| HIST-02 | B07–B11: route extension/trust, component APIs, manifests/data, views | Both, code and book-led; official checks resolve APIs | Correct extension and version decisions in existing guides/skills | [Second pass](book-reference-review-pass-2.md); reported 50 delivery tests; no full frontend corpus execution |
| HIST-03 | B12–B15: accounting, inventory, company scope | Book; official source qualified later version details | Replaces incomplete business templates with workflow invariants and verification scenarios | [Business pass](book-reference-review-pass-3.md); no live business workflows |
| HIST-04 | B16–B18: scheduler, wizards, chatter | Official-led / book / both respectively | Bounded scheduler work, validated operations, realistic tracking/delivery expectations | [Automation](book-reference-review-automation.md); reported 34 skill tests; no live delivery/scheduler checks |
| HIST-05 | B19: existing-data migration procedure and faulty row-ID example | Code with official contract verification | Existing-data preservation checks, phase/version selection, invalid-value policy | [Upgrades](book-reference-review-upgrades.md); example migration unexecuted |
| HIST-06 | Five-version claim matrices, compatibility metadata and access-introspection fix | Official documentation and source, prompted by extraction questions | Version-specific guidance and corrected live-tool schema selection | [Version audit](version-audit.md); historical 767 package tests after fix; mocked RPC, not live Odoo |

## Current batch log

### LEARN-2026-11-03-01 — Contribution reconciliation and workflow

- Inputs: the five extraction reports, four version-audit reports, current package
  guidance and selected example/official files. Exact representative official
  locators are in the contribution report.
- Extracted: 19 retained contribution groups with prose/code/both attribution;
  separate official-only follow-up; clearer coverage distinctions and the
  successful-entry versus distinct-file reconciliation.
- Helpful because: maintainers can identify what the library actually improved,
  avoid treating sampled content as fully reviewed, and repeat the process for
  additional sources without requiring unnecessary edits.
- Retained in: contribution report, workflow, scan plan, this ledger and the
  repository instruction/contribution pointers. No production guidance or tool
  implementation changed in this batch.
- Official verification: representative local pinned 18 ORM/company and 19 upgrade
  contracts rechecked against current package content. Existing matrices supply
  historical checks for other claims. Online generated-page requests timed out.
- Validation: all 58 local Markdown links in the changed/added documents resolve;
  `git diff --check` passed after integration;
  no package or live Odoo tests needed for this documentation-only batch.
- Coverage: full unit inventory and systematic source scan remain pending;
  no new whole chapter or complete recipe family is claimed as deeply reviewed.
- Next: scan stage 1 unit inventory, then ORM/security/transaction workstream.

### LEARN-2026-11-03-02 — Explicit open-gap tracking

- Inputs: current scan plan, original Cybrosys acquisition manifest and local
  runtime/tool availability. No new book chapter or recipe was deeply reviewed.
- Extracted: acquisition failures classified as 24 HTTP 404 entries, 18 missing
  content-container errors and 5 missing-chapter-content errors. Origins: source
  acquisition metadata, rather than book prose or example code.
- Helpful because: recovery can distinguish obsolete URLs from parser failures,
  and deeper-topic, example-review and runtime gaps now have checkable closure
  criteria rather than an implicit promise of completion.
- Retained in: [open-gap tracker](source-learning-gaps.md), 47 individually
  identified entries in [failed-urls.json](source-learning/failed-urls.json),
  and a scan-plan pointer. No production changes were needed.
- Official checks: verified the presence of pinned 18 official reference paths
  for reports, translations, accounting localization, payments, POS and IoT.
  This was reference discovery only; no new Odoo API claim was promoted to guidance.
- Validation: all 47 exported URLs/errors match the original manifest and IDs
  are unique; local links resolve and `git diff --check` passed. No runtime tests
  ran. No Odoo executable on PATH or importable module in active Python was found;
  PostgreSQL client tools are present, but server availability is unverified.
- Remaining: every G01–G13 gap stays open. Failed URLs have not been retried,
  example unit coverage is not yet populated, and no addon/migration was executed.
- Next: full unit inventory, followed by the first source-reading batch; acquisition
  recovery and runtime preparation have independent status and can proceed alongside.

### LEARN-2026-11-03-03 — Essentials archive intake and first scan

- Inputs: two user-provided Essentials ZIPs, extracted beside the v15 book and
  under a separate v17 Essentials directory. Originals retained; differing
  existing files protected. Hashes and inventory are in
  [essentials-archives.json](source-learning/essentials-archives.json).
- Extracted: 14 code-origin lesson groups covering report contexts/language,
  portal pagination/publication/assets, RPC contracts, deployment drift, batch
  CRUD/counts/computes, assertions, wizard context, child-model access, inheritance
  and snapshot selection. See [intake review](essentials-examples-review.md) and
  [backend review](essentials-examples-backend-review.md).
- Helpful because: concrete counterexamples and review scenarios support existing
  guidance. Reporting/language gaps gain selected code evidence. Existing skills
  did not require rewriting.
- Retained in: those research notes, [coverage](source-learning/coverage.jsonl)
  and [lesson dispositions](source-learning/lessons.jsonl). No copied addon code,
  runtime corpus lookup or package behavior change was introduced.
- Official checks: pinned Odoo 15 ORM/security/performance/testing/report/assets/
  external API/deployment docs and selected ORM/API/testing implementation files.
  Reports identify revisions and separate verified contracts from untested effects.
- Validation: archive-to-extracted byte identity and path checks; all 221 Python
  and 127 XML files parse; all 25 literal addon manifests' local data/demo/asset
  references exist. Coverage/lesson references, local Markdown links and whitespace
  checked after integration. No addon, script, browser or migration was executed.
- Coverage: 421 new unit records, 83 directly read (81 v15 and 2 v17 metadata),
  338 pending contextual reading, 323 unapproved duplicate-path candidates.
  Four v15 JS files are empty; no PO/POT catalogs or ch14 directory supplied.
  The v17 ZIP contains no examples.
- Next: reconcile remaining v15 chapter snapshots and deepen report/portal
  contracts. Obtain actual v17 Essentials examples if available. Full-library
  and runtime gaps remain open.

### LEARN-2026-11-03-04 — Systematic inventory and focused extraction

- Consolidated outcome: [current run](source-learning-current-run.md).
- Extracted: 79 new lesson groups (53 code, 14 both, 9 prose, 3 official-only),
  with original source locators and official evidence in 10 persisted review JSONs.
- Helpful because: clearer version/business/extension decisions, concrete defect
  scenarios and actual report/security evidence now support existing guidance.
- Retained: nine focused source reports, runtime report, two linked packaged
  stock/translation references and four reusable maintainer tools. Existing correct
  skills required no broader rewrite; original examples remain unchanged.
- Coverage: all available files/documents/headings/assets inventoried; 758 units
  read, 28 partial, 11,215 pending. V15 Essentials has read representatives of all
  96 distinct contents; duplicate recipe contexts remain separately pending.
- Acquisition: all 47 failures retried; 23 recovered, 19 resolved aliases, five
  unresolved. Provenance and hashes retained per entry.
- Official checks: version-specific pinned docs and implementations per lesson;
  conflicts explicitly qualified. Two independent Odoo 18 contract tests passed;
  original addon/migration execution remains not-run.
- Validation: full suite 783 passed before final inventory refinements; 15 tool
  tests passed after them. Broad Python/XML/manifest scan and hash/source-link
  validation recorded in generated evidence. No existing database/service used.
- Stopped expanding scope following the user's token-usage concern. Most prose,
  remaining code/context review and version-matched original runtime tests remain.
  Future work should use small batches and minimal carried context.

### Commit-readiness verification — 2026-11-03

- Product changes are complete: two original references linked from existing
  stock/translation skills. Outstanding source reading is research backlog, not
  a partially implemented runtime feature.
- Corrected stale inventory wording in the workflow, scan plan and source register.
- Fresh full suite: 783 passed. Ruff, formatting, JSON parsing, 95 local Markdown
  links and whitespace checks passed.
- Built the 0.14.0 wheel and installed it into an isolated temporary target.
  Both new references were delivered by the installed skill loader; the wheel
  excludes research documents, maintainer tools and the source corpus.
- No matching-version original-addon runtime certification or publication is
  implied. The existing independent Odoo 18 contract results remain separate.

## Append a batch

Use a stable batch ID and record inputs/revisions, exact units, extracted lesson
IDs and origins, project benefit, disposition/targets, official evidence, actual
validation, coverage changes, unresolved questions and next units. Keep historical
entries intact; link subsequent corrections by lesson and batch ID. During the
systematic scan, the unit/lesson JSONL files defined by the workflow supply counts;
this ledger stays the readable index and summary.
