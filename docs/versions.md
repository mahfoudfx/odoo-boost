# Odoo version support and onboarding

Odoo Boost registers the on-premise series **14.0 through 19.0** in
`src/odoo_boost/versions.py`. Registration describes curated development guidance
and documentation mappings, not a guarantee that every deployment, Enterprise
addon or third-party override has been integration-tested. Runtime tools use the
configured user's XML-RPC permissions; a live instance is not needed for local
inspection, skills or documentation-link lookup.

## Shared knowledge, effective facts, release deltas

Universal principles live in `guidelines/core/`. `VERSION_REGISTRY` contains an
explicit baseline and parent-linked `VersionSpec` entries with only changed
compatibility facts and documentation paths. `get_version_profile()` resolves
these into an immutable effective profile. Generated instructions include the full expert guidelines, a summary of the
target's effective rules, and its release note. Topic files and specialized
skills remain available separately. Older release notes are not concatenated:
that would reintroduce removed APIs as current advice.

The registry supplies view roots/modifiers, relational command conventions,
asset declarations, display-name overrides, JSON-RPC route types and search-view
group attributes. It is a focused compatibility reference, not an exhaustive
model of the Odoo API. Specialized examples must be checked against the target
source before use. For example, Odoo 17 still uses `tree`, Odoo 18 uses `list`,
and Odoo 19 changes controller route type `json` to `jsonrpc`.

Version normalization is shared by installation, guideline composition and
`search_docs`. A configured version is enough for offline documentation lookup;
lookup never queries a server merely to choose links. `application_info` reports
the detected series and whether it is registered, which helps identify stale
project configuration after an upgrade. Update the configuration and regenerate
agent files when changing the deployment's target version.

## Unknown versions

A new major (including Odoo 20 until explicitly registered), an unregistered
SaaS series, or an unparseable version does not inherit the highest known release.
Shared guidance remains available with an uncertainty notice. No guessed
version-specific documentation links or fallback-linter deprecation rules are
emitted. Inspect the target source/configuration first; use runtime metadata
only for facts that require it. `search_docs` is an offline curated-link lookup,
not a full-text search or a guarantee that a remote page is currently reachable.
Legacy Odoo 14 topics use the official reference index where a deep link has
not been verified.

## Add a version

1. **Register:** add one `VersionSpec` with an explicit parent in
   `VERSION_REGISTRY`. Do not add branches to consumers or promote an unknown
   version by numeric comparison.
2. **Documentation sources:** verify official documentation/source for that
   series and add only changed topic paths to `doc_paths`. Shared topics are in
   `mcp_server/tools/search_docs.py`.
3. **API changes:** add changed, introduced, deprecated or removed compatibility
   facts to `features`. Check actual Odoo source for changes not covered by docs.
   A new fact needs a consumer only when it changes executable behavior; avoid
   an abstract feature system for facts no tool or agent needs.
4. **Guidelines and skills:** add `guidelines/core/versions/v<major>.md` with a
   concise delta and primary-source links. Keep unchanged principles in shared
   guidance. Specialized skills should refer to effective target rules rather
   than copy the version matrix.
5. **Tests and fixtures:** extend `tests/test_versions.py` with positive and
   negative cases across neighboring releases. Add tool regressions only for
   affected runtime behavior. Verify notes are packaged and generated references
   exist. The synthetic future-release test proves consumers need no changes.
6. **Validate:** run Ruff, mypy, the pytest suite and wheel smoke checks from
   [CONTRIBUTING](../CONTRIBUTING.md). Exercise affected tools on a disposable
   target-version Odoo instance with representative addons and a restricted
   user before claiming live compatibility. Update this support statement.

Do not remove an older release merely because a newer one is registered. Keep
unknown-version tests and old-version regression fixtures independent of the
new release.
