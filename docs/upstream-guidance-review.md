# Upstream guidance review

Reviewed 2026-11-02. This is a static comparison of selected upstream files with the bundled guidance and tools, not a client performance evaluation. Revisions identify reviewed source, not an assertion that all upstream content was adopted. No third-party installer, hook, or example wizard stages were executed. The adapted wizard helpers were exercised in an isolated temporary directory.

## Decisions

### OCA/maintainer-tools

Reviewed `master` at `b8311a95009805a6e5593f0390f52c0fa350117f`; repository license reported by GitHub: `AGPL-3.0`.

**Adapt**: Document README fragments and optional business context only for OCA repositories that use their generator; do not import the old example manifest.

Reviewed files:
- [README.md](https://github.com/OCA/maintainer-tools/blob/b8311a95009805a6e5593f0390f52c0fa350117f/README.md)
- [template/module/__manifest__.py](https://github.com/OCA/maintainer-tools/blob/b8311a95009805a6e5593f0390f52c0fa350117f/template/module/__manifest__.py)
- [template/module/readme/CONTEXT.md](https://github.com/OCA/maintainer-tools/blob/b8311a95009805a6e5593f0390f52c0fa350117f/template/module/readme/CONTEXT.md)

### Vauxoo/mcp.odoo

Reviewed `main` at `c6c1faf6f430a6bebada09fce5d6b976149ef9a2`; repository license reported by GitHub: `MIT`.

**Retain**: Existing count_records and compact/full response controls cover the relevant use case; defer new formats and multi-profile architecture without a demonstrated gap.

Reviewed files:
- [README.md](https://github.com/Vauxoo/mcp.odoo/blob/c6c1faf6f430a6bebada09fce5d6b976149ef9a2/README.md)
- [odoo_mcp_multi/plugins/odoo-mcp/skills/odoo-mcp-tools/SKILL.md](https://github.com/Vauxoo/mcp.odoo/blob/c6c1faf6f430a6bebada09fce5d6b976149ef9a2/odoo_mcp_multi/plugins/odoo-mcp/skills/odoo-mcp-tools/SKILL.md)

### fhidalgodev/odoo-development-skill

Reviewed `main` at `11f62cad6f3c5709fb5c9f490b24861b5b4c2486`; repository license reported by GitHub: `MIT`.

**Retain**: Local project-first search and version evidence rules are preferable; do not import exhaustive searches, language preferences or unverified Odoo 20 assertions.

Reviewed files:
- [README.md](https://github.com/fhidalgodev/odoo-development-skill/blob/11f62cad6f3c5709fb5c9f490b24861b5b4c2486/README.md)
- [SKILL.md](https://github.com/fhidalgodev/odoo-development-skill/blob/11f62cad6f3c5709fb5c9f490b24861b5b4c2486/SKILL.md)

### letzdoo/claude-marketplace

Reviewed `master` at `be96e8b57268cc0f5da6142742857751c25cd860`; repository license reported by GitHub: `MIT`.

**Retain**: Keep explicit response compaction and full detail; do not install global shell rewriting or source/test output filters.

Reviewed files:
- [plugins/odoo-development/SKILL.md](https://github.com/letzdoo/claude-marketplace/blob/be96e8b57268cc0f5da6142742857751c25cd860/plugins/odoo-development/SKILL.md)
- [plugins/odoo-token-killer/SKILL.md](https://github.com/letzdoo/claude-marketplace/blob/be96e8b57268cc0f5da6142742857751c25cd860/plugins/odoo-token-killer/SKILL.md)
- [plugins/odoo-token-killer/skills/otk-core/src/filters.rs](https://github.com/letzdoo/claude-marketplace/blob/be96e8b57268cc0f5da6142742857751c25cd860/plugins/odoo-token-killer/skills/otk-core/src/filters.rs)

### unclecatvn/agent-skills

Reviewed `main` at `82ebbaed8988e9697687612575d437ca0eacec4e`; repository license reported by GitHub: `MIT`.

**Adapt**: Add loaded-file and class ownership checks to the detailed source trace; retain bounded, optional tracing.

Reviewed files:
- [README.md](https://github.com/unclecatvn/agent-skills/blob/82ebbaed8988e9697687612575d437ca0eacec4e/README.md)
- [skills/odoo-19.0/SKILL.md](https://github.com/unclecatvn/agent-skills/blob/82ebbaed8988e9697687612575d437ca0eacec4e/skills/odoo-19.0/SKILL.md)
- [skills/odoo-workflow/SKILL.md](https://github.com/unclecatvn/agent-skills/blob/82ebbaed8988e9697687612575d437ca0eacec4e/skills/odoo-workflow/SKILL.md)

## Scope of the adaptations

The UncleCat workflow distinguishes definitions found by search from definitions that actually load. The local trace already checks dependency graphs, inheritance, and XML IDs; it benefits from explicitly checking Python imports, class ownership, manifest data, and asset bundle membership. Keep this detail in the disclosed checklist so routine edits retain their short path.

OCA documents a README generator built from readme fragments. Guide agents to update those fragments and use the existing generator in repositories configured for it. Its optional CONTEXT fragment explains the business use case and useful setup. This is a reference to a convention, not copied template text. The upstream example manifest contains an old 11.0 version and asset conventions, so it is not a version-neutral scaffold.

The universal development skill is useful as an index, but its current Odoo 20 assertions require official source verification. Its broad mandatory search policy conflicts with this project's routine-task approach. The local pattern index and version-specific guidance remain the preferred route.

Vauxoo now documents multiple output formats, pagination, concurrent calls, and multi-profile operation. Those are coherent in its server, but introducing their protocol would expand this project's API without evidence of need. The local count-only operation and explicit full-response escape hatch remain adequate.

Letzdoo's token-saving percentages are upstream claims, not measurements for Odoo Boost. Keep the existing response compaction and preserve complete diagnostics; no global command interception or signature-only source filtering is adopted.

## Future updates

Use the consolidated upstream provenance file for the next comparison baseline. Compare each reviewed path between its recorded SHA and the new candidate SHA, inspect license changes, and record adopt/retain/defer decisions. A reviewed SHA must not be presented as a fully vendored version. Preserve local adaptations and rerun focused guidance/tool tests after changes.

## Workspace skills

Compared all 38 installed skills against [mattpocock/skills at 4ae2317](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d).
The per-skill decisions and current file hashes are in
[upstream-sources.json](../upstream-sources.json). These skills live in
`../.agents/skills`, outside this Git repository; preserve that directory with
its workspace lockfile when moving the workspace. The installer lockfile's
hashes identify the original installation, not these selective adaptations.
The original installed upstream commit was not recorded and cannot be inferred
reliably from those hashes.

Adopted focused improvements:

- `ask-matt`: read the actual skill before making routing claims.
- `claude-handoff`: pass a saved summary as a quoted argument instead of
  interpolating prose as shell code. `handoff`: clarify temporary paths.
- `code-review`: explicitly find and include all standards documents.
- `diagnosing-bugs`: verify a deliberate mutation before trusting a red test.
- `implement`: fetch and identify a supplied ticket before coding.
- `tdd`: explain the coverage and limits of each proposed test seam.
- `teach`: clarify workspace-relative paths and vary correct-answer positions.
- `pr`: repair the component-tree example and its attribution.
- `wizard`: preserve quoted values on reruns, fail cleanly at EOF, create new
  environment files with restricted permissions, and parse the stage function
  before prompting. Only the template was updated; no wizard was executed.

Retained the existing `CONTEXT.md` convention across the skill family rather
than partially adopting the upstream `GLOSSARY.md` rename. Kept current
orchestration and tracker procedures: new parallel integration workflows,
mandatory setup, and remote branch publication are not needed for this update.
`resolving-merge-conflicts` is absent at the reviewed upstream revision; retain
its local files rather than treating upstream removal as a deletion request.
Unchanged skills were retained. The upstream MIT notice is preserved in
[upstream-Matt-Pocock-LICENSE.txt](upstream-Matt-Pocock-LICENSE.txt).

The PR visual menu was also compared with
[humanlayer/skills at 4d69d20](https://github.com/humanlayer/skills/blob/4d69d20f6e9b57b4fcf0d501ccfb1be961f0f329/plugins/show-me/skills/show-me/SKILL.md).
Its existing smallest-useful-visual guidance remains sufficient.

For `setup-ts-deep-modules`, the selected
[dependency-cruiser package metadata](https://github.com/sverweij/dependency-cruiser/blob/5173200de662c89c6ed0fd687e9a62aedaf792a0/package.json)
requires modern Node releases. Added a Node/engine compatibility check and
recognition of `bun.lock`; installation still resolves and locks the compatible
tool in the target TypeScript project. This Python repository needs no new
Node dependency.

## Official sources and snapshots

Refreshed the complete text-only 18.0, 19.0, and 20.0 documentation packs from
their matching official branches, preserving deterministic archive timestamps,
licenses and source commits. Exact revisions and archive SHA-256 values are in
the provenance file and each archive's manifest. Reviewed official coding
transaction guidance and clarified cursor ownership in the bundled OCA rules;
cron progress remains tied to the target series' documented scheduler API.

[Odoo LS 1.6.1](https://github.com/odoo/odoo-ls/releases/tag/1.6.1) is the reviewed
stable release. The existing installer already selects stable releases or an
explicit version and records the installed tag, so no installer change or
binary installation is needed. Official Odoo core branch metadata was checked,
but core implementations were not audited. Enterprise returned 404 to the
public request and remains explicitly unreviewed; version-specific APIs must
still be checked against the target project's accessible source.

## Repeatable maintenance

Start with `upstream-sources.json`. Fetch a candidate revision without executing
upstream scripts. Compare only the relevant paths against the recorded reviewed
revision, including supporting files and licenses. Compare those findings with
the current local files and hashes; retain useful local differences. A missing
upstream path warrants a recorded decision, not an automatic deletion. Record
new reviewed SHAs, selected adaptations, unchanged decisions, and current local
hashes together. Keep installer-owned lockfile fields separate from this review
record.

For documentation snapshots, check out the matching series, use
`tools/build_docs_pack.py`, validate the resulting manifests and corpus, then
refresh the archive hashes. Runtime documentation caches and language-server
installations have their own revision/tag metadata and are updated explicitly
by their existing commands.

## Validation

85 focused tests passed across guidelines, skill loading, offline docs, Odoo LS,
and packaging. All three archives passed ZIP integrity checks; embedded page
counts and revisions match the provenance record. All workspace skill hashes
match the recorded local files. Bash syntax and isolated wizard helper checks
passed for quoted values, replacement on rerun, new-file mode 0600, and EOF.
No Odoo runtime, client workflow benchmark, or live database was exercised.
The optional docs package is now 0.1.1 to identify the refreshed snapshots.
