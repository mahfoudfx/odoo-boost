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
response handling are version-sensitive. The JSON example uses `type="json"`
for 15/17/18; select `type="jsonrpc"` for 19/20. The older spelling remains a
deprecated alias in audited 19/20 source. Bearer authentication is documented
for 18/19/20, and 20 additionally requires `bearer_scope`.

### 1. Create Controller File (`controllers/main.py`)
```python
from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest


class MyController(http.Controller):
    # --- Website Page (HTML) ---
    @http.route("/my/page", type="http", auth="user", website=True)
    def my_page(self, page=1, **kwargs):
        try:
            page = int(page)
        except (TypeError, ValueError):
            raise BadRequest("Invalid page")
        if not 1 <= page <= 1000:
            raise BadRequest("Page out of range")
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
    def api_list(self):
        records = request.env["my.model"].search_read([], fields=["name"], limit=20)
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
                ("Content-Disposition", 'attachment; filename="download.bin"'),
            ],
        )
```

For an external webhook, select HTTP versus JSON-RPC from the provider protocol;
plain JSON is not a JSON-RPC envelope. Authenticate the raw request using the
provider's verified scheme before processing and define replay/idempotency rules.
Implement this separately; an unverified signature comment is not authentication.

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
| `type` | Version-specific | `json` on 15/17/18; `jsonrpc` on 19/20; 20 also has a separate `json2` dispatcher |
| `auth` | `'user'`, `'public'`, `'none'` | Authentication level |
| `methods` | `['GET']`, `['POST']`, etc. | Allowed HTTP methods |
| `website` | `True`/`False` | Integrate with website module |
| `csrf` | `True`/`False` | Check dispatcher defaults; HTTP and JSON-RPC differ |

## Checklist
- [ ] Controller inherits from `http.Controller`
- [ ] Routes have appropriate `auth` level
- [ ] `csrf=False` only on webhook endpoints
- [ ] Public or unauthenticated endpoints authenticate the caller (for example, with a
  verified provider signature) and expose only the intended operation
- [ ] Business logic delegated to model methods
- [ ] Input parameters validated
- [ ] Controller registered in `__init__.py` chain


Redecorate overridden handlers with `@http.route()` to retain publication.
The example JSON route spelling applies to older series; load version notes
before use. Authentication does not authorize every record. For file routes,
verify field access, binary encoding and the supported response helper against
the target model; the generic response above is only suitable for actual bytes.

Official basis: [controller extension](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/backend/http.rst)
and [route/dispatcher contract](https://github.com/odoo/odoo/blob/19.0/odoo/http.py).
