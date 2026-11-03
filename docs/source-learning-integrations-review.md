# Source extraction: POS, IoT and payment integrations

Reviewed 2026-11-03. This is a focused reading of concrete recipes and selected
book sections, not complete POS/IoT/payment library coverage or runtime validation.
Origin labels distinguish the book/example stimulus from official verification.
No production skill or tool needed changing: the useful addition is this original
decision guidance and its exact counterexamples.

## Sources and reading scope

Example paths below are relative to the corresponding nested Cookbook Examples
root. `C17` and `C19` mean Odoo 17 fifth-edition and Odoo 19 sixth-edition cookbooks.
The Cybrosys page paths are relative to `references/odoo-books/cybrosys/`.

- C17 POS: `Chapter22/03_make_rpc` and `Chapter22/06_modify_recipt`, selected
  manifest/import, RPC, loader, receipt JavaScript and template files.
- C19 POS: `Chapter19/06_modify_recipt`, including root/model imports, manifest,
  product loader, receipt JavaScript and template.
- C19 payment: `Chapter22/11_payment_gateway/payment_gateway_generic/`, including
  module/model/controller imports, manifest, active provider/transaction models,
  controller, provider master data and all three view/template files. The extra
  `models/payment_gateway.py` is not imported by `models/__init__.py`.
- C19 IoT: `Chapter21/05_capture_image/my_hostel/`, selected manifest, imports,
  student model/view and security records.
- C17 EPUB `OEBPS/B20997_24.xhtml`: selected driver-loading and device-input sections.
  C19 EPUB `OEBPS/Text/Chapter_21.xhtml`: selected device-input section;
  `OEBPS/Text/Chapter_19.xhtml`: selected RPC/UI/business-logic/receipt and Razorpay
  configuration material. These EPUB members remain partially read.
- Cybrosys development: `point-of-sales__custom-pos-ui.txt`,
  `point-of-sales__customize-customer-receipts.txt`, `iot-box__load-drivers.txt`,
  `iot-box__connect-iot-box-with-odoo.txt`; Enterprise: `iot__devices.txt`,
  `point-of-sale__orders.txt`, `ecommerce__configure-ecommerce-payments.txt`.

Exact fully read paths and lesson evidence are supplied to the consolidating
reviewer in `/tmp/source-integrations-evidence.json`. No hash-identical neighboring
recipe is implicitly marked contextually complete.

## Retained experience

| ID / origin | Decision and concrete source finding | Project value / disposition |
|---|---|---|
| SI-01 — both | Treat a POS customization as a chain: declared POS asset bundle → loaded template/component → model fields → behavior → receipt data. The v17 and v19 receipt examples use different frontend model/import APIs and loaders. Verify each extension against the target release rather than porting the import name alone. | Confirms versioned asset/component guidance; adds a concrete migration review procedure. Note-only. |
| SI-02 — code example | Trace imports before evaluating an apparent backend extension. C19 receipt addon `__init__.py` is empty, so its `models/product.py` is not imported by that addon. C17 imports its loader correctly. Both pinned official v17 and v19 product loaders already include `standard_price`, so blindly appending it is unnecessary in those inspected implementations. | Distinguishes dead sample code from required framework customization. Useful acceptance test: prove a custom field is present from the actual loading path, with the intended visibility. Note-only. |
| SI-03 — both | A server RPC inside an otherwise offline-capable POS introduces an online dependency. Both sampled “last five orders” examples perform a server query; the C17 code has no explicit `order` or transport-error handling. Define what “last” means, preserve authorized scope, request bounded fields/results and give an explicit offline/error outcome. A below-cost popup only warns; it is not a server-enforced sales invariant. | Complements existing performance/security guidance with offline and temporal-query scenarios. Test dropped connectivity, equal timestamps, denied access and bypass of client-side warnings. Note-only; these scenarios were not executed. |
| SI-04 — code example | The C19 generic gateway is a simulation despite its manifest's “fully-correct skeleton” description. Public redirect/verify routes synthesize success; return/webhook accept caller status with sudo processing; webhook signature verification is TODO. Its active amount extractor returns `None` when amount/currency is absent, and official19 explicitly skips amount validation on `None`. Framework processing therefore does not authenticate a notification or guarantee that this sample checked money. | New concrete security counterexample. Keep a simulation isolated; a real adapter authenticates the provider message or verifies via trusted provider API, binds reference/provider/amount/currency, and tests tampering, replay and state ordering. Note-only, with framework behavior source-verified. No live exploit is claimed. |
| SI-05 — both | Separate online payment providers, POS payment methods and terminal/device integrations. The C19 book's Razorpay section mentions the online-provider module; official19 POS Razorpay setup additionally specifies its POS module, terminal selection, username/device serial/API key and test-mode setup. Installing an eCommerce provider alone does not establish that terminal workflow. | Adds a dependency/configuration boundary to integration review. Verify the exact module and payment flow before diagnosing credentials or adapting APIs. Note-only. |
| SI-06 — both | Diagnose IoT by layers: network/database pairing → image/core version → handler synchronization → supported device → application/widget contract → persisted business result. The camera recipe depends on `quality_iot` and a quality test type, not simply a binary field. Official18 describes pairing/token alternatives, automatic handler updates and image compatibility after upgrades. | Converts installation instructions into a useful diagnostic procedure; prevents treating a paired box as proof that camera capture works. The Enterprise widget implementation was unavailable, so its complete private field/options contract remains unresolved. Note-only. |
| SI-07 — both | A custom driver's `supported()` must identify compatible hardware; the Cybrosys sketch returns `True` unconditionally. Official18 base Driver provides a False default and expects an override. Its action idempotency cache is an in-memory LRU of 500 IDs: a useful duplicate-suppression mechanism, not proof of durable exactly-once device operation. | Retains a concrete driver-review rule and restart/retry test scenarios; no hardware protocol assumptions or generic driver copied into the project. Note-only. |
| SI-08 — both | Establish receipt arithmetic as business policy. Sample “savings” subtracts discounted line base price from current product list price × quantity; it is not automatically the same as a price-list discount or tax-inclusive paid difference. C19 clamps the total to zero; refunds, repricing, taxes and currency must be explicit scenarios. The Cybrosys “available quantity” UI passage actually renders a formatted price, so prose intent must be checked against template fields. | Adds useful acceptance criteria without asserting an unverified financial formula. Confirmed source discrepancy; monetary/tax outcomes remain scenario questions for the target installation. Note-only. |

The sampled C19 generic provider also sets test state and remains unpublished in
its data file. This reduces accidental UI exposure but does not implement callback
authentication: the public routes themselves contain no test-state gate. Its
unimported `payment_gateway.py` and unloaded `views/payment_provider.xml` must not
be confused with the active files selected by imports and manifest.

## Official verification

Pinned documentation revisions: 18 `ca129a822019682bd32552e4cbabba2520d1308e`,
19 `de94dcddba224a1ece042792fa444e7ba0c31fdf`. Relevant local files were read;
autodoc directives alone were not treated as method-body evidence.

- [18 POS overview](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/sales/point_of_sale.rst) establishes normal temporary offline operation; it does not promise offline success for a custom RPC.
- [19 Razorpay POS terminal setup](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/applications/sales/point_of_sale/payment_methods/terminals/razorpay.rst) establishes the distinct terminal configuration.
- [18 IoT connection](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/general/iot/connect.rst), [updates](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/general/iot/iot_advanced/updating_iot.rst), and [camera](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/general/iot/devices/camera.rst) support the layered diagnosis. Some production/certificate prerequisites mean a generic local test setup does not prove real device readiness.
- [18 online payments](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/applications/finance/payment_providers.rst) separates provider configuration/features and recommends a duplicate/test database for testing.
- [19 payment transaction](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/addons/payment/models/payment_transaction.py): `_process`, `_validate_amount`, `_extract_amount_data`, `_search_by_reference`, `_set_done`. Exact amount-skip behavior checked in the implementation.
- [19 Razorpay controller](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/addons/payment_razorpay/controllers/main.py) verifies signatures before `_process`; missing/invalid signatures raise Forbidden. This is an official provider-specific example, not a universal signature algorithm.
- [17 POS session loader](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/addons/point_of_sale/models/pos_session.py) and [19 product loader](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/addons/point_of_sale/models/product_product.py) establish the backend loading APIs and existing cost field.
- [18 driver base](https://github.com/odoo/odoo/blob/55f9d29cd13c935226c2b6e48eb661bc89310e8b/addons/hw_drivers/driver.py) establishes the compatibility override and bounded idempotency cache.

The additional pinned official implementation files were fetched successfully,
hashed and retained outside the package in the integration evidence archive.
One initially guessed v19 `models/product.py` URL returned 404; the actual checked
path is `models/product_product.py`. Browser retrieval of raw URLs failed before
the successful direct pinned downloads. Successful downloads are evidence, not
runtime tests of those implementations.

## Validation and remaining gaps

Reviewed import graphs, manifests and selected complete files; compared the book
intent with executable sample paths and pinned official method bodies. No addon,
payment, order, migration, browser session, terminal or hardware operation ran.
No actual provider sandbox or Enterprise `quality_iot` code was available.

POS offline persistence/synchronization, delayed/duplicate callbacks, authorization/
capture/refund and accounting reconciliation, hardware action recovery, installed
edition combinations and full version migrations remain open. This review supplies
focused evidence and practical scenarios; it does not certify the broad topic gaps.
