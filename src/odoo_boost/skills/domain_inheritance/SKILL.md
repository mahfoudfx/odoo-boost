---
name: Model & View Inheritance Mechanisms
description: Detailed guide to Odoo classical inheritance, prototype inheritance, delegation inheritance, and XPath view extensions.
globs: ["models/**/*.py", "views/**/*.xml"]
---

# Odoo Inheritance Mechanisms

Odoo provides three distinct inheritance mechanisms for Python models and XPath extension for views.

## 1. Classical Inheritance (Extension)
Used to add fields or modify methods of an existing model without creating a new database table:

```python
class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_reference = fields.Char(string="Custom Reference")

    def action_confirm(self):
        res = super().action_confirm()
        # Custom logic after standard confirmation
        return res
```

## 2. Prototype Inheritance (Copy / Polymorphic)
Used to create a new model by copying the fields and methods of an existing model into a new database table:

```python
class CustomSaleOrder(models.Model):
    _name = "custom.sale.order"
    _inherit = "sale.order"
    _description = "Independent Custom Sale Order"
```

## 3. Delegation Inheritance (`_inherits`)
Used to embed one model directly into another via a `Many2one` pointer, transparently exposing the parent model's fields:

```python
class ProductTemplate(models.Model):
    _name = "product.template"
    # ...


class ProductProduct(models.Model):
    _name = "product.product"
    _inherits = {"product.template": "product_tmpl_id"}

    product_tmpl_id = fields.Many2one("product.template", required=True, ondelete="cascade")
```

## 4. View Inheritance with XPath
Extend existing XML views cleanly using `inherit_id` and XPath expressions:

```xml
<record id="view_order_form_inherit_custom" model="ir.ui.view">
    <field name="name">sale.order.form.custom</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <!-- Position after payment_term_id -->
        <xpath expr="//field[@name='payment_term_id']" position="after">
            <field name="custom_reference"/>
        </xpath>

        <!-- Modify existing attribute -->
        <xpath expr="//field[@name='partner_id']" position="attributes">
            <attribute name="domain">[('customer_rank', '>', 0)]</attribute>
        </xpath>
    </field>
</record>
```
*XPath positions: `inside`, `after`, `before`, `replace`, `attributes`.*
