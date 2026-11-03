# Odoo 15 Essentials examples: backend extraction

Reviewed 2026-11-03 from the newly supplied archive. Origin of every lesson below
is **code example**, not a new reading of the book prose. Paths are relative to
`references/odoo-books/Odoo 15 Development Essentials/Odoo-15-Development-Essentials-Examples/`
in the workspace. This is a bounded representative-file review, not execution of
the addons or contextual completion of every repeated chapter snapshot.

## Retained experience

| Lesson | Exact source stimulus | Official verification | Project usefulness / disposition |
|---|---|---|---|
| E15-B01: preserve multi-record CRUD contracts | `ch08/library_checkout/models/library_checkout.py`, `ch10/library_checkout/models/library_checkout.py`, `final/library_checkout/models/library_checkout.py`: create validates after super; write reads `self.stage_id.state` once for all records and recursively writes timestamps behind a context flag | Pinned Odoo 15 `BaseModel.write` updates every record; `api.model` on create adapts a list by repeated single creates, whereas `model_create_multi` preserves a batch | Existing ORM guidance confirmed. New concrete failure scenario: transition multiple checkouts starting in different stages, retain per-record previous state, and verify the intended timestamps. A context recursion flag is not an authorization boundary. Note-only; no package edit required. |
| E15-B02: count grouped data, then map results back | `ch10/library_checkout/models/library_checkout.py` and final version retain both a disabled per-record `search_count` and a `read_group` implementation, mapping each member to its count and defaulting absent groups to zero | Official 15 performance batch example and pinned `read_group` implementation support this pattern and the default `member_id_count` group-count key | Existing performance guidance confirmed with a useful before/after teaching example. Preserve visibility/domain semantics and test zero matches, multiple members and results alongside query counts. The author's 'single query' comment is intent, not measured evidence. |
| E15-B03: computes assign every record; UI warnings have a separate contract | Checkout `_compute_request_date_onchange` reads and assigns scalar `self.request_date`, only conditionally assigns it, and returns an onchange-style warning although wired as a stored compute | Official ORM Computed Fields requires assigning the field and demonstrates iteration; the separate onchange API describes warning return values | Existing compute/testing rules confirmed. Add this to the research counterexamples: test recomputation for multiple checkouts and formulate whether date means creation, member change or user input before choosing dependencies. No automatic rewrite is justified without that business choice. |
| E15-B04: assert the result of a behavior, not the existence of its callable | `final/library_app/tests/test_book.py` uses `self.assertTrue(self.book1._check_isbn)` without calling the method; setup uses a fixed example ISBN | Direct Python syntax establishes the defect; official 15 test runner/isolation contract was checked in `odoo/tests/common.py` and testing docs. An Odoo-specific assertion cannot compensate for an uncalled method | Useful new test-review counterexample. Include valid/invalid inputs, explicitly invoke the checker and verify the public invariant. The existing tests do not establish ISBN correctness; they were not executed here. |
| E15-B05: UI selection context is optional and caller-controlled | Both `ch08/library_checkout/wizard/checkout_mass_message.py` and final version index `env.context['active_ids']`, unconditionally return checkout defaults and then post messages | Official `default_get` returns requested defaults; official security docs state public method arguments/records cannot be trusted | Existing wizard trust-boundary guidance confirmed. Test absent/empty/wrong-model/denied selections and respect requested default fields. No claim that this wizard bypasses target ACLs: its `message_post` calls do not themselves use sudo. |
| E15-B06: review each exposed child model, not only its parent document | `final/library_portal/security/ir.model.access.csv` grants portal read on checkout lines; `library_security.xml` restricts members and checkouts but defines no checkout-line ownership rule | Official 15 ACLs plus default-allow record rules: a relation to a restricted parent does not establish a child-model rule | Useful new explicit security scenario: two portal users query checkout lines directly, not only through a parent page. Under the inspected addon policy and absent other installed rules, the child ACL can permit reading other users' line records. Static policy finding; no live exploit or installed-stack result is claimed. |
| E15-B07: distinguish extension from delegation | `final/library_member/models/library_book.py` extends a checker with a fallback to super; `library_member.py` uses `_inherits` via required partner relation plus mail mixins | Official ORM Inheritance and extension distinguishes model extension from delegated fields; delegation does not mean all behavior is inherited | Existing model-design guidance confirmed. Verify lifecycle/access of both member and partner and tests for the extended method's fallback. No claim that the ISBN algorithm supports every ISBN representation. |
| E15-B08: inspect source history before treating final as canonical | ch10's app model has compute/constraints; `final/library_app/models/library_book.py` is a shorter model without those additions. `ch11` and final app manifests retain version `14.0.1.0.0`; final wizard contains a debugging breakpoint | Exact file comparison, not an Odoo API claim; official manifest contract provides context but does not prove addon target compatibility | Valuable source-selection lesson: retain chapter locators and hash snapshots. 'Final' is not proof that it accumulates all chapters or is deployable. Source remains unchanged as evidence. |

## Concrete defects and limitations

- `final/library_checkout/wizard/checkout_mass_message.py` contains
  `pdb.set_trace()` at the beginning of `button_send`; the earlier ch08 version
  lacks it. It can interrupt unattended test/server execution. This is static
  evidence; the process was not started.
- The uncalled ISBN assertion is a false-positive test regardless of whether
  the underlying implementation or sample input is correct.
- Batch compute and mixed-stage write hazards above follow from scalar field
  access and the framework contract. A single-record happy-path test will not
  establish batch correctness.
- Portal child-model visibility is conditional on the inspected ACL/rule set;
  additional modules may add restrictions. Record-rule findings must be validated
  under actual non-admin users and installed modules.
- Wizard tests use `SingleTransactionCase`, distinct from the method-savepoint
  behavior of `TransactionCase`. Their passing results would not establish the
  same isolation contract. No test suite was run in Odoo.
- The inheritance example's ISBN-10 branch strips non-digits, so representations
  using a non-digit check character need explicit policy/tests before claiming full
  ISBN support. This review does not certify the ISBN standard or implementation.

## Official evidence inspected

The official documentation commit is
`f6b84ed59624ba8f0db2b1d0f7097e435550bb7e`; the separately pinned Odoo source
commit is `3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187`. The local files at these
revisions supplied the verification; no successful fresh web request is claimed.

- [ORM: compute, onchange, recordsets and inheritance](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/orm.rst).
- [Security: default-allow rules and public method trust](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/security.rst).
- [Performance: batch operations](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/performance.rst).
- [Testing reference](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/testing.rst).
- [BaseModel write/default_get/read_group](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/odoo/models.py).
- [Single versus multi-create adapters](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/odoo/api.py).
- [TransactionCase and SingleTransactionCase](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/odoo/tests/common.py).

The retained pattern fits the current ORM, testing, security and wizard guidance.
The useful additions here are traceable scenarios and counterexamples; this batch
did not need a new skill, runtime tool, or edit to the existing package rules.

## Fully read source files

One representative for each selected distinct backend/security/manifest content
was read, with explicit additional chapter context. Other hash-identical paths
are not automatically marked contextually duplicate-reviewed. The machine-readable
list for the integrating reviewer is `/tmp/essentials-backend-reviewed.json`.

```text
ch03/library_app/security/library_security.xml
ch04/library_app/__manifest__.py
ch05/library_app/models/__init__.py
ch05/library_app/security/ir.model.access.csv
ch07/ch07_recorsets_code.py
ch08/library_checkout/__manifest__.py
ch08/library_checkout/models/__init__.py
ch08/library_checkout/models/library_checkout.py
ch08/library_checkout/models/library_checkout_line.py
ch08/library_checkout/wizard/checkout_mass_message.py
ch10/library_app/__manifest__.py
ch10/library_app/models/__init__.py
ch10/library_app/models/library_book.py
ch10/library_checkout/__manifest__.py
ch10/library_checkout/models/library_checkout.py
ch11/library_app/__manifest__.py
ch11/library_app/models/res_partner.py
final/library_app/__manifest__.py
final/library_app/models/__init__.py
final/library_app/models/library_book.py
final/library_app/models/library_book_category.py
final/library_app/security/ir.model.access.csv
final/library_app/security/library_security.xml
final/library_app/tests/__init__.py
final/library_app/tests/test_book.py
final/library_checkout/__manifest__.py
final/library_checkout/models/__init__.py
final/library_checkout/models/library_checkout.py
final/library_checkout/models/library_checkout_line.py
final/library_checkout/models/library_checkout_stage.py
final/library_checkout/security/ir.model.access.csv
final/library_checkout/tests/__init__.py
final/library_checkout/tests/test_checkout_mass_message.py
final/library_checkout/wizard/__init__.py
final/library_checkout/wizard/checkout_mass_message.py
final/library_member/__manifest__.py
final/library_member/models/__init__.py
final/library_member/models/library_book.py
final/library_member/models/library_member.py
final/library_member/security/ir.model.access.csv
final/library_member/security/library_security.xml
final/library_portal/__manifest__.py
final/library_portal/security/ir.model.access.csv
final/library_portal/security/library_security.xml
```
