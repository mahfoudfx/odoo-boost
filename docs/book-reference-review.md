# Book reference review

Reviewed on 2026-11-03. This report records a first extraction pass, not a claim
that every book page or example has been deeply read or executed.

## Coverage and provenance

The temporary `references/odoo-books/` collection is outside the distributable
project. Findings below are independently written; no book prose or example
implementation needs to ship with Odoo Boost.

| Source | Inventory coverage | Detailed review in this pass |
| --- | --- | --- |
| Packt, Odoo 15 Development Essentials, fifth edition | All 26 HTML/XHTML EPUB documents parsed; 15 numbered chapters identified | Computed-field search/inverse and transaction-control sections |
| Packt, Odoo 17 Development Cookbook, fifth edition | All 32 HTML/XHTML documents parsed; 25 chapters identified; 3,233 example files, including 1,039 Python and 718 XML | Record-rule and Python-test sections; computed room-availability model and manifest |
| Packt, Odoo 19 Development Cookbook, sixth edition | All 29 HTML/XHTML documents parsed; 21 chapters identified; 2,503 example files, including 1,250 Python and 894 XML | Prefetch, record-rule and Python-test sections; computed room-availability model; ordinary and tagged Python tests |
| Cybrosys Odoo 18 books | Manifest inventories 761 saved pages: development 151, Community 195, Enterprise 363, accounting 52; 47 failed URLs | Computed-field material sampled; functional material remains available for later domain-specific work |

Inventory means headings and file metadata were inspected across the corpus.
It does not mean all body text was read. Example files include repeated chapter
snapshots; file counts are not counts of independent recipes. None of the addon
examples was installed in an Odoo server during this review.

Across the EPUBs, the chapter inventory covers setup, addon structure, models,
ORM, module data, debugging, views, security, internationalization, automation,
controllers, web client/OWL, testing, RPC, performance, email and deployment.
The cookbooks also cover POS and IoT. Chapter numbers differ between editions;
future work should match topic names rather than assume stable numbering.

## Extracted lessons and project applications

### 1. Compute storage is a design choice

Before: `guidelines/core/orm_best_practices.md` recommends `compute` plus
`store=True` for searchable derived fields without describing the alternative.

Target: explain that nonstored computed fields can define a `search` method;
choose storage based on filtering/grouping needs and recomputation cost. An
inverse updates the source values. Dependency paths must represent the actual
inputs. This is supported by the [Odoo 18 ORM reference](https://www.odoo.com/documentation/18.0/de/developer/reference/backend/orm.html).

The v15 example explains both search and inverse; the v17/v19 room examples
show recordset iteration and dependency-driven stored availability. The lesson
is the decision process, not a reusable copy of the sample addon.

### 2. Preserve prefetch before adding explicit reads

Before: the ORM guideline says to prefetch with `read()` rather than accessing
fields one by one, which can imply ordinary recordset iteration is inefficient.

Target: browse a collection together and iterate its recordset so Odoo can
prefetch. Profile query counts before changing retrieval. Batch per-record
queries and creates where semantics permit; avoid suggesting every loop is a
performance defect. These decisions follow the [Odoo 18 performance reference](https://www.odoo.com/documentation/18.0/developer/reference/backend/performance.html)
and [ORM cache description](https://www.odoo.com/documentation/18.0/sv/developer/reference/backend/orm.html).

The v19 prefetch section supports this correction. A possible later diagnostic
for search/count inside loops must remain advisory because aggregation changes
can alter filtering, access or result semantics.

### 3. Record-rule flags are applicability, not denials

Before: security guidance explains global/group composition, but leaves the
default and operation-flag semantics implicit.

Target: ACL grants are additive; after ACL access is granted, record rules are
default-allow when no applicable rule exists. A false rule permission flag means
the rule does not constrain that operation. Global rules intersect; group rules
union within the global bounds. Test users with overlapping groups and multiple
companies. See [Odoo 18 security reference](https://www.odoo.com/documentation/18.0/developer/reference/backend/security.html).

The cookbook security recipes are useful starting scenarios, but examples with a
single group do not establish correctness for overlapping production groups.

### 4. Keep framework transactions atomic

The v15 transaction section describes cursor commit/rollback operations; that
capability should not become blanket advice for business methods. Target guidance
must distinguish interactive shell persistence and explicitly owned cursors from
ordinary framework-managed calls. Odoo owns commit/rollback for normal calls;
manual commits can leave partially completed workflows. See [Odoo 18 coding
guidelines](https://www.odoo.com/documentation/18.0/contributing/development/coding_guidelines.html#never-commit-the-transaction).

### 5. Test discovery and isolation need precise descriptions

Before: the testing guide describes `TransactionCase` as rolling back after each
test, without explaining shared setup and method savepoints.

Target: describe the shared transaction and method savepoints precisely; import
test modules through `tests/__init__.py`; use shared class setup when appropriate;
keep UI onchange tests distinct from direct ORM business-invariant tests. See
[Odoo 18 testing reference](https://www.odoo.com/documentation/18.0/de/developer/reference/backend/testing.html).

The v19 ordinary and tagged test examples reference `self.partner_nikul` although
their setup defines `partner_liam` and `partner_amelia`. This is a concrete reason
to independently construct and run fixtures rather than treat book code as a
validated test corpus.

### 6. Version differences require explicit gates

The sampled room models use `_sql_constraints` in v17 and `models.Constraint`
in v19. The latter is documented in the [Odoo 19 ORM reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html).
The v19 constraint also iterates records where the sampled v17 constraint assumes
a singleton. Preserve the recordset lesson across versions while selecting the
constraint declaration from the configured Odoo series.

## Priorities and remaining work

1. Correct the existing ORM, security and testing guidance before adding tools.
2. Retain the verified rules inside the packaged guidance and existing domain
   skills, so removing reference books cannot remove runtime knowledge.
3. Add original regression fixtures only for implemented scanner behavior. Treat
   unresolved method inheritance, dynamic declarations and dependencies as limits
   on static conclusions.
4. Continue focused extraction of controllers, raw SQL/cache coherence, OWL,
   migration recipes, module data and domain workflows. These have been inventoried
   but not exhaustively reviewed in this pass.

This report is an audit baseline and source trail. It does not assert that its
target changes have been implemented; the implementation diff and validation
results are the authoritative before/after evidence.


## Implemented before/after

| Area | Before | After |
| --- | --- | --- |
| ORM core | Storage presented as the way to search computes; prefetch advice prescribed explicit reads; onchange suggested for validation | Custom searches and storage trade-offs; recordset prefetch; server-side invariants |
| Compute skill | Unsupported `order` callback; incomplete freshness guidance | Search/sort distinction, context dependencies, refresh policy and verification |
| Compute patterns | 524 lines including misleading clock, inverse, and search examples | Concise original patterns with dependency, inverse, access and equivalence checks |
| Performance reference | 550 lines including manual commits, offset batching of changing domains, unconditional index advice | Measured batching, transaction ownership, safe retries, SQL cache/dependency protocol |
| Security | Rule permission semantics implicit; conflicting wizard checklist | Explicit ACL addition and rule applicability; effective-user/group/company checks |
| Testing | Imprecise TransactionCase isolation; generic edge cases | Method-savepoint clarification and compute, batching and query-regression scenarios |

These are guidance changes, not new MCP tools or static diagnostics. Existing
skill routing and guideline composition deliver the changes. Book text, EPUBs,
and example archives are outside the package source tree; no runtime lookup was
added. Rewritten references are independently authored, with primary source links.

Validation: guideline composition and skill installation tests passed (50 tests),
and `git diff --check` passed. A wheel build could not run because the environment
lacks both `build` and `hatchling`; archive contents have not been independently
verified. No Odoo runtime examples were executed. Keep the books until the
remaining extraction topics above have been reviewed if full coverage is wanted.


## Subsequent extraction

See [pass 2](book-reference-review-pass-2.md) for controllers, frontend assets,
views, and module lifecycle. Extracted rules are checked against official
documentation and, where needed, Odoo source for the relevant series.

## Local official-documentation extraction pass

Further verified work is recorded in:
- [Accounting, stock and multi-company](book-reference-review-pass-3.md)
- [Crons, wizards and chatter](book-reference-review-automation.md)
- [Existing-data upgrades](book-reference-review-upgrades.md)

The local official snapshots cover 15, 17, 18, 19 and 20. Each report distinguishes
which series established a rule from details that still require source/runtime
verification. The packaged skills retain source links and independently written
rules, not local corpus dependencies. Complete deep reading of every book chapter
and every example remains outstanding; these reports do not certify whole-library
extraction. Advanced reservation/valuation internals, payment-provider integration,
website builders, reporting, translations and edition/localization differences
remain candidates for subsequent focused review.


## Systematic version follow-up

The [five-version audit](version-audit.md) supersedes earlier version assumptions
where conflicts were found, including the earlier master-only access model claim.
See its matrices, pinned evidence, validation results and runtime-tool limitation.
