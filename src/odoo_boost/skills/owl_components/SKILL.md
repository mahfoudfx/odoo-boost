---
name: owl-components
description: Edit an existing Odoo Owl component, template, registry entry, or asset; create a new component when requested.
globs: ["static/src/**/*.js", "static/src/**/*.xml", "static/src/**/*.scss", "__manifest__.py"]
---

# Owl components and existing frontend edits

## Edit an existing component

Locate the component, matching template, asset entry, and affected test. For a
copy, class, or layout change, edit the relevant node or rule and run the
project's focused frontend check. For changed behavior, follow the handler,
service, or registry entry involved and test that path. Check the configured
Odoo version when an API or asset convention changes. Finish after the focused
check and diff; use the creation steps below for a new component.

## Create a component

Load the configured version notes and inspect the component being extended before
copying imports, hooks, services, or registry APIs. The example shows a common modern
pattern, not a compatibility contract for every supported Odoo version.

Organize frontend files by feature. Prefer registries, services, hooks, composition,
and documented extension points over patching framework code. When patching is the
only viable option, keep it narrow and test it with other installed patches. Scope CSS
classes to the addon (`o_<module>_...`), avoid ID selectors, and never pass untrusted
strings to `markup()`, `innerHTML`, or `insertAdjacentHTML`.

## Steps

### 1. Create JavaScript Component (`static/src/js/my_component.js`)
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        title: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            records: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            this.state.records = await this.orm.searchRead(
                "res.partner",
                [["is_company", "=", true]],
                ["name", "email"],
                { limit: 10 }
            );
        } finally {
            this.state.loading = false;
        }
    }

    onRecordClick(record) {
        this.notification.add(`Clicked: ${record.name}`, { type: "info" });
    }
}
```

### 2. Create QWeb Template (`static/src/xml/my_component.xml`)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component p-3">
            <h3 t-if="props.title" t-esc="props.title"/>
            <div t-if="state.loading" class="text-muted">Loading...</div>
            <div t-else="">
                <div t-foreach="state.records" t-as="record" t-key="record.id"
                     class="my-component-record p-2 border-bottom"
                     t-on-click="() => this.onRecordClick(record)">
                    <strong t-esc="record.name"/>
                    <span t-if="record.email" class="ms-2 text-muted" t-esc="record.email"/>
                </div>
            </div>
        </div>
    </t>
</templates>
```

### 3. Add Styles (Optional) (`static/src/scss/my_component.scss`)
```scss
.my-component {
    .my-component-record {
        cursor: pointer;

        &:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
    }
}
```

### 4. Register in Asset Bundle (`__manifest__.py`)
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_component.js',
        'my_module/static/src/xml/my_component.xml',
        'my_module/static/src/scss/my_component.scss',
    ],
},
```

### 5. Register as Client Action (Optional)
```javascript
// At the end of my_component.js
registry.category("actions").add("my_module.my_action", MyComponent);
```
```xml
<record id="my_component_action" model="ir.actions.client">
    <field name="name">My Component</field>
    <field name="tag">my_module.my_action</field>
</record>
```

## Checklist
- [ ] `@odoo-module` pragma at the top of JS file
- [ ] `static template` matches the QWeb template name
- [ ] `static props` defined for type validation
- [ ] Services used via `useService()` in `setup()`
- [ ] Template uses `t-key` on `t-foreach` loops
- [ ] Assets declared in `__manifest__.py`
- [ ] Component registered in appropriate registry (if needed)
