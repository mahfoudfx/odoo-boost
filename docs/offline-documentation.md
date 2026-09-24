# Offline Odoo documentation

Odoo Boost can search a local, version-matched copy of the official
[Odoo documentation](https://github.com/odoo/documentation) without a web-search
call. The corpus covers application/user, administration, and developer `.rst`
pages. Searches return at most three short excerpts with local file/line and
online page links. Images and built HTML are excluded from the text packs.

## Choose a source

During `odoo-boost install`, choose one of these options for the detected Odoo
series (or the explicit `--target-odoo-version`):

| Choice | Effect |
|---|---|
| `online` (default) | Keep curated web links; install no local documentation. |
| `cached` | Reuse the matching revision already in the shared cache. Shown when available. |
| `packed` | Expand the matching snapshot from the optional `odoo-boost-docs` package. Shown when available. |
| `path` | Copy and index an existing, matching `odoo/documentation` checkout. |
| `download` | Fetch only `.rst` pages and `LICENSE` from the matching official Git branch, then index them. Requires Git and network access. |

The optional [pack package](../packages/odoo-boost-docs/README.md) currently
contains pinned 18.0, 19.0, and 20.0 snapshots. From this repository, install
it in the project VENV with `python -m pip install ./packages/odoo-boost-docs`.
The optional wheel is also attached to each Odoo Boost GitHub Release; download
it and install it in the same VENV as the core package. It is not published to
PyPI by the core release job. Its wheel is separate from the core Odoo Boost
wheel. Each pack includes
license and upstream revision metadata; the documentation is
[CC BY-SA 4.0](https://github.com/odoo/documentation/blob/19.0/LICENSE).
The snapshot is text-only and does not reproduce the complete website.

For a noninteractive installation, pass `--skip-docs` and install a version
later:

```bash
odoo-boost docs install --version 19.0 --source packed
odoo-boost docs install --version 19.0 --source download
odoo-boost docs install --version 19.0 --source checkout --path /srv/odoo/documentation
odoo-boost docs status --version 19.0
odoo-boost docs search "computed fields" --version 19.0 --section developer
```

`--source archive --path /path/to/19.0.zip` accepts a supplied pack. An
explicit `docs install` updates `odoo_docs_path` in a discovered project config
when the target version matches `odoo_version`. The installer does the same for
its chosen source. Downloads occur only after choosing `download` or running
the explicit command; neither normal project startup nor searches use the
network.

## Cache and lookup

The shared cache is `~/.cache/odoo-boost/docs` on Linux or under
`XDG_CACHE_HOME` when set. It stores one directory per series and revision, so
several projects can reuse it. `odoo_docs_path` records the selected directory
in the project config. Re-run `docs install --source download` when you want a
new upstream revision; existing cached revisions remain available. A packaged
snapshot changes only when the optional pack package is updated.

Use `search_docs(query="...", section="developer")` to search locally. Sections
are `developer`, `administration`, `applications`, or `all`; the default is
`all`. Omitting `query` retains the existing curated-link lookup. A configured
version must match the installed documentation series. The search tool reads
only the configured documentation cache; `allowed_roots` still controls the
other local MCP file tools.
