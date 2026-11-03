# Odoo Performance Guide

Use for slow ORM code, repeated queries, large batches, and cron workloads.
Measure on representative data under the intended user and company first.

## Measure and preserve behavior

Record elapsed time, query count, input size, and expected results before changing
code. Use the target version's profiler and query-count assertions. Compare warm
and cold cache behavior; profiling itself adds overhead. Keep permission checks
and business-method side effects in the measured path.

## Batch ORM work

Browse a collection of IDs together before iterating so records share prefetch.
Repeated singleton browsing can defeat that benefit. Related records can trigger
additional fetches; `mapped()` alone does not guarantee that every later field is
already cached. Avoid relying on a fixed prefetch batch size.

Create a list of values in one call when the target model supports batch create.
Write shared values to a recordset together. Preserve overrides and per-record
semantics. For counts across many parents, aggregate once and map counts back,
including zero matches. Check `read_group` / `_read_group` signatures and result
shapes against the configured version.

Use a domain to restrict large datasets at the database. For a small recordset
already in memory, filtering may be appropriate. Choose `search_read` when the
caller needs dictionaries; keep recordsets when later ORM behavior requires them.

## Indexes and stored values

Choose indexes from observed filters, joins, ordering, and query plans. Low
selectivity and write overhead can make an index unhelpful. Confirm index types
in the target version. Stored computes trade read cost for dependency-driven
writes; assess fan-out and data freshness before adding `store=True`.

## Raw SQL and cache consistency

Prefer ORM operations. Direct SQL bypasses ORM access checks and model hooks;
a bulk operation is not by itself a reason to bypass those behaviors.
Parameterize values and compose identifiers with supported helpers. Check the
availability of `odoo.tools.SQL`; do not infer an API requirement from a book's
edition number.

For necessary SQL writes, flush relevant pending ORM fields first. Odoo 15
documents `invalidate_cache`; 17/18/19/20 document the newer recordset invalidation
and dependency-notification example. Select the configured API before coding. Identify
changed records, invalidate the affected cached fields, and notify dependency
tracking with `modified()` when required. Invalidating the cache alone does not
schedule every dependent stored computation. Verify both immediate reads and
stored dependent values after the change.

## Bounded jobs and transactions

Process bounded batches using the scheduler progress API available in the target
version. Normal ORM methods leave commit and rollback to the framework. Explicit
transaction ownership requires a separately justified design and cursor lifecycle.

When processing removes records from a search domain, increasing an offset skips
remaining work. Re-query the remaining domain or use a stable ID cursor with
explicit ordering. Choose a policy for failed records so they cannot trap the job
in an endless first batch. Consider concurrent workers and idempotency.

If failures may be isolated, use a savepoint around each recoverable unit before
catching its exception. A caught database error can leave the transaction unusable
without rollback. Log enough context to retry safely. Verify that every eligible
record is processed once according to the job's retry policy.

## Completion criteria

Compare outputs and permissions with the baseline, measure query count and time,
and test a dataset larger than one batch. Include a failure in a middle batch and
confirm retries do not skip or duplicate side effects.

## Primary references

- [Odoo performance guidance](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/performance.rst): profiling, batches, prefetch, and indexes.
- [Odoo coding guidelines](https://github.com/odoo/documentation/blob/18.0/content/contributing/development/coding_guidelines.rst): transaction ownership and exception handling.
- [Odoo ORM reference](https://github.com/odoo/documentation/blob/18.0/content/developer/reference/backend/orm.rst): SQL, flush, invalidation, and modified fields.

These principles are independently written and packaged with the skill. Consult
the configured version for exact APIs; local books are not runtime dependencies.
