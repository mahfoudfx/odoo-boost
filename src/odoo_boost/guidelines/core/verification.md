# Verification by Change Type

Choose the cheapest check that can catch a realistic failure. Review the final diff in every case. These are starting points, not a fixed sequence; add a check when a concrete dependency or risk appears.

| Change | First useful evidence | Expand when |
|---|---|---|
| Label, translation, or formatting | Exact target and reference; XML/CSV parse if relevant; diff | A referenced field, external ID, or XPath is uncertain |
| Existing view structure or modifier | Target record, inheritance anchor, field existence, XML parse | Inheritance order or dependent views are unclear |
| Local Python method | Caller and override context; focused test or static check for changed behavior | Side effects cross models, companies, or transactions |
| New field, model, or data record | Imports, manifest/data order, external IDs, ACLs, and focused behavior check | Migration, access, or stored data impact is unclear |
| Access rule, public route, `sudo()`, or raw SQL | Relevant security reference; positive and negative authorization cases | A wider trust boundary or data exposure is affected |
| Migration, accounting, or stock valuation | Invariants, affected data paths, and targeted regression checks | Release or data integrity evidence requires broader validation |

Do not create a test that merely repeats the implementation. Report any behavior that could not be verified. Live database checks and module upgrades still require the user's explicit request.
