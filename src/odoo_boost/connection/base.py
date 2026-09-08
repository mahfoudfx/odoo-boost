"""Abstract connection interface for Odoo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class OdooConnection(ABC):
    """Abstract base class for Odoo connections."""

    @abstractmethod
    def authenticate(self) -> int:
        """Authenticate and return the user ID."""

    def ensure_authenticated(self) -> int:
        """Ensure connection is authenticated, returning the user ID."""
        try:
            return self.uid
        except RuntimeError:
            return self.authenticate()

    @abstractmethod
    def execute(
        self,
        model: str,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute an ORM method on a model."""

    @abstractmethod
    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        offset: int = 0,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        """Convenience wrapper for search_read."""

    @abstractmethod
    def search_count(
        self,
        model: str,
        domain: list[Any] | None = None,
    ) -> int:
        """Return the count of records matching *domain*."""

    @abstractmethod
    def get_version(self) -> dict[str, Any]:
        """Return server version info."""

    @property
    @abstractmethod
    def uid(self) -> int:
        """Return the authenticated user ID."""
