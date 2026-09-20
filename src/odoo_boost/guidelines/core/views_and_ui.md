## Views and UI

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
- Add `<div class="oe_chatter">` with `mail.thread` fields for chatter integration.
- Use `widget` attribute for special rendering (e.g. `widget="many2many_tags"`).
- Use `invisible`, `readonly`, `required` attributes with expressions for dynamic UI.

### Actions and Menus
- Window actions (`ir.actions.act_window`) open views for a model.
- Set `view_mode` to define available views: `"list,form"`, `"kanban,list,form"`.
- Use `domain` on actions to pre-filter records.
- Use `context` to set defaults: `{'default_type': 'out_invoice'}`.
- Menus (`ir.ui.menu`) link to actions and define the navigation hierarchy.

### Naming Conventions
- View XML IDs: `<module>.<model_underscored>_view_<type>` (e.g. `sale.sale_order_view_form`).
- Action XML IDs: `<module>.<model_underscored>_action` (e.g. `sale.sale_order_action`).
- Menu XML IDs: `<module>.<model_underscored>_menu` or descriptive names.
