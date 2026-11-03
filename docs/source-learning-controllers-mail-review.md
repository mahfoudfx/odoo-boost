# Source learning: controllers, mail and activity lifecycle

Reviewed 2026-11-03. This pass uses **code examples**, not new book-prose
reading. Controllers are in Chapter13 in both cookbooks. Mail/mixins are in
v17 Chapter23 and v19 Chapter20; v17 Chapter20 is external RPC and was not
silently treated as the matching mail chapter.

## Scope and reading method

Selected all Python/CSV files, data/security XML, student views, website override
templates and digest views in those four chapter roots. This provides controller,
model/import, manifest, ACL, template and lifecycle context; other room UI XML,
binary assets and metadata remain separate units. Selection has **414 paths /
105 distinct contents**. Six contents already had reading evidence from earlier
passes and are linked by hash. This pass read **99 new representative contents**:
65 through full-text inspection and 34 v19 variants through their complete diffs
against previously read full-text baselines. Unchanged portions are traceable to
those baselines; changed portions were inspected rather than inferred from names.

Exact files and diff baselines are supplied to the integrating reviewer in
`/tmp/source-controllers-mail-evidence.json`. All other selected paths retain
pending-context lineage, not automatic duplicate completion. This is not full
coverage of either chapter's prose, every XML view, deployed model assembly or
email/browser behavior.

## Retained experience

Locators are relative to the respective `*-Examples` root. Every lesson has
**code example** origin, with official evidence establishing accepted framework
contracts and source inspection establishing local defects.

| Lesson | Exact stimulus | Decision and project benefit | Disposition |
|---|---|---|---|
| SC-01 | Both Chapter13 `01_http_paths` and `02_paths_auth`, controller `main.py`, manifests/ACLs | Authentication mode and disclosure policy are separate decisions. `none` can be active without a database; a route that queries `request.env` cannot assume that context. The sample none/public routes use unbounded `sudo` searches and raw name interpolation. Retain the route lesson while using intended-user access or a deliberate publication domain, bounded results and escaped output. | Existing controller/security guidance confirmed with complete adjacent examples; no production template copied. |
| SC-02 | Both Chapter13 `03_paths_with_parameters/.../controllers/main.py` | Route converter tokens and endpoint parameter names form a call contract. Both versions name the token `student` but the endpoint parameter `book`. v17 additionally references undefined `student` in its body; v19 changes the body to `book.id` without changing the route token. Check absent/malformed IDs, record existence/access and actual parameter binding. | Concrete static defect retained. Pinned HTTP code filters incoming kwargs then calls the endpoint; this is not a reported live exception trace. |
| SC-03 | Both Chapter13 `04_path_override/website_ext/` controller, manifest and template | Preserve route publication with empty `@http.route()`, use `super`, and change only the intended response context. This example properly declares `website` and keeps escaped template output. Its XPath still depends on the installed parent template and any preceding extensions. | Positive extension pattern retained; existing controller/UI guidance confirmed. Parent template availability and rendered result were not runtime-tested. |
| SC-04 | Chapter13 HTTP versus JSON route variants and `models/sample_auth_http.py` | Select dispatch/authentication contracts from actual source. v17 uses `json`; v19 uses `jsonrpc`, with pinned19 source retaining a deprecated `json` alias. Custom auth exercises contain placeholder route bodies and should remain exercises, not be installed as finished authentication modules. | Version guidance confirmed. No universal custom-auth string parser or finished external callback authentication is inferred from the sample. |
| SC-05 | v17 Chapter23 and v19 Chapter20 recipes02/03, manifest + student model + form | Mail dependency, thread mixin, activity mixin and view integration are separate pieces. `mail.thread` alone does not add activity scheduling. v19's create override preserves a multi-create recordset and loops results; v17 uses the older single-create adapter. Schedule the intended activity after record creation and verify responsible user/date. | Existing mail/ORM guidance confirmed through a complete model/view/dependency chain. No activity was scheduled in a server. |
| SC-06 | Mail recipe03 versus recipe04 student models in both versions | A later chapter snapshot is not guaranteed to preserve earlier behavior. Recipe03 schedules a call when `discharge_date` exists at create; recipe04 replaces create with partner creation/subscription and drops that scheduling. It also does not cover later date changes, cancellation or retry deduplication. Decide the event contract before composing features. | New lifecycle counterexample retained. Verify create, later update, cancellation and retry, rather than assuming the final sample accumulates all earlier recipes. |
| SC-07 | Mail recipes04/05 student methods, mail-template XML and student view | Separate rendering a template, posting a message, subscriber/recipient selection, queue creation and external delivery. The source derives sender from the room creator, recipient from student email, and adds one partner/follower per student creation. Validate assigned-room state, sender policy, missing addresses, identity reuse and visibility before promising notification delivery. | Existing recipient/privacy guidance confirmed with new concrete verification inputs. Exact `message_post_with_source` signature is not certified by the stale illustrative mixin prose. |
| SC-08 | Both mail recipe06 student `message_new` and alias XML | Inbound email is external input. Alias contact policy and mail routing are separate from parsing `From`. The example assumes `Display Name <address>` with unchecked regex `.group(1)` and indexes the first parsed address; a bare valid email fails the regex assumption. Define fallback/rejection, malformed/multiple-address handling and custom-value precedence. | New input-validation counterexample retained, with a pure regex reproduction. No mail gateway or spoofing claim is made from a local parser finding. |
| SC-09 | Both mail recipe07 tracked fields and recipe08 digest model/manifest/view | Tracking is configurable history, not immutable audit. Digest metric naming, date interval, company/visibility scope, recipients and periodicity need separate review. v17 labels its KPI Room Rent but computes a room count; v19 renames it Room Created. Both receive a company from the private helper but omit company filtering; their room model has no company field, so intended shared-versus-company scope must be designed before adding a filter. | Existing tracking rule confirmed and a new metric-definition scenario retained. Private digest helper signatures and exact delivery behavior remain target-source/runtime questions. |

Additional source-quality observations are retained as context rather than new
universal rules: some room computes omit default assignment when dates are absent,
some negative-rent constraint examples omit `ValidationError` imports or assume
singleton access, and controller-era v19 snapshots retain older constraint
declarations while mail-era snapshots adopt `models.Constraint`. These reinforce
the existing dependency/batch/version review process; no automatic rewrite of
teaching snapshots was made.

## Official verification and boundaries

Pinned documentation revisions: 17
`fbf3e3a6ef0bda7c30b28f213848deca17c2a872`; 19
`de94dcddba224a1ece042792fa444e7ba0c31fdf`. Pinned implementation revisions:
17 `6f00fdadb875342de2d14a179f25431f93cd63c9`; 19
`9dea17e805e1f513416b53c566895df26f0f560d`. Local pinned files supplied the checks.

- [17 HTTP controllers](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/http.rst) and [19 HTTP controllers](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/http.rst): publication and decorator option inheritance.
- [17 HTTP implementation](https://github.com/odoo/odoo/blob/6f00fdadb875342de2d14a179f25431f93cd63c9/odoo/http.py) and [19 HTTP implementation](https://github.com/odoo/odoo/blob/9dea17e805e1f513416b53c566895df26f0f560d/odoo/http.py): `route` authentication/dispatch documentation, kwargs filtering and endpoint calls; 19 deprecated JSON alias.
- [17 security](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/security.rst) and [19 security](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/security.rst): access bypass, public-method inputs and escaping.
- [17 mail mixins](https://github.com/odoo/documentation/blob/fbf3e3a6ef0bda7c30b28f213848deca17c2a872/content/developer/reference/backend/mixins.rst) and [19 mail mixins](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/mixins.rst): incoming `message_new`/custom values, subscriptions, alias policy, separate activity mixin and tracking context controls. Some helper signatures/examples in this prose are legacy; this report does not substitute them for a deployed-source check.
- [19 digest emails](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/applications/general/companies/digest_emails.rst): periodicity, recipient configuration, KPI field pair and duplicate-database delivery warning. A staging restore should explicitly account for outbound digest scheduling.

The public-source checks establish workflow distinctions; neither code comments
nor static review prove mail delivery, recipient authorization on a full installed
stack, method existence in all older/newer branches or private helper compatibility.

## Validation and retained result

AST inspection confirms route-token/argument mismatch and the v17 undefined body
name; regex evaluation confirms the bare-address parsing failure. Source comparison
confirms activity scheduling is present in recipe03 and absent in recipe04 in both
editions. No addon import, HTTP request against Odoo, email send, digest schedule or
database mutation occurred.

Nine new lesson records and exact read/diff/duplicate lineage are ready for the
shared ledger. The project's existing controller, security and mail skills already
contain the accepted core policies, so this pass adds traceable scenarios and
counterexamples without unnecessary package changes. Remaining repeated recipe
contexts, other view files, mail-source API inspection and runtime checks stay open.
