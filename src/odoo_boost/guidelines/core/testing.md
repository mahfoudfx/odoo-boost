## Testing

### Python Tests
- Test classes inherit from `odoo.tests.common.TransactionCase` or `HttpCase` (for UI/tour tests). In the audited 15/17/18/19/20 sources, TransactionCase shares a class transaction and isolates test methods with savepoints; its cursor closes without committing.
- Place tests in `tests/` directory with `__init__.py` importing all test modules.
- Test files must start with `test_` prefix.
- Use `tagged()` decorator to categorize tests: `@tagged('post_install', '-at_install')`.

### Common Test Patterns
```python
from odoo.tests import TransactionCase, tagged


# tests/common.py
class TestSaleCommon(TransactionCase):
    test_lang = "en_US"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, lang=cls.test_lang))
        cls.env.user.lang = cls.test_lang
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})


# tests/test_sale_order.py (import TestSaleCommon from .common)
@tagged("post_install", "-at_install")
class TestSaleOrder(TestSaleCommon):
    def test_create_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(order.state, "draft")

    def test_confirm_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        order.action_confirm()
        self.assertEqual(order.state, "sale")
```

### Test Tags
- `at_install`: run during module installation (before post_install).
- `post_install`: run after all modules are installed (most common).
- `standard`: included by default.
- Use `-at_install` + `post_install` for tests that need all modules loaded.

### Running Tests
```bash
# Run all tests for a module
odoo --test-enable -d mydb --stop-after-init -i my_module

# Run specific test class
odoo --test-tags /my_module:TestClassName -d mydb --stop-after-init

# Run tests with pytest (using pytest-odoo)
pytest addons/my_module/tests/ -s
```

### Deterministic Language and Assertions
- Set the language once in a shared base class before creating fixtures. Preserve
  the existing environment context and set `lang="en_US"`; set the test users'
  `lang` explicitly too. Translation tests override the language locally.
- Business tests must run without `--load-language` or preinstalled translations.
  Assert results, state changes, and the specific exception class. Assert message
  text only when wording or translation is the behavior under test.
- Exercise security guards with dedicated non-admin users through `with_user()`
  and explicit groups, language, and allowed companies. Cover both an authorized
  action and a denied action. Make other prerequisites valid so an unrelated ACL,
  record rule, or validation cannot satisfy the negative test. Check the resulting
  state and relevant side effects; execute the guarded call without `sudo()` or
  mocking the permission check.
- Keep translation checks in a separate test module. Prepare the required
  languages and translation fixtures in the test, using the target version's
  helpers. Activating a language alone does not load module catalogs. Use one
  `subTest(lang=lang)` per language with a fresh context and isolated mutable
  fixtures; assert an explicit expected translation so source-text fallback fails.

### Best Practices
- Use `setUpClass` for shared test data — faster than `setUp`.
- Use `cls.env` in `setUpClass`, `self.env` in test methods.
- Test edge cases: empty recordsets, missing required fields, access denial.
- For computes, test batch assignment, dependency edits, and inverse/search semantics.
- For jobs, test more than one batch and a recoverable failure between batches.
- Use query-count assertions for demonstrated N+1 regressions; retain result assertions.
- Use `with self.assertRaises(SpecificException)` for exception testing; choose
  the exception raised by the target version and keep only the failing operation
  inside the context manager.
- Use `Form` for form/onchange behavior. The public `odoo.tests` namespace exports
  it in audited 17/18/19/20 sources; Odoo 15 defines it in `odoo.tests.common`.
  Avoid assuming older helper imports remain available after reorganization.


### Official Evidence
Use the matching [testing reference](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/backend/testing.rst)
and `odoo/tests/common.py` for the isolation contract. Application tests require
Odoo's own runner or a separately configured integration; `pytest-odoo` is optional
third-party tooling, not a built-in Odoo test runner.
