---
name: testing
description: Write Python and JavaScript tests for Odoo modules.
globs: ["tests/**/*.py", "static/tests/**/*.js"]
---

# Writing Odoo Tests

## Steps

### 1. Create Test Directory
```
tests/
├── __init__.py
├── test_my_model.py
└── test_my_controller.py
```

### 2. Register Tests (`tests/__init__.py`)
```python
from . import test_my_model
from . import test_my_controller
```

### 3. Unit Tests (`tests/test_my_model.py`)
```python
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestMyModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.record = cls.env["my.model"].create(
            {
                "name": "Test Record",
                "partner_id": cls.partner.id,
            }
        )

    def test_default_state(self):
        """New records should be in draft state."""
        self.assertEqual(self.record.state, "draft")

    def test_action_confirm(self):
        """Confirming a record changes state to confirmed."""
        self.record.action_confirm()
        self.assertEqual(self.record.state, "confirmed")

    def test_compute_total(self):
        """Total should be sum of line amounts."""
        self.env["my.model.line"].create(
            [
                {"model_id": self.record.id, "name": "Line 1", "amount": 100},
                {"model_id": self.record.id, "name": "Line 2", "amount": 200},
            ]
        )
        self.assertEqual(self.record.total, 300)

    def test_name_constraint(self):
        """Names shorter than 3 characters should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.env["my.model"].create({"name": "AB"})

    def test_access_rights(self):
        """Regular users should not be able to unlink."""
        user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "testuser",
                "groups_id": [(4, self.env.ref("my_module.group_my_model_user").id)],
            }
        )
        record = self.record.with_user(user)
        with self.assertRaises(Exception):
            record.unlink()
```

### 4. Form Tests (Testing Onchanges)
```python
from odoo.tests.common import Form


def test_form_onchange(self):
    """Test form view onchange behavior."""
    form = Form(self.env["my.model"])
    form.name = "New Record"
    form.partner_id = self.partner
    record = form.save()
    self.assertEqual(record.partner_id, self.partner)
```

### 5. HTTP/Controller Tests
```python
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestMyController(HttpCase):
    def test_my_page_access(self):
        """Authenticated users can access the page."""
        self.authenticate("admin", "admin")
        response = self.url_open("/my/page")
        self.assertEqual(response.status_code, 200)

    def test_tour(self):
        """Run a JavaScript tour test."""
        self.start_tour("/web", "my_module_tour", login="admin")
```

### 6. Running Tests
```bash
# All tests for a module
odoo -d mydb --test-enable --stop-after-init -i my_module

# Specific test tag
odoo -d mydb --test-tags /my_module:TestMyModel --stop-after-init

# With pytest-odoo
pytest addons/my_module/tests/test_my_model.py -v -s
```

## Checklist
- [ ] Test files prefixed with `test_`
- [ ] Tests imported in `tests/__init__.py`
- [ ] `@tagged('post_install', '-at_install')` for most tests
- [ ] `setUpClass` for shared test data
- [ ] Tests cover CRUD operations, computed fields, constraints
- [ ] Access rights tested with non-admin user
- [ ] Edge cases tested (empty recordsets, missing data)
- [ ] Controller/HTTP tests use `HttpCase`
