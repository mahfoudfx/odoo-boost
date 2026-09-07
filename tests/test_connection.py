"""Tests for odoo_boost.connection (ABC, XmlRpcConnection, factory)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from odoo_boost.config.schema import OdooConnection as OdooConnectionConfig
from odoo_boost.connection.base import OdooConnection
from odoo_boost.connection.factory import create_connection
from odoo_boost.connection.xmlrpc import XmlRpcConnection


class TestXmlRpcConnection:
    def _make_conn(self) -> XmlRpcConnection:
        return XmlRpcConnection("http://localhost:8069", "testdb", "admin", "admin")

    def test_authenticate_success(self):
        conn = self._make_conn()
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 2
        conn._common = mock_common
        uid = conn.authenticate()
        assert uid == 2
        assert conn.uid == 2

    def test_authenticate_failure(self):
        conn = self._make_conn()
        mock_common = MagicMock()
        mock_common.authenticate.return_value = False
        conn._common = mock_common
        with pytest.raises(ConnectionError, match="Authentication failed"):
            conn.authenticate()

    def test_uid_before_auth_raises(self):
        conn = self._make_conn()
        with pytest.raises(RuntimeError, match="Not authenticated"):
            _ = conn.uid

    def test_execute(self):
        conn = self._make_conn()
        conn._uid = 2
        mock_object = MagicMock()
        mock_object.execute_kw.return_value = [{"id": 1}]
        conn._object = mock_object
        result = conn.execute("res.partner", "read", [1], fields=["name"])
        mock_object.execute_kw.assert_called_once_with(
            "testdb", 2, "admin", "res.partner", "read", [[1]], {"fields": ["name"]}
        )
        assert result == [{"id": 1}]

    def test_search_read(self):
        conn = self._make_conn()
        conn._uid = 2
        mock_object = MagicMock()
        mock_object.execute_kw.return_value = [{"id": 1, "name": "Test"}]
        conn._object = mock_object
        result = conn.search_read("res.partner", fields=["name"], limit=5)
        assert result == [{"id": 1, "name": "Test"}]

    def test_search_count(self):
        conn = self._make_conn()
        conn._uid = 2
        mock_object = MagicMock()
        mock_object.execute_kw.return_value = 42
        conn._object = mock_object
        count = conn.search_count("res.partner", [("is_company", "=", True)])
        assert count == 42

    def test_get_version(self):
        conn = self._make_conn()
        mock_common = MagicMock()
        mock_common.version.return_value = {"server_version": "18.0"}
        conn._common = mock_common
        version = conn.get_version()
        assert version["server_version"] == "18.0"

    def test_url_trailing_slash_stripped(self):
        conn = XmlRpcConnection("http://localhost:8069/", "testdb", "admin", "admin")
        assert conn._url == "http://localhost:8069"

    def test_timeout_transport_selection(self):
        conn_http = XmlRpcConnection("http://localhost:8069", "db", "u", "p", timeout=15.0)
        transport_http = conn_http._get_transport()
        assert transport_http.timeout == 15.0

        conn_https = XmlRpcConnection("https://example.com", "db", "u", "p", timeout=25.0)
        transport_https = conn_https._get_transport()
        assert transport_https.timeout == 25.0


class TestConnectionFactory:
    def test_create_xmlrpc(self, sample_connection_config):
        conn = create_connection(sample_connection_config)
        assert isinstance(conn, XmlRpcConnection)

    def test_unsupported_protocol_raises(self):
        # Pydantic Literal won't allow other values normally, so we
        # use model_construct to bypass validation for this edge case
        cfg = OdooConnectionConfig.model_construct(
            url="http://localhost",
            database="db",
            username="admin",
            password="admin",
            protocol="jsonrpc",
        )
        with pytest.raises(ValueError, match="Unsupported protocol"):
            create_connection(cfg)


class TestOdooConnectionABC:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            OdooConnection()  # type: ignore[abstract]
