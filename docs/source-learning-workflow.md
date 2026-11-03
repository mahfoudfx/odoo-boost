# Internal source learning workflow

This is a maintainer process for continuously learning from books, addon code,
official references and future sources. It runs during source-review tasks; it is
not a scheduled background job or a runtime feature of the distributed package.

Start with the [contribution report](source-contribution-report.md),
[scan plan](source-scan-plan.md) and [ledger](source-learning-ledger.md).
Existing reports remain historical evidence; the ledger records subsequent work
and links to them without claiming to reconstruct missing reading history.

## Review one bounded batch

1. **Register.** Assign a stable source ID in the ledger. Record author/title,
   edition, Odoo series, location or URL, revision or content hash, acquisition
   failures and reuse/license constraints. A new revision is new review input.
   Finish when the input can be located and distinguished from other revisions.
2. **Inventory.** Enumerate every chapter/section, saved web page and example
   recipe/file, including configuration, tests, XML, JavaScript, styles, templates,
   translations and assets. Record EPUB member paths rather than page numbers
   alone. Link a recipe to its prose where possible. Keep failed URLs and missing
   files as explicit gaps. Finish when every available unit has an identifier.
3. **Select and read.** Choose a chapter or a related recipe family, small enough
   to finish in this session. Read the explanation and the relevant implementation,
   manifest, imports, permissions, data and tests. Compare adjacent snapshots and
   editions to find the actual change and its assumptions. Record exact unit IDs
   and reading depth; an inventory or keyword hit is not a completed review.
4. **Extract experience.** For each useful lesson, describe the problem, the
   decision, why it works, when to choose it, its costs, failure modes and how to
   verify it. Look for design seams, extension points, invariants, debugging
   strategies, performance evidence and operational failure recovery as well as
   API syntax. Extract good practice and defects in examples alike.
5. **Check officially.** Check every retained Odoo behavior/API claim against
   documentation for the target series. Record exact section/path, documentation
   revision and a supporting official link. Where prose is incomplete, generated
   or contradictory, inspect the matching official implementation and record its
   separate commit and symbol. Retain the discrepancy. Runtime-dependent claims
   require a relevant experiment before being labelled runtime-verified.
6. **Choose a disposition.** Use the smallest useful outcome: existing knowledge
   confirmed, new research note, guideline, skill/reference, original example,
   meaningful regression fixture, version fact, justified implementation fix,
   rejected claim, or deferred question. A confirmed rule with no package change
   is a successful extraction. Add a rule only if it improves a real decision;
   add a tool only for a demonstrated capability gap.
7. **Validate and record.** Check changed documentation links; run tests appropriate
   to changed behavior or delivery. Record actual commands/results and limits.
   Update unit coverage, lesson dispositions and the batch log even if no code
   changed. Finish with the extraction summary below and the next bounded batch.

## Evidence and coverage rules

- Classify origins as **book prose**, **code example**, **both**, or **official-only**.
  Code embedded in a book counts as code evidence only when actually inspected;
  retain a locator distinguishing it from a companion repository file.
- Distinguish the source that prompted a lesson from the official evidence that
  established correctness. A book-triggered audit can produce an official-only
  correction. Historical attribution that cannot be recovered stays uncertain.
- Check each claimed series independently. Shared wording may cover versions
  only where semantics agree. The existing pinned audit covers 15/17/18/19/20;
  14/16 and future series need their own verification when a claim includes them.
- Track **inventory**, **reading**, **official verification**, **integration** and
  **execution** separately. A test of skill installation verifies delivery, not
  the behavior of an Odoo addon. Record unavailable runtime validation explicitly.
- Hash identical files to reduce repeated reading, but preserve every path and
  recipe context. Inspect manifests, dependencies and neighboring changes before
  accepting a duplicate mapping; byte identity alone does not prove equivalent use.
- Preserve source material privately as evidence. Author original explanations
  and minimal examples; record license and attribution before reusing code.
  Installed skills must work without the local source corpus.
- Revisit retained lessons when official APIs change, a source revision changes,
  a relevant bug appears, or an actual task exposes a gap. Review the affected
  units and claims rather than restarting the entire library.

## Required records

Keep human-readable summaries in the ledger. During systematic scanning, add
`docs/source-learning/coverage.jsonl` with one record per inventoried unit and
`docs/source-learning/lessons.jsonl` with one record per extracted lesson. Create
these when executing scan stage 1. The inventory now covers all available sources;
historical reading is credited only where exact evidence exists. Preserve existing
rows and reading history when adding further sources.

The systematic run now inventories all four example roots, three EPUBs (documents,
heading sections and assets), saved Cybrosys text and acquisition entries. Existing
historical extraction remains separate where its exact reading scope is unknown.
The [current execution report](source-learning-current-run.md) summarizes progress.

## Maintainer commands

Run from the repository root. These tools maintain research evidence; they are
outside the installed runtime package.

```bash
# Refresh files/hashes and syntax checks; preserve unchanged human review history.
python tools/inventory_learning_sources.py --batch-id <batch-id>

# Retry unresolved URLs; acquired content remains pending technical review.
python tools/recover_book_pages.py

# Retain human review evidence in docs/source-learning/reviews/ before merging it.
python tools/record_source_review.py --batch-id <batch-id> \
  --evidence docs/source-learning/reviews/<review>.json

# Refresh summary totals after recording a review.
python tools/inventory_learning_sources.py --batch-id <batch-id>

# Optional independent contract tests on a supplied matching local Odoo checkout.
python tools/validate_source_contracts.py --odoo-root /path/to/odoo
```

The runtime harness creates and stops its own temporary PostgreSQL cluster. Its
current fixtures target Odoo 18 report/security contracts, not arbitrary book
addons. Socket/network sandbox restrictions can require tool approval; report
actual results separately from original-addon execution.

Review evidence JSON contains `fully_read_files`, `partial_files` (including exact
EPUB member/section or text ranges), and `lessons`. Optional `content_review_map`
records path, representative and `content_sha256`; equivalent content alone does
not complete another path's context. Keep original input locators and official
evidence for each lesson. The merger checks source hashes and rejects conflicting
lesson IDs: use a linked correction ID rather than rewriting history.

Recovered pages keep original URLs/errors, retry results and content checksums.
Alias resolution means a corrected publisher link maps to already saved content;
it is distinct from fetching new content or reading it. Use `--gap-id` to retry
specific entries and `--cached` to repair extraction from retained raw HTML.

A coverage record contains:

```json
{"unit_id":"B19:example:Chapter06/05_data_migrations/my_hostel/migrations/19.0.1/post-migrate.py","source_id":"B19","revision":"<source hash>","locator":"<relative path or EPUB member#section>","content_sha256":"<hash>","kind":"code example","inventory":"present","reading":"pending","official_verification":"pending","execution":"not-run","lesson_ids":[],"duplicate_of":null,"batch_id":null}
```

A lesson record contains:

```json
{"lesson_id":"L-0001","unit_ids":["<unit id>"],"origin":"both","problem":"<problem>","decision":"<lesson and tradeoff>","official_evidence":[{"series":"19.0","url":"<official URL>","revision":"<commit>","locator":"<section or symbol>","result":"verified"}],"disposition":"note-only","project_targets":[],"benefit":"<practical value>","validation":"<performed checks and limits>","batch_id":"<batch id>"}
```

Use `pending`, `partial`, `read`, or `duplicate-reviewed` for reading; use
`pending`, `verified`, `qualified`, `conflict`, or `unresolved` for official
verification. Integration and execution are lesson-specific when a unit contains
several claims. A unit with no useful lesson still gets a reading outcome and
reason. Failed retrievals get `inventory: missing` with the URL/error recorded.
Stable IDs survive reordering; a content change reopens affected review status.

## End every extraction batch with

- **Extracted:** lessons and their origin: prose, code, both or official-only.
- **Helpful because:** the concrete development decision or project gap addressed.
- **Retained in:** file/symbol links, or the reason no change was needed.
- **Verified against:** official versions/revisions and actual checks performed.
- **Remaining:** unresolved claims, runtime limits, coverage and next units.

Update the ledger before sending this summary. Report exact counts only from
unit records. Completion means every unit is read or contextually duplicate-reviewed
and every candidate lesson has a disposition; missing inputs remain declared
exceptions. It does not certify that every possible future insight was discovered.
