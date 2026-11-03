# Development Essentials example archive intake and scan

Reviewed 2026-11-03, batch `LEARN-2026-11-03-03`. Inputs are the two user-provided
ZIP archives, not new book prose. Retained technical lessons below have **code
example** origin, with official documentation used to establish the contract.

## Extraction and availability

Paths below are relative to the workspace's `references/odoo-books/`.

| Source ID | Archive | Extracted directory | Files / distinct contents | Outcome |
|---|---|---|---|---|
| B15-CODE | `Odoo-15-Development-Essentials-Examples.zip` | `Odoo 15 Development Essentials/Odoo-15-Development-Essentials-Examples/` | 419 / 96 | Substantial collection; repeated chapter snapshots |
| E17-CODE | `Odoo-17-Development-Essentials-Examples.zip` | `Odoo-17-Development-Essentials/Odoo-17-Development-Essentials-Examples/` | 2 / 2 | README and LICENSE only; no actual examples |

The v17 Essentials collection is distinct from the existing v17 Cookbook. No v17
Essentials EPUB is established by this intake. Its README contains only the title
and publisher; it gives no explanation or alternate location for missing examples.

Archive SHA-256:

```text
B15-CODE 34cceb82db42f8401b2b5957d4ed88177982374e2b50b6fa5987c44ed5b681ad
E17-CODE 68018ff658ebff5c51681f00bd85a560bc5c04bc769f35462eac8c33b67286c7
```

ZIP CRCs/content were read during extraction; paths and symlinks were checked.
Original ZIPs remain intact. The single archive wrapper directory was removed
when choosing the destination. Existing differing files were not overwritten.
Both root LICENSE files say MIT, while addon manifests commonly declare AGPL-3;
preserve these declarations and establish the applicable file license before reuse.
No example code is copied into the distributed project in this batch.

## Broad static scan

Every v15 file is inventoried in [coverage.jsonl](source-learning/coverage.jsonl),
with hashes, reading status and execution status separate. All 221 Python files
parse using the current Python parser; all 127 XML files parse. All 25 addon
manifests are literal dictionaries, and their declared local data/demo/assets
paths exist. These are static checks, not Odoo installation, XML-schema, asset
compilation or runtime validation. `assets` values being sets still need review
despite parsing successfully.

Other v15 files: 41 CSV, 10 PNG, 6 CSS, 4 JS, 5 shell, 1 nginx configuration,
1 service configuration, 1 README and 2 extensionless metadata files. All four
JS files are empty. The archive has no `ch14` directory or PO/POT translation
catalogs. Gaps in frontend/i18n coverage therefore cannot be closed by file count.

Exact hashes mark duplicate candidates only; repeated snapshots remain pending
contextual review. Direct reading is recorded only for files actually read in this
batch. The backend report lists its own inspected paths and qualifiers.

## Retained lessons: reports, portal, RPC and operations

Each locator below is relative to the extracted v15 directory. Official evidence
is pinned to documentation commit `f6b84ed59624ba8f0db2b1d0f7097e435550bb7e`
for Odoo 15; it does not assert the same contract for every newer version.

| Lesson ID | Inspected example | Experience extracted | Project benefit and disposition |
|---|---|---|---|
| EX15-01 | `ch12/library_app/reports/library_publisher_report.py` and matching XML | Custom report providers may supply a different data contract: here publisher/book groups, rather than default `docs`. Align provider keys and template loops, and supply document defaults explicitly only if the custom template needs them. The provider searches books once, but repeated Python filtering by publisher still has a cost worth measuring. | Note retained: complements `report_development` by explaining custom contexts; confirms its existing explicit `doc_ids`/`doc_model`/`docs` example without requiring edits. |
| EX15-02 | `ch12/library_app/reports/library_book_report.xml` | A `t-lang` call controls template language; translated record fields also need the relevant language context. The native-language wrapper does not explicitly re-browse the records, so do not assume translated fields follow it. Test template text and translated data separately. | Note retained: provides a concrete review scenario for report-language correctness; reporting/translation gaps gain partial coverage, not closure. |
| EX15-03 | `ch13/library_portal/controllers/portal.py`, ACL/rules and portal templates | Keep list, count and pagination under the same authorized scope and URL. The route uses `/my/book-checkouts`, but pager generation uses `/my/book_checkouts`. This is a concrete URL mismatch. No explicit order is passed: verify the model order and add a stable tie-breaker when required. | Note retained: useful portal acceptance criteria; confirms existing authorization guidance and adds an exact paging defect to review scenarios. |
| EX15-04 | `ch13/library_portal/controllers/main.py` and `__manifest__.py`; `ch11/library_checkout/__manifest__.py` and `views/assets.xml` | Public catalogue `sudo().search([])` bypasses normal visibility and is unbounded. Explicitly design the public publication policy. Portal CSS is declared in the backend bundle despite styling a frontend template. Asset declarations use sets rather than the documented ordered lists; preserve ordering explicitly. The legacy asset XML is commented out of the active manifest, so its mere presence is not a loaded-XML defect. | Note retained: existing controller/asset guidance is confirmed by new counterexamples. Empty JavaScript files provide no new Owl/POS implementation. |
| EX15-05 | All four `ch09/client_app/*.py` files | Isolate RPC transport behind a domain API, request explicit fields and bound list calls. Validate the CLI argument shape: `library.py` passes a list slice as the title while adapters build an `ilike` operand from it. The unused `library_odoorpc.py::_execute` unpacks `None` as keyword arguments when omitted; this is a Python call-shape defect. Demo admin credentials and HTTP localhost settings are setup placeholders, not deployment configuration. | Note retained: useful client-contract and input-shape review scenarios; no need to replace the project's existing RPC adapter. Third-party OdooRPC behavior is not certified by official Odoo docs. |
| EX15-06 | All six `ch15/*` files and `ch02/ch02_install.sh` | Read scripts as versioned operational recipes, not executable installation instructions. `ch15_deploy.sh` clones Odoo 14 and a v12 Essentials repository although this archive is for v15. The staging scripts use matching older paths; the deploy script has an Odoo option line separated from its command. Database and filestore copies must represent the same application state; restore isolation/configuration requires its own validation. | Note retained: exposes version drift and motivates a reproducible restore test. None of these scripts was executed; no production/staging database was touched. |

Official checks supporting the retained rules:

- [Report contexts, translated templates and record language](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/reports.rst): custom-report warning, translatable templates and report assets.
- [Asset bundles and ordered manifest declarations](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/frontend/assets.rst): manifest values are file lists; frontend and backend bundles serve different contexts.
- [Security](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/security.rst): additive model access, default-allow record rules and access bypass risks. `auth=user` alone is not an ownership policy.
- [External API](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/external_api.rst): authentication, `execute_kw`, domains, requested fields and pagination. Python call/CLI defects above are directly inspected code findings.
- [Deployment](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/administration/on_premise/deploy.rst): database filtering, proxy configuration, database/filestore backups. Safe restore behavior needs actual environment-specific tests.

The local pinned official files supplied these checks. Report rendering, portal
URLs and asset bundles were not exercised in an Odoo server/browser. Suspected
effects remain source-review findings until runtime tests establish outcomes.

## Backend and remaining work

See [backend review](essentials-examples-backend-review.md) for further ORM,
security, testing and wizard findings, precise code locators and official evidence.
Machine-readable lesson dispositions are in [lessons.jsonl](source-learning/lessons.jsonl).

This batch closes extraction/intake of both ZIPs and inventories their files. It
does not close systematic reading, contextual duplicate review, book-wide topic
coverage or runtime validation. The v17 archive needs actual example content if
that source is to contribute code; the existing v17 Cookbook remains separately
available. Next reading should reconcile the remaining v15 chapter snapshots and
test the report/portal contracts on a disposable v15 instance when available.
