## Views and UI

### Audited Version Boundaries

| View convention | 15 | 17 | 18 / 19 / 20 |
|---|---|---|---|
| List root and action mode | `tree` | `tree` | `list` |
| Dynamic modifiers | `attrs` / `states` patterns | Inline Python expressions | Inline Python expressions |

Use the same list-view naming in nested views and actions. Include fields used
by modifier expressions in the architecture. Exact search-view attributes and
chatter markup still require the target version's schema/parent view.

### View Types
- **Form**: detail view for a single record. Uses `<form>` root element.
- **List**: tabular view. Use the root element and dynamic-attribute syntax selected by
  the configured Odoo version notes.
- **Kanban**: card-based view. Uses `<kanban>` with QWeb templates inside.
- **Search**: defines search filters and group-by options. Uses `<search>`.
- **Pivot / Graph / Calendar / Gantt**: analytical and planning views.

### View Inheritance
- Use `<record model="ir.ui.view">` with `inherit_id` to extend existing views.
- XPath expressions: `<xpath expr="//field[@name='partner_id']" position="after">`.
- Positions: `before`, `after`, `inside`, `replace`, `attributes`.
- Use `position="attributes"` to modify attributes without replacing the element.
- Always use specific XPath expressions — avoid fragile `//div[1]` selectors.

### Form View Best Practices
- Use `<sheet>` inside `<form>` for the main content area.
- Use `<group>` to organize fields into columns — `<group>` creates a 2-column layout.
- Use `<notebook>` + `<page>` for tabbed sections.
- Use the target version's chatter element and model mixins; inspect the inherited
  view rather than copying legacy chatter markup into a newer series.
- Use `widget` attribute for special rendering (e.g. `widget="many2many_tags"`).
- Select modifier syntax from version notes: modern series use inline expressions;
  older series may require `attrs` for dynamic conditions. Include fields referenced
  by expressions in the view, even if invisible.

### Actions and Menus
- Window actions (`ir.actions.act_window`) open views for a model.
- Set `view_mode` with the configured version's list-view name (`list` or `tree`)
  and keep it consistent with the view architecture.
- Use `domain` on actions to pre-filter records.
- Use `context` to set defaults: `{'default_type': 'out_invoice'}`.
- Menus (`ir.ui.menu`) link to actions and define the navigation hierarchy.

### Naming Conventions
- View XML IDs: `<module>.<model_underscored>_view_<type>` (e.g. `sale.sale_order_view_form`).
- Action XML IDs: `<module>.<model_underscored>_action` (e.g. `sale.sale_order_action`).
- Menu XML IDs: `<module>.<model_underscored>_menu` or descriptive names.


### Verification
Inspect the resolved inherited architecture, not only the extension XML. Check
XPath targets, action/menu references, modifiers and fields under intended user
groups. A hidden button or readonly widget is a UI affordance, not a server-side
permission check. Validate in the target version; static parsing alone does not
prove the rendered view works.

See [Odoo 18 view architecture](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/user_interface/view_architectures.rst)
and the [older view API](https://github.com/odoo/documentation/blob/16.0/content/developer/reference/backend/views.rst)
when maintaining older addons.
