<!-- Adapted from letzdoo/claude-marketplace. Examples are references, not active-version facts. Odoo Boost version guidance and the target source take precedence. -->

# Odoo Test Patterns Guide

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEST PATTERNS GUIDE                                                         ║
║  Comprehensive testing patterns for Odoo modules across all versions         ║
║  Generate when include_tests: true is specified                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Test File Structure

```
{module_name}/
├── tests/
│   ├── __init__.py
│   ├── common.py              # Shared test data and base classes
│   ├── test_{model_name}.py   # Model unit tests
│   ├── test_security.py       # Security/access tests
│   ├── test_translation.py    # Translation contracts, when applicable
│   └── test_integration.py    # Integration tests
```

## Test Class Hierarchy

```python
# tests/__init__.py
from . import test_my_model
from . import test_security
from . import test_integration
```

## Base Test Classes

### Common Test Setup

Apply the [testing guidelines](../../../guidelines/core/testing.md) for language,
assertions, and security coverage. Set the shared language before fixture creation
and carry it onto each dedicated user.

```python
# tests/common.py
from odoo.tests import TransactionCase


class TestMyModuleCommon(TransactionCase):
    """Common setup for all tests in this module"""

    test_lang = "en_US"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, lang=cls.test_lang))
        cls.env.user.lang = cls.test_lang

        # Create shared test data
        cls.company = cls.env.ref("base.main_company")
        cls.user_admin = cls.env.ref("base.user_admin")

        # Create test partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )

        # Create test user with specific groups
        cls.user_manager = cls.env["res.users"].create(
            {
                "name": "Test Manager",
                "login": "test_manager",
                "email": "manager@example.com",
                "lang": cls.test_lang,
                "company_id": cls.company.id,
                "company_ids": [(6, 0, [cls.company.id])],
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("my_module.group_manager").id,
                        ],
                    )
                ],
            }
        )

        cls.user_basic = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "user@example.com",
                "lang": cls.test_lang,
                "company_id": cls.company.id,
                "company_ids": [(6, 0, [cls.company.id])],
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                        ],
                    )
                ],
            }
        )
```

## Unit Tests

### Basic Model Tests

```python
# tests/test_my_model.py
from psycopg2.errors import NotNullViolation
from odoo.tests import tagged
from odoo.exceptions import ValidationError, UserError
from .common import TestMyModuleCommon


@tagged("post_install", "-at_install")
class TestMyModel(TestMyModuleCommon):
    """Unit tests for my.model"""

    def test_create_record(self):
        """Test basic record creation"""
        record = self.env["my.model"].create(
            {
                "name": "Test Record",
                "partner_id": self.partner.id,
            }
        )
        self.assertTrue(record.id)
        self.assertEqual(record.name, "Test Record")
        self.assertEqual(record.state, "draft")

    def test_create_with_defaults(self):
        """Test creation with default values"""
        record = self.env["my.model"].create(
            {
                "name": "Test",
            }
        )
        # Check default company
        self.assertEqual(record.company_id, self.env.company)
        # Check default state
        self.assertEqual(record.state, "draft")

    def test_name_required(self):
        """Test the database NOT NULL constraint on name."""
        with self.assertRaises(NotNullViolation):
            self.env["my.model"].create({})

    def test_state_workflow(self):
        """Test state transitions"""
        record = self.env["my.model"].create(
            {
                "name": "Workflow Test",
            }
        )

        # Add required line for confirmation
        self.env["my.model.line"].create(
            {
                "model_id": record.id,
                "name": "Line 1",
                "quantity": 1,
            }
        )

        # Test confirm
        self.assertEqual(record.state, "draft")
        record.action_confirm()
        self.assertEqual(record.state, "confirmed")

        # Test done
        record.action_done()
        self.assertEqual(record.state, "done")

    def test_confirm_without_lines_fails(self):
        """Test that confirmation requires lines"""
        record = self.env["my.model"].create(
            {
                "name": "No Lines Test",
            }
        )

        with self.assertRaises(UserError):
            record.action_confirm()
```

### Computed Field Tests

```python
@tagged("post_install", "-at_install")
class TestMyModelComputed(TestMyModuleCommon):
    """Test computed fields"""

    def test_compute_total(self):
        """Test total computation"""
        record = self.env["my.model"].create(
            {
                "name": "Computed Test",
            }
        )

        # Create lines
        self.env["my.model.line"].create(
            {
                "model_id": record.id,
                "name": "Line 1",
                "quantity": 2,
                "price_unit": 10.0,
            }
        )
        self.env["my.model.line"].create(
            {
                "model_id": record.id,
                "name": "Line 2",
                "quantity": 3,
                "price_unit": 20.0,
            }
        )

        # Total should be (2*10) + (3*20) = 80
        self.assertEqual(record.total_amount, 80.0)

    def test_compute_line_count(self):
        """Test line count computation"""
        record = self.env["my.model"].create({"name": "Count Test"})
        self.assertEqual(record.line_count, 0)

        self.env["my.model.line"].create(
            {
                "model_id": record.id,
                "name": "Line 1",
            }
        )
        self.assertEqual(record.line_count, 1)
```

### Constraint Tests

These SQL examples assume database constraints; a Python constraint should assert
its actual exception class, usually `ValidationError`.

```python
from psycopg2.errors import UniqueViolation


@tagged("post_install", "-at_install")
class TestMyModelConstraints(TestMyModuleCommon):
    """Test model constraints"""

    def test_date_constraint(self):
        """Test date_start must be before date_end"""
        with self.assertRaises(ValidationError):
            self.env["my.model"].create(
                {
                    "name": "Date Test",
                    "date_start": "2024-12-31",
                    "date_end": "2024-01-01",  # Before start
                }
            )

    def test_unique_code_per_company(self):
        """Test unique code constraint"""
        self.env["my.model"].create(
            {
                "name": "First",
                "code": "TEST001",
            }
        )

        with self.assertRaises(UniqueViolation):
            self.env["my.model"].create(
                {
                    "name": "Duplicate",
                    "code": "TEST001",  # Same code
                }
            )

    def test_positive_quantity(self):
        """Test quantity must be positive"""
        record = self.env["my.model"].create({"name": "Qty Test"})

        with self.assertRaises(ValidationError):
            self.env["my.model.line"].create(
                {
                    "model_id": record.id,
                    "name": "Negative",
                    "quantity": -1,
                }
            )
```

## Security Tests

These examples assume basic users can create, read, and write their own records,
while managers can also delete and confirm them. Adapt the fixtures and expected
exception to the module's actual access contract. The confirmation tests exercise
a method's group guard with otherwise valid data and write access.

```python
# tests/test_security.py
from odoo.tests import tagged
from odoo.exceptions import AccessError
from .common import TestMyModuleCommon


@tagged("post_install", "-at_install")
class TestMyModelSecurity(TestMyModuleCommon):
    """Security and access rights tests"""

    def _create_confirmable_record(self, user):
        record = self.env["my.model"].with_user(user).create({"name": "Guard Test"})
        self.env["my.model.line"].with_user(user).create(
            {"model_id": record.id, "name": "Line 1", "quantity": 1}
        )
        return record

    def test_user_can_read_own_records(self):
        """Test basic user can read their own records"""
        record = (
            self.env["my.model"]
            .with_user(self.user_basic)
            .create(
                {
                    "name": "User Record",
                }
            )
        )

        # Should be able to read
        record.with_user(self.user_basic).read(["name"])

    def test_user_cannot_delete(self):
        """Test basic user cannot delete records"""
        record = self.env["my.model"].create({"name": "Test"})

        with self.assertRaises(AccessError):
            record.with_user(self.user_basic).unlink()
        self.assertTrue(record.exists())

    def test_manager_can_delete(self):
        """Test manager can delete records"""
        record = self.env["my.model"].create({"name": "Test"})
        record.with_user(self.user_manager).unlink()
        self.assertFalse(record.exists())

    def test_basic_user_cannot_confirm(self):
        record = self._create_confirmable_record(self.user_basic)
        # Establish that ordinary writes work before exercising the method guard.
        record.write({"name": "Ready for Confirmation"})
        self.assertEqual(record.state, "draft")

        with self.assertRaises(AccessError):
            record.action_confirm()
        self.assertEqual(record.state, "draft")

    def test_manager_can_confirm(self):
        record = self._create_confirmable_record(self.user_manager)
        record.action_confirm()
        self.assertEqual(record.state, "confirmed")

    def test_multi_company_isolation(self):
        """Test records are isolated by company"""
        # Create second company
        company2 = self.env["res.company"].create(
            {
                "name": "Company 2",
            }
        )

        # Create user in company2
        user_company2 = self.env["res.users"].create(
            {
                "name": "User Company 2",
                "login": "user_c2",
                "lang": self.test_lang,
                "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
                "company_id": company2.id,
                "company_ids": [(6, 0, [company2.id])],
            }
        )

        # Create record in main company
        record = self.env["my.model"].create(
            {
                "name": "Main Company Record",
                "company_id": self.company.id,
            }
        )

        # User in company2 should not see it
        records = self.env["my.model"].with_user(user_company2).search([])
        self.assertNotIn(record, records)
```

Odoo's `assertRaises` helper rolls back its savepoint on the expected exception.
State assertions after it verify the transaction outcome; proving that a guard
prevents an external side effect also requires observing that boundary, such as
asserting that a patched mail sender was never called. Keep the guard itself real.

For translation-specific examples, use
[Testing Translations](translation-i18n-patterns.md#testing-translations).

## Integration Tests

```python
# tests/test_integration.py
from odoo.tests import tagged, HttpCase
from .common import TestMyModuleCommon


@tagged("post_install", "-at_install")
class TestMyModelIntegration(TestMyModuleCommon):
    """Integration tests"""

    def test_full_workflow(self):
        """Test complete record lifecycle"""
        # Create
        record = self.env["my.model"].create(
            {
                "name": "Full Workflow Test",
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(record.state, "draft")

        # Add lines
        self.env["my.model.line"].create(
            {
                "model_id": record.id,
                "name": "Line 1",
                "quantity": 1,
                "price_unit": 100,
            }
        )

        # Confirm
        record.action_confirm()
        self.assertEqual(record.state, "confirmed")

        # Check partner was notified (if mail integration)
        if hasattr(record, "message_ids"):
            self.assertTrue(len(record.message_ids) > 0)

        # Complete
        record.action_done()
        self.assertEqual(record.state, "done")

        # Cannot delete done records
        from odoo.exceptions import UserError

        with self.assertRaises(UserError):
            record.unlink()

    def test_copy_record(self):
        """Test record duplication"""
        record = self.env["my.model"].create(
            {
                "name": "Original",
                "state": "confirmed",
            }
        )

        # Add line
        self.env["my.model.line"].create(
            {
                "model_id": record.id,
                "name": "Line",
            }
        )

        # Copy
        copy = record.copy()

        self.assertNotEqual(copy.id, record.id)
        self.assertIn("(copy)", copy.name)
        self.assertEqual(copy.state, "draft")  # Reset to draft
        self.assertEqual(len(copy.line_ids), len(record.line_ids))  # Lines copied

    def test_batch_operations(self):
        """Test batch create and write"""
        # Batch create
        records = self.env["my.model"].create(
            [
                {"name": "Batch 1"},
                {"name": "Batch 2"},
                {"name": "Batch 3"},
            ]
        )
        self.assertEqual(len(records), 3)

        # Batch write
        records.write({"active": False})
        for record in records:
            self.assertFalse(record.active)
```

## HTTP/Tour Tests

```python
# tests/test_ui.py
from odoo.tests import tagged, HttpCase


@tagged("post_install", "-at_install")
class TestMyModelUI(HttpCase):
    """UI/Tour tests"""

    def test_ui_create_record(self):
        """Test creating record via UI"""
        self.start_tour(
            "/web",
            "my_module_create_tour",
            login="admin",
        )
```

## Test Tags Reference

| Tag | Meaning |
|-----|---------|
| `post_install` | Run after module installation |
| `-at_install` | Don't run during installation |
| `standard` | Standard test (default) |
| `external` | Requires external services |

## Version-Specific Test Patterns

### v16+ with Command Class

```python
def test_create_with_command(self):
    """Test creation with Command class (v16+)"""
    from odoo.fields import Command

    record = self.env["my.model"].create(
        {
            "name": "Command Test",
            "line_ids": [
                Command.create({"name": "Line 1", "quantity": 1}),
                Command.create({"name": "Line 2", "quantity": 2}),
            ],
        }
    )
    self.assertEqual(len(record.line_ids), 2)
```

### v17+ Visibility Testing

```python
def test_view_visibility(self):
    """Test view visibility conditions (v17+)"""
    record = self.env["my.model"].create(
        {
            "name": "Visibility Test",
            "state": "draft",
        }
    )

    # Get form view
    view = self.env["ir.ui.view"].search(
        [
            ("model", "=", "my.model"),
            ("type", "=", "form"),
        ],
        limit=1,
    )

    # In v17+, visibility uses Python expressions
    # Test that the view renders correctly
    fields_view = self.env["my.model"].get_views([(view.id, "form")])["views"]["form"]
    self.assertIn("invisible", str(fields_view))
```

### v18+ Multi-Company Testing

```python
from odoo.exceptions import UserError


def test_check_company_auto(self):
    """Test automatic company checking (v18+)"""
    # Create partner in different company
    company2 = self.env["res.company"].create({"name": "Company 2"})
    partner_c2 = self.env["res.partner"].create(
        {
            "name": "Partner C2",
            "company_id": company2.id,
        }
    )

    # Should raise if check_company=True
    with self.assertRaises(UserError):
        self.env["my.model"].create(
            {
                "name": "Cross Company",
                "company_id": self.company.id,
                "partner_id": partner_c2.id,  # Different company
            }
        )
```

## Running Tests

```bash
# Run all tests for a module
./odoo-bin -d testdb -i my_module --test-enable --stop-after-init

# Run specific test class
./odoo-bin -d testdb --test-tags my_module.TestMyModel

# Run with coverage
coverage run ./odoo-bin -d testdb -i my_module --test-enable --stop-after-init
coverage report
```

## Test Generation Checklist

For each model, generate tests for:

- [ ] Basic CRUD operations (create, read, update, delete)
- [ ] All computed fields
- [ ] All constraints (Python and SQL)
- [ ] State workflow transitions
- [ ] Access rights by user group
- [ ] Record rules (multi-company, ownership)
- [ ] Onchange methods
- [ ] Action methods (buttons)
- [ ] Copy behavior
- [ ] Batch operations
