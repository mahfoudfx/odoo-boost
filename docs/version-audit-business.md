# Version audit: accounting, stock and multi-company

Audit date: 2026-11-03. Scope: the extracted claims in the three packaged
`domain_accounting`, `domain_stock`, and `domain_multi_company` skills for 15, 17,
18, 19 and 20. This audit compares official documentation and selected official
model implementations; it does not execute Odoo or certify every installed addon,
localization, or private API. Books supplied questions, not authority.

## Evidence identity

Local documentation root is `references/odoo-official-docs/<series>/<revision>/`:

| Series | Documentation revision |
|---|---|
| 15.0 | `f6b84ed59624ba8f0db2b1d0f7097e435550bb7e` |
| 17.0 | `fbf3e3a6ef0bda7c30b28f213848deca17c2a872` |
| 18.0 | `ca129a822019682bd32552e4cbabba2520d1308e` |
| 19.0 | `de94dcddba224a1ece042792fa444e7ba0c31fdf` |
| 20.0 | `3efea922210a1451b0e48c58a33706b04c4786c1` |

Supplementary implementation checks used official `odoo/odoo` branch source on
the audit date. Those web reads are branch-specific, not a pinned source checkout
or proof that the deployed revision matches. The documentation revisions above
must not be mistaken for source-code revisions. Recheck moving branch code when
porting to a specific deployment.

## Claim-by-version matrix

V = verified in the pinned documentation; S = verified in official branch source;
Q = qualified guidance, not a universal API or runtime guarantee; U = unresolved,
kept outside the skill's technical contract. Evidence keys follow the table.

| Claim | 15 | 17 | 18 | 19 | 20 | Evidence / disposition |
|---|---|---|---|---|---|---|
| Validated-invoice corrections use credit/debit-note workflow | V | V | V | V | V | A1; retain workflow; avoid jurisdiction-specific blanket legal advice |
| Credit note does not itself refund cash or return stock | V | V | V | V | V | A1 explicitly separates those operations |
| Posting, payment and reconciliation are distinct | V | V | V | V | V | A2; configured payment paths differ |
| Payment registration always needs bank reconciliation to become paid | Q | Q | Q | Q | Q | A2 contains configuration exceptions; do not prescribe one universal state path |
| Fiscal-position tax mapping configuration | V: mapping rows | V: mapping rows | V: mapping rows | V: taxes | V: taxes | A3; add version boundary |
| Balance comparison respects company-currency precision | S | S | S | S | S | A4; internal method signatures differ |
| Generic journal/invoice creation snippets are production-complete | Q | Q | Q | Q | Q | Structural examples only; company, account, access and localization validation required |
| Mandatory explicit currency_field argument in every Monetary declaration | Q | Q | Q | Q | Q | Endpoint source checks A5 disprove a universal requirement; explicit association is advice |
| Count is staged until applied | V | V | V | V | V | I1; retain distinction from arbitrary on-hand mutation |
| Applied count creates stock movement | S | V | V | V | V | I1 plus 15 quant source; labels differ |
| Move-line execution quantity fields | S: qty_done, reserved product_uom_qty | S: quantity/picked | S: quantity/picked | S: quantity/picked | S: quantity/picked | I2; add explicit porting boundary |
| Move-line unit relation | S: product_uom_id | S: product_uom_id | S: product_uom_id | S: product_uom_id | S: uom_id | I2; do not inherit 19 name into 20 |
| UoM categories and per-unit rounding apply unchanged | S: categories | S: categories | S: categories | S: reference chain | S: reference chain | I3; 19/20 documentation contains stale category language |
| UoM rounding precision | S: per UoM | S: per UoM | S: per UoM | S: Product Unit; compatibility rounding field | S: Product Unit; no rounding field | I3; use target helpers |
| Stock movement automatically posts the same valuation entries in every version | Q | Q | Q | Q | Q | I4; 15/17/18 automated-movement configuration versus 19/20 invoicing/closing model |
| Correct active company and company context dependency | V | V | V | V | V | C1; retain with_company and depends_context(company) |
| Relational consistency and visibility are separate | V | V | V | V | V | C1; check_company belongs on appropriate relations, not company_id |
| Shared/restricted company domains differ | V | V | V | V | V | C1; retain both policy cases |
| Older ir.rule XML declaration is portable unchanged | V | V | V | V | S: ir.access | C1/C2; scope XML to 15/17/18/19; add 20 declaration |
| company_dependent always means ir.property rows | U | U | U | U | U | Public behavior is supported; complete storage migration audit not performed |

U does not mean the feature is absent. It means this audit does not authorize a
storage-internals or private-API rule from incomplete documentation. Verification
scenarios in the skills are proposed checks, not claims that those checks ran.

## Documentation evidence paths

All paths below begin at the pinned snapshot's `content/` directory.

- A1: all five series,
  `applications/finance/accounting/customer_invoices/credit_notes.rst`, correction
  introduction and refund/return note.
- A2: all five series, `applications/finance/accounting/payments.rst`, registration,
  outstanding-account, partial payment and reconciliation sections. Read each
  version's configuration exceptions; names alone do not establish identical behavior.
- A3: all five series,
  `applications/finance/accounting/taxes/fiscal_positions.rst`. The 15/17/18
  tax-and-account mapping section differs from 19/20 tax mapping on taxes.
- I1: 15,
  `applications/inventory_and_mrp/inventory/management/inventory_adjustments/count_products.rst`;
  17/18/19/20,
  `applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.rst`.
- I3 documentation: 15,
  `applications/inventory_and_mrp/inventory/management/products/uom.rst`;
  17/18/19/20,
  `applications/inventory_and_mrp/inventory/product_management/configure/uom.rst`.
  The 19/20 page mentions reference units but also retains category text: inspect
  I3 source for schema and conversion decisions.
- I4: 15,
  `applications/inventory_and_mrp/inventory/management/reporting/inventory_valuation_config.rst`;
  17/18,
  `applications/inventory_and_mrp/inventory/product_management/inventory_valuation/inventory_valuation_config.rst`;
  19/20,
  `applications/finance/accounting/get_started/inventory_valuation.rst`.
- C1: all five series, `developer/howtos/company.rst`, context, strict relational
  checks and shared/restricted access sections. The 20 declaration example differs.

## Official implementation evidence

Each link's branch can be replaced with the relevant audited series where stated.

- A4: `addons/account/models/account_move.py` in 15/17/18/19/20.
  The 15 `_check_balanced` and later `_get_unbalanced_moves` implementations use
  company-currency precision rather than raw float equality.
  [15 implementation](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/addons/account/models/account_move.py),
  [19 implementation](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/addons/account/models/account_move.py),
  [20 implementation](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/addons/account/models/account_move.py).
- A5: Monetary's currency-field fallback checked at the endpoints:
  [15 fields](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/odoo/fields.py),
  [20 numeric fields](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/odoo/orm/fields_numeric.py).
  This is enough to reject the old universal requirement, not a complete five-version
  audit of Monetary internals.
- I1 supplement: [15 stock quant implementation](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/addons/stock/models/stock_quant.py),
  inventory inputs and application path.
- I2: `addons/stock/models/stock_move_line.py` inspected in all five branches:
  [15](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/addons/stock/models/stock_move_line.py),
  [17](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/addons/stock/models/stock_move_line.py),
  [18](https://github.com/odoo/odoo/blob/55f9d29cd13c935226c2b6e48eb661bc89310e8b/addons/stock/models/stock_move_line.py),
  [19](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/addons/stock/models/stock_move_line.py),
  [20](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/addons/stock/models/stock_move_line.py).
- I3: `addons/uom/models/uom_uom.py` inspected in all five branches:
  [15](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/addons/uom/models/uom_uom.py),
  [17](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/addons/uom/models/uom_uom.py),
  [18](https://github.com/odoo/odoo/blob/55f9d29cd13c935226c2b6e48eb661bc89310e8b/addons/uom/models/uom_uom.py),
  [19](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/addons/uom/models/uom_uom.py),
  [20](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/addons/uom/models/uom_uom.py).
  The later conversion docstring itself retains category wording while its body
  uses factors and its schema uses reference relations. Follow implementation
  and allowed-unit policy rather than inferring validation from stale prose.
- C2: [20 unified access source](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/odoo/addons/base/models/ir_access.py)
  establishes `ir.access`, operation/domain fields and group-dependent permission
  versus global restriction behavior. The older XML example is no longer universal.

## Package changes and remaining validation

The three owned domain skills now contain explicit boundaries and current source
links. Removed the explicit unmapped product-tax assignment from the invoice
example; qualified generic creation examples, Monetary advice and payment states.
Added stock field/unit/valuation differences and version-scoped company access
examples. No local reference path is needed at installation or runtime.

Validation: skill loading/installation tests passed (34 tests); diff check passed.
No live accounting, reservation, reconciliation or company-permission test ran.
Exact localization behavior, complete storage migrations, every valuation method,
and all private method signatures remain outside the verified contract. The
version table makes those limits visible rather than claiming blanket compatibility.


## Reproducible source follow-up

Selected implementation files were subsequently downloaded at fixed commits; see
[central audit](version-audit.md) for the source revision table and local manifest.
Links above now use those commits. Only files listed in that manifest were
archived; a branch observation is not proof that unarchived files were compared.
