# Custom-module skill coverage audit

This is a static audit of the bundled guidance, completed without a client
trace. It identifies focused evaluation cases; it does not claim a token or
time improvement. The [workflow evaluation guide](workflow-evaluation.md)
defines the client measurements and acceptance gate.

| Surface | Current route | Routine case to replay | Boundary case to replay | Decision from static audit |
|---|---|---|---|---|
| Python/ORM | `extending-models`, `domain-computed-fields`, `domain-wizards`, core ORM guidance | Change a known field label or bounded method | Add a stored or computed field affecting existing rows | Existing routes cover this; retain until a trace shows a gap. |
| PostgreSQL/SQL | `pattern-library` performance and migration references, `security-rules`, code review | Correct formatting in a known SQL view without changing query semantics | Change a constraint or migration with existing data | Require data-integrity evidence for the boundary; no broad SQL skill yet. |
| XML/QWeb/CSV | `xml-views`, `report-development`, `security-rules` | Reorder existing view fields or correct an ACL row | Change an uncertain inheritance anchor or access scope | Existing small-edit path covers views and reports; replay CSV access cases. |
| PO/POT localization | `translation-edits` | Correct exact French and Arabic report entries | Translate runtime-assembled text | Existing focused route covers static text; dynamic text must escalate. |
| JavaScript/Owl/CSS/SCSS | `owl-components`, `xml-views`, asset guidance | Edit an existing component template or scoped style | Change service behavior or a version-sensitive registry entry | Added a short existing-component path to `owl-components`. |
| HTTP/integrations | `controllers-routes`, integration references in `pattern-library` | Correct a private route's existing response text | Change public route authentication or webhook handling | Added a short existing-route path; retain access checks for changed behavior. |
| Reports/exports | `report-development`, `translation-edits` | Correct static QWeb/PDF column text | Add a calculation or new export format | Existing report edit route covers static output; evaluate addon-specific exports before adding guidance. |
| Tests/operations | `testing`, `upgrade-analysis`, config and version guidance | Run one affected test in the configured VENV | Upgrade a module with changed dependencies or stored data | Added `odoo://project/context` for explicit VENV and external-root resolution; no default full-suite workflow. |

## Source and acceptance rule

For Odoo behavior, use the project's custom modules and configuration first,
then version-matched [Odoo documentation](https://github.com/odoo/documentation)
and [source](https://github.com/odoo/odoo). Use
[OCA maintainer guidance](https://github.com/OCA/maintainer-tools) when that
project follows OCA conventions. For skill packaging, consult the
[Agent Skills specification](https://agentskills.io/specification),
[OpenAI plugin examples](https://github.com/openai/plugins), and
[Anthropic examples](https://github.com/anthropics/skills). Review
[UncleCat's Odoo guides](https://github.com/unclecatvn/agent-skills) or other
third-party material only for a named gap, recording revision and license
before adaptation. The detailed source order is in the
[next-iteration plan](routine-task-workflow-plan.md#sources-for-the-next-skill-review).

Run each routine and boundary case in a fixed client/model/repository setup.
Record first-pass correctness, elapsed time, input/output/cached tokens where
available, tool calls, repeated reads, unrelated source exploration, and
missed escalation. Keep a new or revised skill only when it improves the
measured result without a correctness regression. The original maintenance
translation trace and a comparable custom-addon fixture are not in this
repository, so client-level comparison remains open.
