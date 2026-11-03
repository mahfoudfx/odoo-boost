## Controllers

### HTTP Controllers
- Inherit from `http.Controller` and use `@http.route()` decorator.
- Use `type='http'` for HTTP responses. Select the JSON-RPC route spelling from
  configured series: `json` on 15/17/18 and `jsonrpc` on 19/20. The audited
  19/20 source keeps `json` as a deprecated alias; use the canonical spelling.
- `auth='user'` uses the authenticated user; `public` uses the shared Public
  user for anonymous requests. `none` may run without a selected database.
  `bearer` is documented in 18/19/20; review token and session fallback behavior.
  On 20, bearer routes also require `bearer_scope`. Do not backport that option
  to earlier series without checking its route API.
- Always specify `website=True` for website-integrated routes.

Odoo 20 also registers a `json2` dispatcher. Its payload/authentication contract
is separate from JSON-RPC; select it only after inspecting that version's API.

### Route Definition
Choose route type, response helpers, and decorator options from the configured Odoo
version notes. The JSON example below applies where that version supports `type="json"`.

```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):
    @http.route("/my/page", type="http", auth="user", website=True)
    def my_page(self, **kwargs):
        return request.render(
            "my_module.my_template",
            {
                "records": request.env["my.model"].search([], limit=50),
            },
        )

    @http.route("/api/data", type="json", auth="user")
    def api_data(self):
        records = request.env["my.model"].search_read([], ["name"], limit=50)
        return {"records": records}
```

### Best Practices
- Use `request.env` to access the ORM environment — it's pre-configured with the current user.
- Return `request.render()` for HTML, return a dict for JSON routes.
- Use `request.redirect()` for redirects.
- Validate and bound all input parameters — controllers are the system boundary. Never
  accept an arbitrary model name, fields, domain, or sudo flag from a client.
- Retain CSRF protection for browser HTTP writes. External callbacks that disable
  it need independent authentication and replay handling. Check dispatcher defaults:
  HTTP and JSON-RPC routes do not have identical CSRF behavior.
- Don't put business logic in controllers — call model methods instead.
- Use `methods=['POST']` to restrict routes to specific HTTP methods when appropriate.

### Extending Controllers
- Inherit the controller class and override/extend routes.
- Call `super()` when extending to preserve parent behavior.
- Redecorate an overridden route with `@http.route()` to preserve its publication.
  Empty decorator arguments retain inherited options; supplied arguments replace
  those options. Verify the resulting authentication and allowed HTTP methods.


### Verification and Sources
Test anonymous and authenticated access, another user's record IDs, pagination
bounds, and rejected writes. Render untrusted values through escaped templates.
Authentication alone does not authorize every requested record.

See the [official controller extension documentation](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/backend/http.rst)
and [route API and dispatchers](https://github.com/odoo/odoo/blob/19.0/odoo/http.py).
Use the matching branch when implementing another series.
