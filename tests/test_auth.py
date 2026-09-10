"""Tests for odoo_boost.mcp_server.auth (static bearer token verification)."""

from __future__ import annotations

import asyncio

import pytest

from odoo_boost.mcp_server.auth import StaticTokenVerifier


def _verify(verifier: StaticTokenVerifier, token: str):
    return asyncio.run(verifier.verify_token(token))


class TestStaticTokenVerifier:
    def test_empty_token_rejected_at_construction(self):
        with pytest.raises(ValueError):
            StaticTokenVerifier("")

    def test_valid_token_returns_access_token(self):
        verifier = StaticTokenVerifier("s3cret")
        access = _verify(verifier, "s3cret")
        assert access is not None
        assert access.token == "s3cret"
        assert access.client_id == "odoo-boost"

    def test_invalid_token_returns_none(self):
        verifier = StaticTokenVerifier("s3cret")
        assert _verify(verifier, "wrong") is None
        assert _verify(verifier, "") is None
