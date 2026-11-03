# Version audit: controllers, frontend, module lifecycle and views

Audit date: 2026-11-03. Scope: the extracted rules in four core guidelines and
`controllers_routes`, `owl_components`, and `xml_views`. This is documentation
and selected source verification across five requested series, not runtime
certification, a complete Odoo API inventory, or a full book reading.

## Pinned documentation evidence

Local roots are `references/odoo-official-docs/<series>/<revision>/content/`:

| Series | Official documentation revision |
|---|---|
| 15.0 | `f6b84ed59624ba8f0db2b1d0f7097e435550bb7e` |
| 17.0 | `fbf3e3a6ef0bda7c30b28f213848deca17c2a872` |
| 18.0 | `ca129a822019682bd32552e4cbabba2520d1308e` |
| 19.0 | `de94dcddba224a1ece042792fa444e7ba0c31fdf` |
| 20.0 | `3efea922210a1451b0e48c58a33706b04c4786c1` |

Evidence keys resolve relative to each pinned root:

- **M**: `developer/reference/backend/module.rst` (manifest fields and hooks).
- **D**: `developer/reference/backend/data.rst` (sequential operations and noupdate).
- **H**: `developer/reference/backend/http.rst` (controller extension).
- **J**: `developer/reference/frontend/javascript_modules.rst` (transformation).
- **O**: `developer/reference/frontend/owl_components.rst` (component/template).
- **S**: `developer/reference/frontend/services.rst` (RPC and useService).
- **A**: `developer/reference/frontend/assets.rst` (bundles and ordering).
- **V**: `developer/reference/backend/views.rst` for 15;
  `developer/reference/user_interface/view_architectures.rst` for 17/18/19/20.

Status **V** means verified in that version's official documentation or selected
source; **Q** means qualified by an explicit version/context restriction; **U**
means unresolved and not promoted as a universal package fact. No cell implies
that behavior was executed in Odoo.

## Five-version claim matrix

| Claim / evidence | 15 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|
| Overridden routes need redecorating (**H**) | V | V | V | V | V |
| Manifest reference marks name required; other cited fields optional (**M**) | V | V | V | V | V |
| Data definitions follow dependency order; noupdate affects updates (**D**) | V | V | V | V | V |
| Hook signature: pre / post / uninstall (**M**) | V: cr / cr+registry / cr+registry | V: env each | V: env each | V: env each | V: env each |
| Native JS transformation (**J**) | V: first-line pragma opt-in | V: first-line pragma opt-in | V: automatic standard paths | V: automatic standard paths | V: automatic standard paths |
| RPC controller API shown in services (**S**) | V: RPC service | V: RPC service | V: imported rpc helper | V: imported rpc helper | V: imported rpc helper |
| Asset dictionary / bundle dependency ordering (**A**) | V | V | V | V | V |
| Owl component example imports (**O** + source) | Q: global owl API | Q: docs contain stale global API example; source confirms modern hooks | V: @odoo/owl examples | V: @odoo/owl examples | V: @odoo/owl examples |
| Owl template discriminator (**O**) | V: owl="1" explicitly required | V: modern example omits discriminator | V: modern example | V: modern example | V: modern example |
| List root and action name (**V**) | V: tree | V: tree | V: list | V: list | V: list |
| Dynamic view modifiers (**V**, 17 source) | V: attrs/states patterns | V: inline; source rejects attrs/states | V: inline examples | V: inline examples | V: inline examples |
| Canonical JSON-RPC route type (source) | V: json | V: json | V: json | V: jsonrpc; json deprecated alias | V: jsonrpc; json deprecated alias |
| Auth none may run without DB (**H** / source) | V | V | V | V | V |
| Built-in bearer in inspected route API (source) | Q: not listed; do not copy newer auth | Q: not listed; do not copy newer auth | V: documented | V: documented | V: bearer_scope required |
| HTTP vs JSON-RPC CSRF behavior (source) | Q: HTTP dispatcher enforces unsafe-method CSRF | V: defaults differ | V: defaults differ | V: defaults differ | V: defaults differ |
| Additional json2 dispatcher (source) | U: not investigated | U: not investigated | U: not investigated | U: not investigated | V: registered separately |

“Automatic standard paths” means `static/src` and `static/tests`; code outside
those paths still needs its documented transformation convention. An absent
feature from an old API list is not proof that every installed customization
rejects it. The package instructs users to inspect the target instead of claiming
absolute absence.

## Official source checks beyond local RST

Local RST contains autodoc directives rather than the complete generated route
API. The following official branch source was consulted on the audit date.
These links were fetched by branch, not pinned to Git commit; they are a separate
confidence category from the documentation snapshots above.

- [15 HTTP](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/odoo/http.py):
  route docstring and HttpRequest dispatch.
- [17 HTTP](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/http.py):
  route type/auth/CSRF docstrings.
- [18 HTTP](https://github.com/odoo/odoo/blob/55f9d29cd13c935226c2b6e48eb661bc89310e8b/odoo/http.py):
  bearer and route API.
- [19 HTTP](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/http.py):
  deprecated JSON alias and dispatcher contract.
- [20 routing](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/odoo/http/routing_map.py)
  and [dispatchers](https://github.com/odoo/odoo/blob/006f5cc915ebb0f30c6f8602c1b42e6d7ff1e754/odoo/http/dispatcher.py):
  relocated modules, bearer_scope, deprecated alias, and json2 registration.
- [15 bundled Owl](https://github.com/odoo/odoo/blob/3a28e5b0adbb36bdb1155a6854cdfbe4e7f9b187/addons/web/static/lib/owl/owl.js):
  `__info__.version` is 1.4.11 and global exports include hooks/tags.
- [17 hooks](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/addons/web/static/src/core/utils/hooks.js)
  and [bundled Owl](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/addons/web/static/lib/owl/owl.js):
  modern import/export API; bundled version 2.8.4 in source inspected. The 17
  component RST still has an older `owl.hooks` snippet; source takes precedence.
- [17 view validation](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/addons/base/models/ir_ui_view.py):
  `_check_xml` explicitly rejects attrs/states.

## Package corrections

- JS core now marks the example as modern 17+ and separates 15 global Owl usage.
  It records pragma and RPC boundaries across all five versions. Automatic
  transformation starts with the audited 18 documentation, rather than 19 only.
- The Owl skill now gates 15 template/import behavior and distinguishes 15/17
  native-module opt-in from the 18+ standard-path convention.
- Core and skill controller guidance now records canonical route spelling,
  alias status, bearer support scope, and 20 bearer_scope/json2 differences.
- Manifest guidance records the older cursor/registry hook contract separately
  from the env contract. Dependency ordering and licensing rules remain shared.
- Core view guidance has explicit tree/list and modifier boundaries. XML view
  creation examples are labeled 18/19/20 and use matching modern chatter markup;
  existing-view edits still inspect the actual parent architecture.
- The core HTML example's unbounded search was bounded to match its own guidance.

## Limits and remaining verification

Search-view RNG attribute removal, all controller response/binary helpers, every
Owl hook, payment/website-specific registries, edition-specific views and every
backend/frontend override were not independently enumerated here. Existing rules
requiring the actual target schema/source remain necessary. Source API checks
should be pinned to the deployment commit before migration work where a moving
branch would be insufficient evidence. No master-only claim was used as 20 proof.

Validation: focused guideline/skill tests and `git diff --check` are run after the
edits. These checks concern composition and installation of guidance, not live
route, browser, module-install or view-validation behavior.


## Reproducible source follow-up

Selected implementation files were subsequently downloaded at fixed commits; see
[central audit](version-audit.md) for the source revision table and local manifest.
Links above now use those commits. Only files listed in that manifest were
archived; a branch observation is not proof that unarchived files were compared.
