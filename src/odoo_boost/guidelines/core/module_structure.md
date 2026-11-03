## Module Structure

### Standard Directory Layout

This example uses the Odoo 15/17/18/19 ACL and record-rule layout. For Odoo 20,
use the access CSV filename and schema described under File Naming below.
```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml          # groups + record rules
├── data/
│   └── data.xml              # default data records
├── demo/
│   └── demo.xml              # demo data (loaded in demo mode)
├── controllers/
│   ├── __init__.py
│   └── main.py
├── wizard/
│   ├── __init__.py
│   └── my_wizard.py
├── report/
│   └── my_report.xml
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       ├── xml/               # OWL component templates
│       └── scss/
└── i18n/
    └── fr.po
```

### __manifest__.py
- `name` is required by the manifest reference. Declare actual dependencies and
  data files explicitly; do not confuse project conventions with required keys.
- Follow the project/OCA version convention, e.g. `18.0.1.0.0`; this is distinct
  from the upstream manifest reference's semantic-versioning recommendation.
- Order `data` files by external-ID dependencies: define groups before ACLs that
  reference them, actions before menus, and referenced records before their users.
- `demo` lists files loaded only when demo data is enabled.
- `assets` defines JavaScript/CSS bundles to include.
- Declare the module's actual compatible license; upstream defaults to `LGPL-3`,
  but community modules may use other supported licenses.
- `installable` defaults to `True`; set to `False` for deprecated modules.

### File Naming
- Model files: named after the model they define (`sale_order.py` for `sale.order`).
- View files: `<model_name>_views.xml` (e.g. `sale_order_views.xml`).
- Access CSV names follow the target model: `ir.model.access.csv` for Odoo
  15/17/18/19, and `ir.access.csv` for Odoo 20. Update the manifest path as well
  as the CSV columns: the filename determines the imported model.
- XML may define groups and other security records. Use `ir.rule` only on the
  older access model; Odoo 20 uses `ir.access` permissions and restrictions.
- Each Python package (`models/`, `controllers/`, `wizard/`) needs an `__init__.py`.


### Data and Lifecycle
- Preserve stable external IDs. Changing them requires an upgrade plan for
  references and existing records.
- `noupdate` preserves installation-time data during normal updates; changing XML
  alone is not a reliable way to update such records in existing databases.
- Hooks implement exceptional installation or cleanup needs; installation hooks
  are not substitutes for upgrade scripts. The audited manifest references specify:
  - Odoo 15: `pre_init_hook(cr)`, `post_init_hook(cr, registry)`,
    `uninstall_hook(cr, registry)`.
  - Odoo 17/18/19/20: each of these hooks receives `env`.
  Inspect the configured loader before reusing an older hook implementation.
- Test installation on an empty disposable database and upgrade on representative
  existing data. Repeat the upgrade to check idempotency and preserved settings.

### Official References
- [Manifest fields and hooks](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/module.rst)
- [Data operations and external IDs](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/data.rst)

- [Odoo 20 CSV filenames](https://github.com/odoo/documentation/blob/20.0/content/developer/reference/backend/data.rst#csv-data-files)
- [Odoo 20 access schema](https://github.com/odoo/documentation/blob/20.0/content/developer/reference/backend/security.rst)
