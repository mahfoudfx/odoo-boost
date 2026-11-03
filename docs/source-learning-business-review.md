# Source learning: reservation, valuation, reconciliation and localization

Reviewed 2026-11-03. This pass reads six complete saved Cybrosys book-text pages
and selected coherent sections of two larger Enterprise pages. All source-stimulated
lessons have **book prose** origin; no companion business addon was executed or
newly reviewed as code in this pass. Official documentation supplies accepted
workflow contracts. This is technical workflow extraction, not a certification of
a country's accounting requirements or every installed localization.

## Sources actually read

Paths below are relative to workspace `references/odoo-books/cybrosys/`.

| Reading depth | Input |
|---|---|
| Complete text page | `community/inventory__configuration.txt` |
| Complete text page | `accounting/basics-of-accounting__reconciliation.txt` |
| Complete text page | `accounting/configuration__reconciliation-models.txt` |
| Complete text page | `accounting/odoo-erp__odoo-localization.txt` |
| Complete text page | `accounting/basics-of-accounting__anglo-saxon-accounting.txt` |
| Complete text page | `enterprise/accounting__anglosaxon-accounting.txt` |
| Selected sections only | `enterprise/inventory__configuration.txt`: lines 155–245 (operation types), 850–1105 (removal, costing and packaging) |
| Selected section only | `enterprise/inventory__operations.txt`: lines 750–930, especially 3.11 Landed Costs; the following replenishment section is only partial |

Screenshots remain remote references in this archive; reading text does not imply
visual verification of its UI. Search hits elsewhere are not marked read. Cookbook
coverage and other functional pages remain separate pending units.

## Retained lessons and project value

| Lesson ID | Origin / source stimulus | Experience extracted and official check | Project benefit / disposition |
|---|---|---|---|
| SB-01 | Book prose: Community configuration; Enterprise operation types | Diagnose reservation using operation policy. Odoo 18 documents at-confirmation, manual and scheduled reservation; available stock is not the same as allocation to an order. Scheduled reservation has normal/starred windows. The official detailed pages also demonstrate manual override. | Integrated in a linked stock decision reference. Provides a decision tree before changing assignment logic, plus competing-order/time-boundary test scenarios. |
| SB-02 | Book prose: Enterprise configuration, Reserve Packagings | Packaging policy can deliberately reserve less than available. The book's example of 24 demanded units in 12-unit packagings and 22 available agrees with official 18 docs: full-only reserves 12, partial policy reserves 22. Backorder and actual movement remain separate. | Integrated as a concrete acceptance scenario; prevents automatically treating reservation shortfalls as broken stock calculations. No scenario was executed. |
| SB-03 | Book prose: Community/Enterprise removal and costing sections | Physical stock removal and cost valuation are separate policies even if both say FIFO. The official 18 removal docs establish category-over-location priority, location-name ordering for closest location, and demand-oriented package selection. The book's closest-distance and smallest-package wording is too broad. | Integrated with a comparison checklist. Helps developers avoid implementing a distance optimizer or smallest-package rule from a UI label. |
| SB-04 | Book prose: Enterprise 3.11 Landed Costs | Retain cost-allocation workflow and split-method choices, but separate inventory value from selling price. The book repeatedly says landed costs revise selling price; official 18 docs define product valuation adjustments. The book requires automated valuation; the pinned official 18 page explicitly permits manual or automatic with AVCO/FIFO. That eligibility discrepancy needs matching module/source and runtime validation before becoming an executable rule. | Integrated as qualified decision guidance and an explicit unresolved eligibility question. Helps avoid incorrect automatic sales-price changes and unsupported configuration restrictions. |
| SB-05 | Book prose: accounting reconciliation introduction; official payment/reconciliation details refine it | Payment matching and bank reconciliation address different facts. Odoo 18 docs describe payment-linked invoice residuals, outstanding-account configuration, and bank suspense replacement during reconciliation. Registering payment does not itself establish bank settlement; exact journal/payment states are configuration dependent. | Existing accounting guidance confirmed, with more precise traceable review scenarios. Note-only; no unnecessary replacement of the existing skill. |
| SB-06 | Book prose: accounting reconciliation models | Treat model sequence and matching conditions as business policy. Official 18 docs state first matching model in sequence applies; auto-validation requires conditions, while underpayment tolerance does not apply to overpayments. Test competing rules, wrong partner/reference and amounts above/below tolerance. | New note retained for accounting automation review. Adds realistic failure cases beyond balanced debits/credits; no private reconciliation API is promoted. |
| SB-07 | Book prose: localization overview | A company country is the start of module selection, not proof of configured localization correctness. Official 18 documentation describes company-specific packages, parent-localization inheritance by branches, restrictions on package changes after posting, and additional chart/tax/report configuration. | Note retained: record company, installed `l10n_*` modules and configuration before drawing conclusions. Enables reproducible localization-specific fixtures without universal country claims. |
| SB-08 | Book prose: both Anglo-Saxon pages; official-only version qualification | The book says Anglo-Saxon accounting is Enterprise-only and provides fixed journal narratives. This pass does not have enough matching module/edition implementation evidence to accept that exclusivity claim. Official 18 docs support mode-dependent accounting; official 19 docs change accounting valuation timing to invoicing/closing while physical valuation remains movement based. | Existing version gate confirmed. Keep edition exclusivity unresolved and account mappings/timing conditional; do not copy the book tables as universal posting instructions. |

No generic API signatures for reservation, landed costs or reconciliation were
invented. The retained value is the decision process, distinctions between business
facts, test inputs and known limits of the book examples.

## Official evidence inspected

Odoo 18 documentation revision:
`ca129a822019682bd32552e4cbabba2520d1308e`. Relevant sections were read locally;
generated odoo.com requests for reconciliation models and valuation configuration
timed out. The unsuccessful requests are not presented as live verification.

- [Reservation methods](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/shipping_receiving/reservation_methods.rst), plus its three linked method pages: timing and available/reserved distinctions.
- [Packaging](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/product_management/configure/packaging.rst), Partial reservation: the numeric packaging example.
- [Removal strategies](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/shipping_receiving/removal_strategies.rst), strategy table and configuration priority.
- [Automatic valuation configuration](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/inventory_valuation_config.rst), setup and accounting-mode sections.
- [Landed costs](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/landed_costs.rst), purpose, split methods and important eligibility note.
- [Payments](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/finance/accounting/payments.rst), linked/standalone and payment configuration sections.
- [Bank reconciliation](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/finance/accounting/bank/reconciliation.rst), resulting entry, suspense account and manual write-off sections.
- [Reconciliation models](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/finance/accounting/bank/reconciliation_models.rst), sequence, types, auto-validation and underpayment-only tolerance.
- [Fiscal localizations](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/finance/fiscal_localizations.rst), Configuration. The developer accounting-localization tutorial was also consulted for module structure; its installation prose is not used to certify every edition/runtime.
- [Inventory valuation, 19](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/applications/finance/accounting/get_started/inventory_valuation.rst), introduction, accounting standards and valuation methods: explicit newer-version boundary.

The AVCO return page was sampled, but its full scenario and exact valuation APIs
were not reviewed to completion; it supplies no new accepted rule in this pass.

## Implemented result and validation

Added an independently authored
[reservation and valuation reference](../src/odoo_boost/skills/domain_stock/references/reservation-and-valuation.md)
and a conditional link in the existing stock skill. It covers timing, packaging,
physical removal versus costing, landed-cost pricing distinction and scenario
evidence. It has no local-book dependency. Accounting/localization findings remain
traceable research notes because the existing skill already captures core workflow
boundaries and this pass does not justify private-API or universal legal rules.

Validation: `tests/test_skills.py` passed (35 tests); both local links in the
new report/reference and skill pointer resolve; `git diff --check` passed.
No live Odoo stock allocation, costing, reconciliation, edition matrix or
localization workflow was run. These gaps gain focused reading and useful retained
guidance; they remain open for source/runtime depth and remaining pages.
