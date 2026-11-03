## JavaScript and OWL

### OWL Framework
- Odoo uses **OWL** (Odoo Web Library) as its frontend component framework (v14+).
- OWL is a modern reactive framework similar to Vue/React with XML templates.
- Components extend the target series' Owl Component. The example below uses
  the modern `@odoo/owl` API (17+); Odoo 15 documents the global `owl` API.
- Templates use QWeb syntax with `t-` directives.

### Version Selection

| Convention | 15 | 17 | 18 / 19 / 20 |
|---|---|---|---|
| Native JS transformation | First-line `@odoo-module` opt-in | First-line `@odoo-module` opt-in | Automatic under `static/src` and `static/tests`; check exceptions outside them |
| Controller RPC | `useService("rpc")` | `useService("rpc")` | Import `rpc` from `@web/core/network/rpc` |
| Owl template discriminator | Add `owl="1"` | Modern Owl template | Modern Owl template |

The 17 component documentation still contains legacy Owl snippets; verify imports
against its official source rather than mixing `owl.hooks` with Owl 2 APIs.

### Component Structure (modern API, 17+)
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    static props = {
        recordId: { type: Number, optional: true },
    };

    setup() {
        this.state = useState({ count: 0 });
    }

    increment() {
        this.state.count++;
    }
}
```

### Template (QWeb XML)
- Place in `static/src/xml/my_component.xml`.
- Register via assets in `__manifest__.py`.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component">
            <span t-esc="state.count"/>
            <button t-on-click="increment">+1</button>
        </div>
    </t>
</templates>
```

### Key Concepts
- **Hooks**: `useState`, `useRef`, `useEffect`, `useService`, `useEnv` — similar to React hooks.
- **Services**: Use `useService("orm")` for model calls and `useService("notification")`
  for notifications. For controller calls, inspect the version: modern APIs import
  `rpc` from `@web/core/network/rpc`; older series may expose an RPC service.
- **Registry**: `registry.category("actions")`, `registry.category("fields")`, `registry.category("services")`.
- **Props validation**: Define `static props` for type checking in dev mode.
- **Lifecycle (17+)**: Register hooks such as `onWillStart`, `onMounted`, and
  `onWillUnmount` in `setup()`; import them from `@odoo/owl`. For Odoo 15, inspect
  the existing component's global Owl API and lifecycle before porting this code.
  Use `setup()` for initialization so component extensions remain possible.

### Assets Declaration
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/**/*',
        'my_module/static/src/xml/**/*',
        'my_module/static/src/scss/**/*',
    ],
},
```

### Best Practices
- Follow the version table for JS transformation; automatic transformation in
  standard paths is documented starting with the audited Odoo 18 branch.
- Use Odoo's built-in services (`rpc`, `orm`, `action`) instead of raw `fetch`.
- Keep components small and focused — compose from smaller components.
- Use `t-key` on `t-foreach` loops for proper reconciliation.
- Don't directly manipulate the DOM — use OWL's reactive state instead.

- Release timers and external listeners when the component is destroyed; verify
  async results cannot update a stale component.
- Select the bundle for the execution context (backend, website, POS, or tests).
  Asset ordering operations require their target to exist earlier in the bundle.
- Verify loading, empty, error, and success states in the actual target client.

### Official References
- [Components](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/frontend/owl_components.rst)
- [JavaScript modules](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/frontend/javascript_modules.rst)
- [Services](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/frontend/services.rst)
- [Assets](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/frontend/assets.rst)
