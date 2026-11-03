# Book extraction: accounting, stock, and multi-company

This focused pass compares selected book passages with local official documentation.
It is not a complete reading of the library and executes no Odoo business workflows.
The report supplies implementation evidence; package edits and checks are recorded
by the implementing reviewer.

## Evidence roots

Book paths below are relative to `references/odoo-books/`:

- `cybrosys/accounting/financial-management__customer-financial-handling-in-odoo-18.txt`
- `cybrosys/accounting/configuration__fiscal-position.txt`
- `cybrosys/community/inventory__operations.txt`
- `Odoo-17-Development-Cookbook-5E/Odoo-17-Development-Cookbook-5E.epub`, member `OEBPS/B20997_04.xhtml`
- `Odoo-19-Development-Cookbook-6E/Odoo-19-Development-Cookbook-6E.epub`, members `OEBPS/Text/Chapter_4.xhtml` and `OEBPS/Text/Chapter_8.xhtml`
- `Odoo 15 Development Essentials/Odoo 15 Development Essentials.epub`, selected execution-environment material in `OEBPS/B16119_07_Final_PD_ePub.xhtml`.

Official paths below are relative to `references/odoo-official-docs/<series>/<revision>/content/`.
Revision identifiers are preserved in `references/odoo-official-docs/manifest.json`.

## Claim and disposition matrix

| Proposed lesson | Book stimulus | Official evidence | Versions checked | Disposition |
|---|---|---|---|---|
| Correct validated invoices through credit/debit-note workflow; do not present resetting to draft as routine refund/correction | Customer financial handling: credit notes and invoice states | `applications/finance/accounting/customer_invoices/credit_notes.rst` | 18 | Add to accounting skill; separate invoice correction from low-level journal-entry API possibilities |
| Posting state and payment/reconciliation state represent different workflow facts | Customer financial handling: status and payment status | `applications/finance/accounting/customer_invoices/credit_notes.rst` (refund payment is separate) | 18 | Add verification of refund payment and stock return separately from credit note |
| Fiscal positions map taxes and accounts, may remove taxes or replace one by several, and automatic selection depends on sequence/conditions | Fiscal-position chapter | `applications/finance/accounting/taxes/fiscal_positions.rst` | 18 | Prefer standard invoice fiscal-position pipeline over copying product taxes blindly; API signatures require source lookup |
| A counted inventory quantity is staged until Apply, which generates traceable stock movement | Inventory operations | `applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.rst` | 18 | Replace blanket quant prohibition with distinction between direct on-hand mutation and supported count/apply workflow |
| Product stock tracking uses inventory UoM; unit conversion is supported between units in the same category | Inventory operations | `applications/inventory_and_mrp/inventory/product_management/configure/uom.rst` | 18 | Explain conversion and rounding; avoid treating every quantity as implicitly product UoM |
| Company-dependent fields need correct active-company evaluation; nonstored derived values need company context dependencies | Cookbook field attributes, execution environment | `developer/howtos/company.rst` | 15, 17, 18, 19, 20 | Add with_company plus depends_context('company') and two-company tests |
| Company relational consistency is distinct from record visibility | Company fields and current skill model | `developer/howtos/company.rst` | 15, 17, 18, 19, 20 | Add check_company rules: not on company_id itself; shared records cannot link arbitrarily to company-specific records |
| Shared and company-restricted models use different rule domains | Current skill always shows shared-record domain | `developer/howtos/company.rst` | 15, 17, 18, 19, 20 | Show both policy choices and test selected-company combinations |
| v19 cookbook's ir.property storage explanation must not be generalized | v17 and v19 Chapter 4 both describe old ir.property storage | Local ORM page uses autodoc for field internals, not a complete generated field reference | Not resolved by local text alone | Exclude storage-backend claim until official source is inspected; retain stable public company_dependent API |

## Concrete package gaps

`domain_accounting` currently copies `product.taxes_id` into invoice lines and
suggests a partner fiscal-position mapping call as if that represented the complete
invoice mapping policy. Explain that tax/account selection belongs to the standard
company, fiscal-position, localization and invoice workflow. Do not prescribe an
unverified private method signature. Preserve currency-rounding invariants rather
than encourage binary floating-point equality checks.

`domain_stock` currently declares `quantity` as the general move-line field despite
supporting older versions, and its transfer example immediately sets all planned
quantities as done. This can erase the distinction among demand, reservation and
actual execution. Replace universal executable snippets with version-aware workflow
steps unless verified against the target source. Include tracked lots/serials,
partial transfer/backorder, and adjustment traceability in verification. The local
application docs establish workflow behavior, not exact Python field compatibility.

`domain_multi_company` currently searches all visible records after `with_company`.
Changing the active company is not an explicit per-record domain filter. Add a
company domain when processing one company's documents and distinguish that from
record-rule authorization. Verify access with an ordinary user, with A only, B
only and A+B selected, and test company-dependent values in both active companies.

## Official source links

- [Multi-company developer guidance, 18](https://github.com/odoo/documentation/blob/18.0/content/developer/howtos/company.rst); matching local files were checked in 15, 17, 19 and 20.
- [Credit notes, 18](https://github.com/odoo/documentation/blob/18.0/content/applications/finance/accounting/customer_invoices/credit_notes.rst)
- [Fiscal positions, 18](https://github.com/odoo/documentation/blob/18.0/content/applications/finance/accounting/taxes/fiscal_positions.rst)
- [Inventory adjustments, 18](https://github.com/odoo/documentation/blob/18.0/content/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.rst)
- [Units of measure, 18](https://github.com/odoo/documentation/blob/18.0/content/applications/inventory_and_mrp/inventory/product_management/configure/uom.rst)

These lessons are a technical workflow extraction, not jurisdiction-specific
accounting advice. No book prose or example code is copied into this report.
Remaining topics include payment reconciliation internals, valuation changes
across releases, advanced stock reservation, and edition/localization differences.

## Implemented result

Updated the three existing domain skills. Accounting now qualifies balance checks
by currency precision and separates invoice correction, payment and stock return.
Stock uses a version-aware workflow in place of the automatic full-completion
snippet and describes supported count/apply adjustments. Multi-company distinguishes
restricted/shared rule policy, context switching, explicit scope and consistency.
The unresolved storage-backend claim remains excluded.

See also [automation](book-reference-review-automation.md) and
[data upgrades](book-reference-review-upgrades.md). The controller skill was
reconciled with the earlier verified core guidance: bounded input/data, accurate
CSRF defaults, no placeholder webhook authentication presented as implementation.

Validation after integration: 50 guideline/skill tests passed and `git diff --check`
passed. A temporary installation delivered 90 skill files and 14 guideline files,
including the new linked upgrade reference. Installed text contained no local book
or official-snapshot directory dependencies. This is installation-path verification,
not a rebuilt wheel or live accounting/stock/scheduler execution.
