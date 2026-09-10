"""Static bearer-token verification for the HTTP MCP transport."""

from __future__ import annotations

import hmac

from mcp.server.auth.provider import AccessToken, TokenVerifier


class StaticTokenVerifier(TokenVerifier):
    """Verify a single pre-shared bearer token.

    The MCP SDK wraps the Streamable HTTP route in an authentication middleware
    whenever a ``token_verifier`` is supplied, so passing an instance of this
    class is enough to require ``Authorization: Bearer <token>``.
    """

    def __init__(self, token: str, client_id: str = "odoo-boost") -> None:
        if not token:
            raise ValueError("StaticTokenVerifier requires a non-empty token.")
        self._token = token
        self._client_id = client_id

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or not hmac.compare_digest(token, self._token):
            return None
        return AccessToken(token=token, client_id=self._client_id, scopes=[])
