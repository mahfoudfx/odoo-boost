## Controllers

### HTTP Controllers
- Inherit from `http.Controller` and use `@http.route()` decorator.
- Route types: `type='http'` (HTML pages) or `type='json'` (JSON-RPC).
- Auth modes: `auth='user'` (logged in), `auth='public'` (anyone), `auth='none'` (no session).
- Always specify `website=True` for website-integrated routes.

### Route Definition
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):
    @http.route("/my/page", type="http", auth="user", website=True)
    def my_page(self, **kwargs):
        return request.render(
            "my_module.my_template",
            {
                "records": request.env["my.model"].search([]),
            },
        )

    @http.route("/api/data", type="json", auth="user")
    def api_data(self, model_name, domain=None):
        records = request.env[model_name].search_read(domain or [])
        return {"records": records}
```

### Best Practices
- Use `request.env` to access the ORM environment — it's pre-configured with the current user.
- Return `request.render()` for HTML, return a dict for JSON routes.
- Use `request.redirect()` for redirects.
- Validate and sanitize all input parameters — controllers are the system boundary.
- Use `csrf=False` only for webhook endpoints that receive external POST requests.
- Don't put business logic in controllers — call model methods instead.
- Use `methods=['POST']` to restrict routes to specific HTTP methods when appropriate.

### Extending Controllers
- Inherit the controller class and override/extend routes.
- Call `super()` when extending to preserve parent behavior.
- Use `route=` in the decorator to keep or update the URL pattern.
