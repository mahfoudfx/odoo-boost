# Book reference review: controllers, frontend and module lifecycle

This is a focused second extraction pass, compared with official Odoo documentation
and source on 2026-11-03. It records research findings, not an assertion that every
book chapter has been fully read or that examples were executed. Books and example
archives remain temporary sources; packaged rules must be independently written.

## Local evidence inspected

Paths below are relative to `references/odoo-books/`. Both cookbook example roots
are named after their book and contain a nested `*-Examples` directory.

- Odoo 15 Development Essentials EPUB: `OEBPS/B16119_03_Final_PD_ePub.xhtml`,
  `OEBPS/B16119_05_Final_PD_ePub.xhtml` and
  `OEBPS/B16119_13_Final_PD_ePub.xhtml`: selected manifest, data and portal sections.
- Odoo 17 cookbook EPUB: `OEBPS/B20997_13.xhtml`: selected controller recipes.
- Odoo 19 cookbook EPUB: `OEBPS/Text/Chapter_3.xhtml` and
  `OEBPS/Text/Chapter_13.xhtml`: selected manifest and controller sections.
- In both v17 and v19 example roots:
  `Chapter13/02_paths_auth/my_hostel/controllers/main.py` and
  `Chapter13/04_path_override/website_ext/controllers/main.py`.
- In the v17 examples: `Chapter03/03_new_addon_file_structure/my_hostel/__manifest__.py`
  and `Chapter03/06_access_rights/my_hostel/__manifest__.py`.
- In the v19 examples:
  `Chapter22/01_initial_module/my_hostel/static/src/js/hostel.js`,
  `Chapter22/04_dynamic_snippets/my_hostel/static/src/js/snippets.js` and
  `Chapter22/04_dynamic_snippets/my_hostel/static/src/builder/snippet_option.js`.

This sample does not cover the complete frontend, website builder, payment,
installation-hook or migration corpus. No Odoo runtime was started.

## Controller corrections

The existing controller extension guide should say to redecorate overridden
endpoints with `@http.route()` to retain publication. Empty decorator arguments
inherit previous route configuration; explicit options replace corresponding
values. The book override example demonstrates this correctly. Official evidence:
[Odoo 18 controller documentation](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/http.rst).

The authentication examples are unsafe production templates: their none/public
routes run unrestricted student searches with `sudo()` and interpolate record
names into HTML. Preserve the lesson about authentication modes, but use bounded
queries under the intended user's permissions and escaped QWeb output. Treat
public authentication separately from permission to disclose records. A none-auth
route can run without a database, so it cannot assume `request.env` is usable.
Official evidence: [Odoo 19 HTTP source](https://github.com/odoo/odoo/blob/19.0/odoo/http.py)
and [Odoo security documentation](https://www.odoo.com/documentation/18.0/developer/reference/backend/security.html).

For cookie-authenticated state changes use suitable unsafe HTTP methods and retain
CSRF protection on HTTP routes. Disabling CSRF for a third-party callback requires
an alternative authentication design; POST alone is not authentication. JSON-RPC
and HTTP have distinct dispatch behavior. The v19 book uses `jsonrpc`, whereas the
v17 book uses `json`; keep the difference behind version guidance. Source evidence:
[Odoo 19 route/dispatch implementation](https://github.com/odoo/odoo/blob/19.0/odoo/http.py).

## Frontend corrections

The core OWL guide currently presents lifecycle names as methods. For OWL 2,
register lifecycle callbacks such as `onWillStart`, `onMounted`, `onWillUnmount`
and `onWillDestroy` in `setup()`. Distinguish these component hooks from website
Interaction lifecycle methods: the sampled v19 snippet uses `willStart()` on an
Interaction, not an OWL Component. Evidence:
[official Owl component lifecycle](https://github.com/odoo/owl/blob/master/doc/v2/reference/component.md).

Replace blanket `useService("rpc")` advice with target-version service/network
API selection. The Odoo 18 services documentation itself demonstrates an import
from `@web/core/network/rpc`; ORM model calls use the ORM service. Components use
`useService` for registered services, with lifecycle-aware asynchronous handling.
Evidence: [Odoo 18 services documentation](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/frontend/services.rst).

A mandatory `@odoo-module` pragma for every JS file is obsolete for v19 files under
`static/src` and `static/tests`, where conversion is automatic. Outside those
locations the pragma opts in; legacy branches need their own rule. Evidence:
[Odoo 19 JavaScript module documentation](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/frontend/javascript_modules.rst).

Asset operations depend on prior declaration of their targets and module loading
order. An addon replacing another addon's asset must depend on its owner. Verify
the correct bundle for backend, website or POS rather than copying backend paths
for all applications. Evidence:
[Odoo 18 asset documentation](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/frontend/assets.rst).

## Manifest, data and view corrections

The module-structure guide currently calls name/version/depends/data required.
Official manifest documentation marks `name` required; the others describe
metadata and declared dependencies/files. Explicit dependency declarations are
still necessary for referenced models and external IDs. The guide's LGPL-only
license recommendation should become a compatible-license decision: the official
list includes AGPL and other licenses, and the inspected book manifests use AGPL.
OCA-style version numbering is a project convention rather than the sole valid
manifest version format. Evidence:
[Odoo 18 manifest documentation](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/module.rst).

Replace a fixed security/views/data load sequence with dependency order: files
and operations are processed sequentially and references must already exist.
Retain stable external IDs across updates. Explain that `noupdate` changes upgrade
behavior and test installation separately from updates. Evidence:
[Odoo 18 data documentation](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/data.rst).

The shared views guide should defer list/tree roots, view modes, dynamic modifier
syntax and chatter markup to the configured version instead of giving modern
examples as universal syntax. UI readonly/invisibility is not server-side access
control. Verify inherited views against the actual installed parent and groups;
book screenshots alone cannot establish XPath validity in a customized database.
These are recommended validation steps, not claims that all relevant view chapters
have already been reviewed.

## Implementation targets and completion evidence

Target the four existing packaged core guides: `controllers.md`,
`javascript_owl.md`, `module_structure.md`, and `views_and_ui.md`. Keep concise
rules there and version-specific syntax in the existing version notes. Do not
add a runtime dependency on these local evidence paths. Actual changes and tests
must be recorded by the implementing reviewer; this research document is source
support rather than test evidence.

## Pass 2 before/after reported by implementing reviewer

| Area | Before | After |
| --- | --- | --- |
| Controllers | Ambiguous route override advice and generic authentication descriptions | Route re-publication, database availability, escaped output and callback trust boundaries |
| OWL and assets | Component lifecycle shown as legacy method names; universal RPC-service/pragma advice | OWL lifecycle hooks and version-selected network/module APIs |
| Module metadata | Several optional manifest fields called universally required; LGPL-only recommendation | Accurate required metadata, dependency declarations and compatible license choice |
| Module data | Fixed security/views/data order | External-ID dependency order and install/update distinction |
| Views | Modern markup mixed into shared guidance | Active-version syntax selection and server-side security distinction |

The implementing reviewer reports changes to these four core guides and the OWL
skill checklist, 50 guideline/skill tests passed, and `git diff --check` passed.
These checks validate composition and installation paths; they do not execute the
book addons or prove application behavior on a live Odoo instance.

Remaining extraction includes accounting, stock, multi-company and other business
workflow invariants, plus deeper coverage of migrations, website builders and
payment callbacks. Keep the temporary references until their desired coverage is
complete. This pass is useful packaged guidance extraction, not completion of the
entire library review.
