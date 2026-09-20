"""XML-RPC client for Odoo instances exposing the external RPC API."""

from __future__ import annotations

import http.client
import xmlrpc.client
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, cast

from odoo_boost.connection.base import OdooConnection as BaseConnection


@contextmanager
def _translate_connection_errors(url: str) -> Iterator[None]:
    """Map low-level XML-RPC/OS errors to a friendly ``ConnectionError``."""
    try:
        yield
    except xmlrpc.client.ProtocolError as exc:
        raise ConnectionError(
            f"Cannot connect to Odoo at {url} ({exc.errcode} {exc.errmsg}). "
            "Ensure your Odoo instance and reverse proxy are running."
        ) from exc
    except OSError as exc:
        raise ConnectionError(
            f"Cannot reach Odoo at {url}: {exc}. Ensure your Odoo instance is running."
        ) from exc


class _TimeoutTransport(xmlrpc.client.Transport):
    """HTTP transport with an explicit socket timeout."""

    def __init__(
        self,
        timeout: float = 30.0,
        use_datetime: bool = False,
        use_builtin_types: bool = False,
    ) -> None:
        super().__init__(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
        self.timeout = timeout

    def make_connection(self, host: Any) -> http.client.HTTPConnection:
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


class _SafeTimeoutTransport(xmlrpc.client.SafeTransport):
    """HTTPS transport with an explicit socket timeout."""

    def __init__(
        self,
        timeout: float = 30.0,
        use_datetime: bool = False,
        use_builtin_types: bool = False,
    ) -> None:
        super().__init__(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
        self.timeout = timeout

    def make_connection(self, host: Any) -> http.client.HTTPSConnection:
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


class XmlRpcConnection(BaseConnection):
    """Connects to Odoo via XML-RPC (works on all supported versions)."""

    def __init__(
        self,
        url: str,
        database: str,
        username: str,
        password: str,
        timeout: float = 30.0,
    ) -> None:
        self._url = url.rstrip("/")
        self._database = database
        self._username = username
        self._password = password
        self._timeout = timeout
        self._uid: int | None = None
        self._common: xmlrpc.client.ServerProxy | None = None
        self._object: xmlrpc.client.ServerProxy | None = None

    def _get_transport(self) -> xmlrpc.client.Transport:
        if self._url.lower().startswith("https://"):
            return _SafeTimeoutTransport(timeout=self._timeout)
        return _TimeoutTransport(timeout=self._timeout)

    # -- lazy proxy helpers --------------------------------------------------

    @property
    def _common_proxy(self) -> xmlrpc.client.ServerProxy:
        if self._common is None:
            self._common = xmlrpc.client.ServerProxy(
                f"{self._url}/xmlrpc/2/common",
                transport=self._get_transport(),
                allow_none=True,
            )
        return self._common

    @property
    def _object_proxy(self) -> xmlrpc.client.ServerProxy:
        if self._object is None:
            self._object = xmlrpc.client.ServerProxy(
                f"{self._url}/xmlrpc/2/object",
                transport=self._get_transport(),
                allow_none=True,
            )
        return self._object

    # -- public interface ----------------------------------------------------

    def authenticate(self) -> int:
        with _translate_connection_errors(self._url):
            uid = self._common_proxy.authenticate(
                self._database, self._username, self._password, {}
            )

        if not uid:
            raise ConnectionError(f"Authentication failed for {self._username}@{self._database}")
        self._uid = int(uid)  # type: ignore[arg-type]
        return self._uid

    @property
    def uid(self) -> int:
        if self._uid is None:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return self._uid

    def execute(
        self,
        model: str,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        uid = self.ensure_authenticated()
        with _translate_connection_errors(self._url):
            return self._object_proxy.execute_kw(
                self._database,
                uid,
                self._password,
                model,
                method,
                list(args),
                kwargs or {},
            )

    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        offset: int = 0,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {"offset": offset}
        if fields is not None:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        result = self.execute(model, "search_read", domain or [], **kwargs)
        return cast("list[dict[str, Any]]", result)

    def search_count(
        self,
        model: str,
        domain: list[Any] | None = None,
    ) -> int:
        return int(self.execute(model, "search_count", domain or []))

    def get_version(self) -> dict[str, Any]:
        with _translate_connection_errors(self._url):
            return self._common_proxy.version()  # type: ignore[return-value]
