# Reference extraction: automation, wizards, and chatter

This focused review compares local book/code samples with official documentation
snapshots listed in `references/odoo-official-docs/manifest.json`. It is not a
claim of complete reading or runtime execution of the book corpus.

## Evidence reviewed

Local book paths are under `references/odoo-books/`:

- `cybrosys/development/server-side-development__wizards.txt`: transient input,
  defaults, form button and leave-record creation example.
- `cybrosys/development/emails__chatter.txt`: discussion, internal notes, followers,
  and scheduled activities.
- `Odoo-19-Development-Cookbook-6E/Odoo-19-Development-Cookbook-6E-Examples/Chapter20/02_chatter_in_form_view/my_hostel/models/hostel_room.py`:
  sampled model and dependency patterns; it does not itself establish tracking
  security or delivery guarantees.

Official source files were read from the matching revision directories:
`content/developer/reference/backend/actions.rst` in 15.0, 17.0, 18.0, 19.0 and
20.0; and 18.0 `mixins.rst`, `security.rst`, `orm.rst`, plus
`content/contributing/development/coding_guidelines.rst`.

## Verified extraction and implementation

| Topic | Before | Verified rule retained in package |
| --- | --- | --- |
| Cron XML | Universal `numbercall` example | Select fields from configured series; older 15/17 docs list the field, absence from later prose alone is not proof of removal |
| Cron progress | Generic bounded loop without scheduler contract | 18 documents `_notify_progress`; 19/20 document `_commit_progress` with time-budget return and framework batching |
| Recoverable errors | Catch any exception and continue without rollback | Restore transaction consistency before subsequent queries; isolate recoverable units, distinguish unexpected failures |
| Wizard action | Direct write to a target state and presumed chatter mixin | Implement verified business operation; validate caller-controlled context, target permissions, state and company |
| Tracking | Claimed automatic audit entry for every change | Supported field tracking can be disabled by context; no immutable audit guarantee |
| Messages | Notification example described guaranteed public follower delivery | Distinguish internal subtype visibility and recipient/subscription-dependent delivery |

Package destinations: `domain_crons_automation/SKILL.md`,
`domain_wizards/SKILL.md`, and `domain_mail_chatter/SKILL.md` under
`src/odoo_boost/skills/`. No local-book lookup or copied cookbook code was added.
The wizard Python class and XML remain explicitly structural templates requiring
an application-specific `action_apply` implementation; a generic direct state
mutation is no longer presented as a complete workflow.

## Official citations

- [15 actions](https://github.com/odoo/documentation/blob/15.0/content/developer/reference/backend/actions.rst)
- [17 actions](https://github.com/odoo/documentation/blob/17.0/content/developer/reference/backend/actions.rst)
- [18 progress](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/actions.rst)
- [19 progress and triggering](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/backend/actions.rst)
- [20 progress](https://github.com/odoo/documentation/blob/20.0/content/developer/reference/backend/actions.rst)
- [Mail tracking flags and subtypes](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/mixins.rst)
- [Public-method arguments and escaping](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/security.rst)
- [Transaction ownership](https://github.com/odoo/documentation/blob/18.0/content/contributing/development/coding_guidelines.rst)

Validation: `tests/test_skills.py` passed (34 tests); `git diff --check` passed.
These checks cover package skill loading/installation, not live scheduler,
notification delivery, or application workflow behavior. Exact runtime field
removal claims and generated API details require matching official source before
being promoted to version-specific rules.
