# Source learning: window actions, inherited views and field widgets

Reviewed 2026-11-03. Origin: **code examples** from both Cookbook companion
repositories, with official 17/19 documentation checks. No new book-prose reading
or Odoo/browser execution is claimed. Findings are retained research notes;
the existing XML/UI/Owl guidance already supports the main decisions and does not
need a forced rewrite.

## Scope and reading evidence

The contiguous family is `Chapter09/00_initial_module` through
`Chapter09/10_view_inheritance` inclusive in both v17 and v19. It covers menus,
action-specific views, widgets, object/action buttons, action context/domains,
lists, search/search panels and form/list/search inheritance. All **48 distinct
textual file contents** in that family were read in full, including model/import,
manifest, ACL/group and XML context. They correspond to 174 file paths; the other
126 hash-identical paths remain pending contextual completion rather than being
automatically marked read. Binary assets and chapter-level metadata outside the
recipe range remain separate inventory units.

Additionally read six files per version for the integer-color field widget:
v17 `Chapter15/01_field_widget/my_hostel/` and v19
`Chapter14/01_field_widget/my_hostel/`: manifest, JS, QWeb template, SCSS,
room view and room model. Both use Owl components, despite being in differently
numbered chapters. In total **60 exact file paths / 57 distinct contents** were
directly read. The evidence file supplies exact paths and duplicate candidates to
the integrating reviewer; the shared coverage ledger remains authoritative after
integration. Full frontend or Chapter09/12/14/15 coverage is not implied.

## Retained lessons

Paths below are relative to each cookbook's `*-Examples` root.

| Lesson | Source stimulus | Senior developer decision and official verification | Project value / disposition |
|---|---|---|---|
| SU-01 | Both versions `Chapter09/01_menus_and_actions copy/.../views/hostel_room.xml`, 06 and 09 variants plus ACLs | An action's domain selects a workspace; it does not authorize data access. The action labelled all rooms filters to draft, then a later example includes draft/available. Treat the visible menu label, action domain, search criteria and ACL/rules as distinct concerns. Official actions describe implicit search-query filtering; security defines actual model/record authorization. | Existing security/UI rules confirmed with exact examples. Test the same user through another action or direct ORM/RPC query rather than assuming a menu filter is a security boundary. |
| SU-02 | Both versions `Chapter09/05_action_context/.../views/hostel_room.xml` and room models | Separate environment language (`lang`) from default input values (`default_lang`, `default_room_rating`) and model-specific switches. v17's room model has no `lang` field; v19 adds a language selection and temporarily makes `name` translatable in recipe05, but recipe06 removes `translate=True`. Inspect actual model evolution rather than assuming context alone adds a field or translation support. | Note retained: practical context/default/translation review checklist, supported by official actions and pinned17 `default_get` implementation. The example's `active_test=False` also needs an archive-capable model before it has useful meaning. |
| SU-03 | Both versions `Chapter09/02_action_specific_views/.../views/hostel_room.xml` and manifest | Select list/form order through `ir.actions.act_window.view` and its sequence, and inspect the server's composed `views` list rather than assuming `view_id` alone controls every view. Official17/19 docs describe ordered action-view records, fallback `view_id` and unfilled modes. Keep tree/list spelling aligned with the target version. | Existing UI guidance confirmed and expanded in this note with the composition decision; prevents accidental default-view selection when several modules extend the model. |
| SU-04 | Both versions `Chapter09/10_view_inheritance/.../views/hostel_room.xml` | An inheritance XPath matches the first node in the current architecture; specs apply sequentially and extension priority affects the result. Stable named group anchors in these examples work in their inspected base, but a future sibling extension can change matches. Inspect the resolved architecture under real modules/groups, rather than interpreting the XPath as a global all-match edit. | New precise counterexample/checklist retained. Both inspected base form anchors have exactly one static match, which establishes intent only; no resolved Odoo architecture was generated. |
| SU-05 | v19 `Chapter09/08_search_view/.../views/hostel_room.xml`; both versions09 | A search-field `filter_domain` can deliberately OR display-name and room-number predicates using `self`; other fields/filters and the action domain still constrain results. Search completion domains, field filter domains and group-by context have different roles. Official19 architecture docs specify precedence over `operator` and domain combination. | Note retained: test room-name versus room-number matches, combinations with fixed draft-only action scope, and visibility under intended users. Avoid diagnosing a valid search result exclusion as a widget bug. |
| SU-06 | Both versions `Chapter09/09_search_view_panel/.../views/hostel_room.xml` | Search-panel counters and expansion are product/performance choices. These examples request multi-selection on a selection field, counters and zero-result expansion. Official17/19 docs permit selection multi-values, so that alone is not a defect; counters can add work and have a performance switch. | Existing performance principle confirmed with a UI scenario. Verify zero-result categories, combined filters and measured query cost before overriding search-panel internals. No universal query-count claim is made. |
| SU-07 | v17 `Chapter09/02_action_specific_views/.../models/hostel.py`, v19 corresponding model and object buttons | Follow the complete button-to-method path. v17's `change_state` calls `is_allowed_transition` but the model defines no such method; v19 restores it. Under the supplied addon and base-only dependency, the v17 call path lacks its helper. Even a working button path does not establish that arbitrary permitted writes enforce the same transition policy. Official security warns that public methods/parameters are caller-controlled and ACLs are checked during CRUD. | Concrete new faulty-example scenario retained. Test valid/invalid transitions and direct writes if the workflow is a business invariant. Syntax parsing alone could not find this missing behavior. No live failure trace is claimed. |
| SU-08 | The six field-widget files per version listed above | Use the actual extension family: both widgets are Owl `Component`s registered in the fields registry, not legacy widget includes. v17 uses the module pragma; v19's standard static path is automatically transpiled. Keep model field type, template, registry key and asset declaration together. The example's click path has no explicit readonly guard, so exercise readonly/edit modes and inspect target props/record API; do not turn a CSS hover rule into a permission claim. | Existing Owl/module/version guidance confirmed with concrete paired examples. Official field howtos themselves use an illustrative prop shape; inspect target implementation before prescribing one universal update callback. Browser behavior remains unverified. |

The v19 group XML additionally writes `implied_by_ids` with refs named
`base.user_root`/`base.user_admin`, whereas v17 assigns the `users` relation.
That deserves a matching-schema/comodel check. The pinned archived files available
to this pass do not establish the exact v19 group-field contract, and an attempted
official raw-source lookup failed; this suspicion stays unresolved rather than
becoming an asserted runtime defect or a package correction.

## Official evidence

Documentation revisions: 17
`fbf3e3a6ef0bda7c30b28f213848deca17c2a872`; 19
`de94dcddba224a1ece042792fa444e7ba0c31fdf`. Relevant local pinned sections supplied
verification; no successful fresh HTTP lookup is claimed.

- [17 actions](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/actions.rst) and [19 actions](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/actions.rst), Window Actions: domain/context, specific views and composition order.
- [17 view inheritance](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/user_interface/view_records.rst) and [19 view inheritance](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/user_interface/view_records.rst), resolution and inheritance specs: first match, priority and sequential application.
- [17 view architectures](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/user_interface/view_architectures.rst) and [19 view architectures](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/user_interface/view_architectures.rst), search fields/filter domains, group-by and search-panel attributes.
- [19 security](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/security.rst), ACL/rules and Unsafe Public Methods.
- [17 default_get implementation](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/models.py), requested-field defaults and `default_` context lookup.
- [17 field customization](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/howtos/javascript_field.rst) and [19 field customization](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/javascript_field.rst), registry/template/type/readonly prop contract.
- [17 module conversion](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/frontend/javascript_modules.rst) versus [19 module conversion](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/frontend/javascript_modules.rst), opt-in pragma versus default standard static paths.

## Validation and limits

Direct AST inspection confirms the missing helper in the v17 action-specific-view
model. ElementTree checks confirm one intended base form anchor in each inheritance
example. These checks exercise source structure, not Odoo model assembly or inherited
view resolution. All 60 reviewed paths and 126 duplicate mappings are recorded
for integration; duplicate mapping does not certify recipe context.

No production skill/tool changed in this pass, so no package behavior tests were
needed. No browser assets, readonly interaction, view install/update or record
transition was executed. Remaining Chapter09 recipes11–22, Chapter12 specialized
views, and the rest of the frontend/controller families remain pending.
