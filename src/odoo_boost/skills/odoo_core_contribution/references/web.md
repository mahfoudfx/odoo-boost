# Web contribution checks

- Apply these as Odoo repository house rules. A custom addon may follow its own
  established conventions where they differ.
- Organize JavaScript, templates, and styles by feature so coupled behavior is
  reviewed together.
- Prefer registries, services, hooks, composition, and supported extension
  points. Patch framework code only when no stable extension point exists, keep
  the patch narrow, and test interaction with other patches.
- Prefer explicit methods over getters where evaluation cost or side effects
  would be hidden.
- Prefix CSS classes with the owning module namespace. Avoid ID selectors and
  keep selectors scoped to the feature.
- Ship readable, unminified third-party sources under `static/lib`; declare
  application assets through the target version's manifest conventions.
- In Owl loops, provide stable keys. Escape data before it reaches HTML sinks;
  do not turn an untrusted string into trusted markup.
