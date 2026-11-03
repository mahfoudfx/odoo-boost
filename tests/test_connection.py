"""Tests for odoo_boost.connection (ABC, XmlRpcConnection, factory)."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
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

    def test_ensure_authenticated_when_cached(self):
        conn = self._make_conn()
        conn._uid = 5
        assert conn.ensure_authenticated() == 5

    def test_ensure_authenticated_when_none(self):
        conn = self._make_conn()
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 7
        conn._common = mock_common
        assert conn.ensure_authenticated() == 7
        assert conn.uid == 7

    def test_authenticate_protocol_error(self):
        import xmlrpc.client

        conn = self._make_conn()
        mock_common = MagicMock()
        mock_common.authenticate.side_effect = xmlrpc.client.ProtocolError(
            "http://localhost:8069/xmlrpc/2/common", 502, "Bad Gateway", {}
        )
        conn._common = mock_common
        with pytest.raises(ConnectionError, match="502 Bad Gateway"):
            conn.authenticate()

    def test_authenticate_os_error(self):
        conn = self._make_conn()
        mock_common = MagicMock()
        mock_common.authenticate.side_effect = ConnectionRefusedError("Connection refused")
        conn._common = mock_common
        with pytest.raises(ConnectionError, match="Cannot reach Odoo"):
            conn.authenticate()

    def test_execute_lazy_authentication(self):
        conn = self._make_conn()
        assert conn._uid is None

        mock_common = MagicMock()
        mock_common.authenticate.return_value = 3
        conn._common = mock_common

        mock_object = MagicMock()
        mock_object.execute_kw.return_value = [{"id": 1}]
        conn._object = mock_object

        result = conn.execute("res.partner", "read", [1])
        assert result == [{"id": 1}]
        assert conn.uid == 3
        mock_common.authenticate.assert_called_once()

    def test_parallel_rpc_calls_do_not_overlap(self):
        conn = self._make_conn()
        transport_busy = Lock()
        start = Barrier(8)

        def request(result):
            # Model the single in-flight request supported by HTTPConnection.
            assert transport_busy.acquire(blocking=False), "overlapping RPC requests"
            try:
                time.sleep(0.01)
                return result
            finally:
                transport_busy.release()

        common = MagicMock()
        common.authenticate.side_effect = lambda *args: request(2)
        common.version.side_effect = lambda: request({"server_version": "18.0"})
        conn._common = common
        objects = MagicMock()
        objects.execute_kw.side_effect = lambda *args: request([{"id": 1}])
        conn._object = objects

        def call(index):
            start.wait(timeout=5)
            if index % 2:
                return conn.get_version()
            return conn.execute("res.partner", "read", [1])

        with ThreadPoolExecutor(max_workers=8) as workers:
            results = list(workers.map(call, range(8)))

        assert results == [[{"id": 1}], {"server_version": "18.0"}] * 4
        common.authenticate.assert_called_once()

    def test_failed_rpc_releases_connection_for_next_call(self):
        conn = self._make_conn()
        conn._uid = 2
        objects = MagicMock()
        objects.execute_kw.side_effect = [OSError("disconnected"), [{"id": 1}]]
        conn._object = objects
        with pytest.raises(ConnectionError):
            conn.execute("res.partner", "read", [1])
        with ThreadPoolExecutor(max_workers=1) as workers:
            result = workers.submit(conn.execute, "res.partner", "read", [1]).result(timeout=5)
        assert result == [{"id": 1}]


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
