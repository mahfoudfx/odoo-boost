---
name: domain-crons-automation
description: Implement reliable, batch-safe recurring background jobs with ir.cron.
globs: ["models/**/*.py", "data/**/*.xml"]
---

# Crons and Scheduled Actions

Use this skill for `ir.cron`; event-based `base.automation` is a separate mechanism.

## Define the workload

1. Identify the eligible domain, configured cron user, company scope, side effects,
   retry policy, and maximum batch size. Cron context is not a browser session.
2. Declare only schedule fields available in the target series. Older recipes may
   include `numbercall`; verify model fields before porting their XML. Use stable
   external IDs and choose `noupdate` deliberately to preserve administrator settings.
3. Process a bounded batch under the configured user's permissions. Record success
   so subsequent runs find remaining work. When processing changes the search domain,
   re-query remaining records or use a stable cursor; increasing offsets can skip work.

## Select the scheduler API

- Odoo 15/17: use the documented scheduled-action interface for that series;
  do not copy newer progress calls into it.
- Odoo 18: the actions reference documents `_notify_progress(done=..., remaining=...)`.
- Odoo 19/20: use the documented `_commit_progress` batching contract. Return when
  its remaining-time result reaches zero; let the scheduler manage repeated batches.

The progress method in 19/20 has commit semantics. Keep it outside a per-record
savepoint and use it only in the intended scheduler context. Ordinary model methods
leave transaction ownership to the framework; generic `cr.commit()` loops are not
an interchangeable batching API.

## Handle failures and retries

For a recoverable record failure, isolate its work in a savepoint and catch the
exception outside that savepoint, so failed SQL is rolled back before more queries.
Choose which exception types are recoverable; let unexpected failures propagate.
A logged exception alone does not repair an aborted transaction. Follow the target
scheduler's documented rollback/progress contract when managing batches explicitly.

External side effects require idempotency or deduplication: a database rollback
cannot recall an email or remote API operation. Define a failure state/backoff so
one bad first record cannot starve the remaining queue. Consider concurrent workers
and re-check eligibility when acquiring work.

## Verify completion

Test more than one batch, an empty batch, a failure in the middle, and a retry.
Confirm permissions/company scope, no skipped records, and no duplicated external
side effects. Use the scheduler's supported trigger in a disposable test database;
Odoo 19 documents `method_direct_trigger` in registry test mode.

## Official references

- [Odoo 18 scheduled actions](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/actions.rst)
- [Odoo 19 batching](https://github.com/odoo/documentation/blob/19.0/content/developer/reference/backend/actions.rst)
- [Odoo 20 batching](https://github.com/odoo/documentation/blob/20.0/content/developer/reference/backend/actions.rst)
- [Transaction ownership and exception handling](https://github.com/odoo/documentation/blob/18.0/content/contributing/development/coding_guidelines.rst)
