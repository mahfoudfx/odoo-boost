---
name: controllers-routes
description: Edit or create an Odoo HTTP controller, route, API endpoint, or webhook, including authentication and response behavior.
globs: ["controllers/**/*.py", "__manifest__.py"]
---

# Controllers and routes

## Edit an existing route

Find the exact decorator, handler, callers, and access boundary. Keep a text or
template-only change local and run a focused check. For route, payload, or
permission changes, verify the configured Odoo version and test allowed and
denied requests, including record rules and webhook authentication where
relevant. Review the diff once the affected behavior passes. Use the creation
steps below when adding a route.

## Create a route

Load the configured version notes before copying route decorators; route types and
response handling are version-sensitive.

### 1. Create Controller File (`controllers/main.py`)
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):
    # --- Website Page (HTML) ---
    @http.route("/my/page", type="http", auth="user", website=True)
    def my_page(self, page=1, **kwargs):
        records = request.env["my.model"].search([], limit=20, offset=(page - 1) * 20)
        return request.render(
            "my_module.my_page_template",
            {
                "records": records,
                "page": page,
            },
        )

    # --- JSON API Endpoint ---
    @http.route("/api/my-model", type="json", auth="user", methods=["POST"])
    def api_list(self, domain=None, limit=20, **kwargs):
        records = request.env["my.model"].search_read(domain or [], limit=limit)
        return {"status": "ok", "data": records}

    # --- Public Page (no login required) ---
    @http.route("/public/info", type="http", auth="public", website=True)
    def public_info(self, **kwargs):
        return request.render("my_module.public_info_template", {})

    # --- File Download ---
    @http.route("/my/download/<int:record_id>", type="http", auth="user")
    def download_file(self, record_id, **kwargs):
        record = request.env["my.model"].browse(record_id)
        if not record.exists():
            return request.not_found()
        return request.make_response(
            record.file_content,
            headers=[
                ("Content-Type", "application/octet-stream"),
                ("Content-Disposition", f"attachment; filename={record.filename}"),
            ],
        )

    # --- Webhook (external POST, no CSRF) ---
    @http.route("/webhook/my-event", type="json", auth="none", methods=["POST"], csrf=False)
    def webhook(self, **kwargs):
        data = request.get_json_data()
        # Verify the provider signature before processing `data`.
        return {"received": True}
```

### 2. Register Controller (`controllers/__init__.py`)
```python
from . import main
```

### 3. Import in Module Root (`__init__.py`)
```python
from . import controllers
from . import models
```

### 4. Create QWeb Template (for HTML routes)
```xml
<odoo>
    <template id="my_page_template" name="My Page">
        <t t-call="website.layout">
            <div class="container mt-4">
                <h1>My Records</h1>
                <t t-foreach="records" t-as="record">
                    <div class="card mb-2 p-3">
                        <h5 t-field="record.name"/>
                    </div>
                </t>
            </div>
        </t>
    </template>
</odoo>
```

## Route Parameters Reference
| Parameter | Values | Description |
|-----------|--------|-------------|
| `type` | `'http'`, `'json'` | HTTP returns HTML, JSON returns JSON-RPC |
| `auth` | `'user'`, `'public'`, `'none'` | Authentication level |
| `methods` | `['GET']`, `['POST']`, etc. | Allowed HTTP methods |
| `website` | `True`/`False` | Integrate with website module |
| `csrf` | `True`/`False` | CSRF protection (default True) |

## Checklist
- [ ] Controller inherits from `http.Controller`
- [ ] Routes have appropriate `auth` level
- [ ] `csrf=False` only on webhook endpoints
- [ ] Public or unauthenticated endpoints authenticate the caller (for example, with a
  verified provider signature) and expose only the intended operation
- [ ] Business logic delegated to model methods
- [ ] Input parameters validated
- [ ] Controller registered in `__init__.py` chain
