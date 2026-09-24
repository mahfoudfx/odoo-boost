# Verification by Change Type

Choose the cheapest check that can catch a realistic failure. Review the final diff in every case. These are starting points, not a fixed sequence; add a check when a concrete dependency or risk appears.

| Change | First useful evidence | Expand when |
|---|---|---|
| Label, translation, or formatting | Exact target and reference; XML/PO/CSV parse if relevant; diff | The source occurrence is dynamic or ambiguous, or a referenced field, external ID, or XPath is uncertain |
| Existing view structure or modifier | Target record, inheritance anchor, field existence, XML parse | Inheritance order or dependent views are unclear |
| Smart button with a new action or count | Target model, action/domain, count source, access boundary, XML parse and focused behavior check | Records cross companies or permission boundaries, or inherited behavior is unclear |
| Local Python method | Caller and override context; focused test or static check for changed behavior | Side effects cross models, companies, or transactions |
| Field on an existing model | Field type, import, default/storage, affected view reference, access exposure, and focused behavior check | Existing rows, computed dependencies, or cross-model data change the behavior |
| New model or data record | Imports, manifest/data order, external IDs, ACLs, and focused behavior check | Migration, access, or stored data impact is unclear |
| Access rule, public route, `sudo()`, or raw SQL | Relevant security reference; positive and negative authorization cases | A wider trust boundary or data exposure is affected |
| Migration, accounting, or stock valuation | Invariants, affected data paths, and targeted regression checks | Release or data integrity evidence requires broader validation |

Do not create a test that merely repeats the implementation. Report any behavior that could not be verified. Live database checks and module upgrades still require the user's explicit request.
