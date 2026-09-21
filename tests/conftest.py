"""Shared pytest fixtures for Odoo Boost tests."""

from __future__ import annotations

from typing import Any

import pytest

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.config.schema import OdooConnection as OdooConnectionConfig
from odoo_boost.connection.base import OdooConnection

# ---------------------------------------------------------------------------
# MockOdooConnection — in-memory fake that satisfies the OdooConnection ABC
# ---------------------------------------------------------------------------


class MockOdooConnection(OdooConnection):
    """In-memory mock Odoo connection for testing.

    Stores records keyed by model name. Use ``seed()`` to populate data.
    """

    def __init__(self) -> None:
        self._uid: int | None = None
        self._records: dict[str, list[dict[str, Any]]] = {}
        self._version: dict[str, Any] = {
            "server_version": "18.0",
            "server_serie": "18.0",
            "server_version_info": [18, 0, 0, "final", 0, ""],
            "protocol_version": 1,
        }

    # -- seeding helpers -----------------------------------------------------

    def seed(self, model: str, records: list[dict[str, Any]]) -> None:
        """Populate the mock store with records for *model*."""
        self._records[model] = records

    # -- ABC implementation --------------------------------------------------

    def authenticate(self) -> int:
        self._uid = 2
        return self._uid

    @property
    def uid(self) -> int:
        if self._uid is None:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return self._uid

    def execute(self, model: str, method: str, *args: Any, **kwargs: Any) -> Any:
        if method == "search_read":
            domain = args[0] if args else []
            return self._filter(model, domain, **kwargs)
        if method == "search_count":
            domain = args[0] if args else []
            return len(self._filter(model, domain))
        if method == "read_group":
            return [{"state": "draft", "amount_total": 100.0, "state_count": 2}]
        # For arbitrary method calls, return a generic response
        return {"method": method, "args": list(args), "kwargs": kwargs}

    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        offset: int = 0,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        records = self._filter(model, domain or [])
        if order:
            # Simple sort: only handle "field_name" or "field_name asc/desc"
            parts = order.split(",")[0].strip().split()
            key = parts[0]
            reverse = len(parts) > 1 and parts[1].lower() == "desc"
            records = sorted(records, key=lambda r: r.get(key, ""), reverse=reverse)
        records = records[offset:]
        if limit is not None:
            records = records[:limit]
        if fields:
            records = [{k: r.get(k) for k in ["id"] + fields if k in r} for r in records]
        return records

    def search_count(self, model: str, domain: list[Any] | None = None) -> int:
        return len(self._filter(model, domain or []))

    def get_version(self) -> dict[str, Any]:
        return dict(self._version)

    # -- internal ------------------------------------------------------------

    def _filter(self, model: str, domain: list[Any], **kwargs: Any) -> list[dict[str, Any]]:
        """Very simple domain filtering — handles common patterns."""
        records = list(self._records.get(model, []))
        for clause in domain:
            if not isinstance(clause, (list, tuple)) or len(clause) != 3:
                continue
            field, op, value = clause
            if op == "=":
                records = [r for r in records if r.get(field) == value]
            elif op == "!=":
                records = [r for r in records if r.get(field) != value]
            elif op == "ilike":
                records = [r for r in records if value.lower() in str(r.get(field, "")).lower()]
            elif op == "in":
                records = [r for r in records if r.get(field) in value]
        return records


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_connection() -> MockOdooConnection:
    """Return a fresh MockOdooConnection."""
    return MockOdooConnection()


@pytest.fixture()
def sample_connection_config() -> OdooConnectionConfig:
    """Return a sample OdooConnection config."""
    return OdooConnectionConfig(
        url="http://localhost:8069",
        database="testdb",
        username="admin",
        password="admin",
    )


@pytest.fixture()
def sample_config(sample_connection_config: OdooConnectionConfig) -> OdooBoostConfig:
    """Return a sample OdooBoostConfig."""
    return OdooBoostConfig(
        connection=sample_connection_config,
        odoo_version="18.0",
        agents=["claude_code", "cursor"],
        project_path=".",
        # Unit tests create temporary addon paths outside the repository.
        allow_external_local_paths=True,
    )


@pytest.fixture()
def server_context(mock_connection: MockOdooConnection, sample_config: OdooBoostConfig):
    """Set up the global MCP server context with a mock connection, then tear down."""
    from odoo_boost.mcp_server.context import ServerContext, set_context

    mock_connection.authenticate()
    _seed_default_data(mock_connection)

    ctx = ServerContext(connection=mock_connection, config=sample_config)
    set_context(ctx)
    yield ctx

    # Reset context
    from odoo_boost.mcp_server.context import reset_context

    reset_context()


def _seed_default_data(conn: MockOdooConnection) -> None:
    """Populate the mock connection with data the MCP tools will query."""
    conn.seed(
        "ir.module.module",
        [
            {
                "id": 1,
                "name": "base",
                "shortdesc": "Base",
                "summary": "Core module",
                "description": "",
                "author": "Odoo SA",
                "website": "https://www.odoo.com",
                "installed_version": "18.0.1.0.0",
                "state": "installed",
                "category_id": [1, "Hidden"],
                "license": "LGPL-3",
                "application": False,
            },
            {
                "id": 2,
                "name": "sale",
                "shortdesc": "Sales",
                "summary": "Sales management",
                "description": "",
                "author": "Odoo SA",
                "website": "https://www.odoo.com",
                "installed_version": "18.0.1.0.0",
                "state": "installed",
                "category_id": [2, "Sales"],
                "license": "LGPL-3",
                "application": True,
            },
            {
                "id": 3,
                "name": "purchase",
                "shortdesc": "Purchase",
                "summary": "Purchase management",
                "description": "",
                "author": "Odoo SA",
                "website": "https://www.odoo.com",
                "installed_version": "18.0.1.0.0",
                "state": "uninstalled",
                "category_id": [3, "Purchases"],
                "license": "LGPL-3",
                "application": True,
            },
        ],
    )
    conn.seed(
        "ir.model",
        [
            {"id": 1, "model": "res.partner", "name": "Contact", "info": "", "field_id": [1, 2, 3]},
            {"id": 2, "model": "sale.order", "name": "Sales Order", "info": "", "field_id": [4, 5]},
        ],
    )
    conn.seed(
        "ir.model.fields",
        [
            {
                "id": 1,
                "model_id": 1,
                "name": "name",
                "field_description": "Name",
                "ttype": "char",
                "relation": False,
                "required": True,
                "readonly": False,
                "store": True,
                "index": True,
                "help": False,
            },
            {
                "id": 2,
                "model_id": 1,
                "name": "email",
                "field_description": "Email",
                "ttype": "char",
                "relation": False,
                "required": False,
                "readonly": False,
                "store": True,
                "index": False,
                "help": "Contact email",
            },
            {
                "id": 3,
                "model_id": 1,
                "name": "company_id",
                "field_description": "Company",
                "ttype": "many2one",
                "relation": "res.company",
                "required": False,
                "readonly": False,
                "store": True,
                "index": True,
                "help": False,
            },
        ],
    )
    conn.seed(
        "ir.model.data",
        [
            {
                "id": 1,
                "module": "base",
                "name": "partner_admin",
                "model": "res.partner",
                "res_id": 1,
                "noupdate": True,
            },
            {
                "id": 2,
                "module": "base",
                "name": "model_ir_model",
                "model": "ir.model",
                "res_id": 1,
                "noupdate": True,
            },
        ],
    )
    conn.seed(
        "ir.ui.view",
        [
            {
                "id": 1,
                "name": "res.partner.form",
                "model": "res.partner",
                "type": "form",
                "arch": "<form><field name='name'/></form>",
                "inherit_id": False,
                "priority": 16,
                "active": True,
            },
            {
                "id": 2,
                "name": "res.partner.tree",
                "model": "res.partner",
                "type": "tree",
                "arch": "<tree><field name='name'/></tree>",
                "inherit_id": False,
                "priority": 16,
                "active": True,
            },
        ],
    )
    conn.seed(
        "ir.ui.menu",
        [
            {
                "id": 1,
                "name": "Sales",
                "parent_id": False,
                "action": "ir.actions.act_window,1",
                "sequence": 10,
                "child_id": [2],
                "complete_name": "Sales",
            },
            {
                "id": 2,
                "name": "Orders",
                "parent_id": 1,
                "action": "ir.actions.act_window,2",
                "sequence": 1,
                "child_id": [],
                "complete_name": "Sales / Orders",
            },
        ],
    )
    conn.seed(
        "ir.model.access",
        [
            {
                "id": 1,
                "name": "access_res_partner_user",
                "model_id": [1, "res.partner"],
                "group_id": [1, "base.group_user"],
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": False,
            },
        ],
    )
    conn.seed(
        "ir.rule",
        [
            {
                "id": 1,
                "name": "res_partner_rule",
                "model_id": [1, "res.partner"],
                "groups": [],
                "domain_force": "[(1, '=', 1)]",
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
                "global": True,
            },
        ],
    )
    conn.seed(
        "ir.config_parameter",
        [
            {"id": 1, "key": "web.base.url", "value": "http://localhost:8069"},
            {"id": 2, "key": "database.uuid", "value": "test-uuid-1234"},
        ],
    )
    conn.seed(
        "ir.module.module.dependency",
        [
            {"id": 1, "name": "base", "auto_install_required": False},
        ],
    )
    conn.seed(
        "res.partner",
        [
            {"id": 1, "name": "Azure Interior", "email": "azure@example.com", "is_company": True},
            {"id": 2, "name": "Joel Willis", "email": "joel@example.com", "is_company": False},
        ],
    )
    conn.seed(
        "base.automation",
        [
            {
                "id": 1,
                "name": "Auto-assign partner",
                "model_name": "res.partner",
                "trigger": "on_create",
                "active": True,
                "action_server_ids": [1],
            },
        ],
    )
    conn.seed(
        "ir.actions.server",
        [
            {
                "id": 1,
                "name": "Update partner",
                "model_name": "res.partner",
                "state": "code",
                "code": "record.write({'active': True})",
                "sequence": 5,
            },
        ],
    )
