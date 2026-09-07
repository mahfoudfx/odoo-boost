## Testing

### Python Tests
- Test classes inherit from `odoo.tests.common.TransactionCase` (rolls back after each test) or `HttpCase` (for UI/tour tests).
- Place tests in `tests/` directory with `__init__.py` importing all test modules.
- Test files must start with `test_` prefix.
- Use `tagged()` decorator to categorize tests: `@tagged('post_install', '-at_install')`.

### Common Test Patterns
```python
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

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

### Best Practices
- Use `setUpClass` for shared test data — faster than `setUp`.
- Use `cls.env` in `setUpClass`, `self.env` in test methods.
- Always test with a non-admin user for ACL validation: `self.env['my.model'].with_user(user).create(...)`.
- Test edge cases: empty recordsets, missing required fields, access denial.
- Use `with self.assertRaises(...)` for exception testing.
- Use `Form` helper for testing form view onchanges: `from odoo.tests.common import Form`.
