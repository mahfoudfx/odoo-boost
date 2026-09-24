# Plan: efficient routine Odoo changes

Status: package implementation applied; client-level benchmark and incident attribution remain open. This document records the agreed design.
Primary-source findings and links are in [research-simple-task-agent-workflows.md](research-simple-task-agent-workflows.md).

## Goal and boundary

Help supported coding agents complete clear, local Odoo changes with focused inspection, one relevant verification pass, and a prompt stop. Preserve deeper investigation for changes whose dependencies or risks require it. Improve correctness and efficiency across clients without assuming that a model will obey a hard tool-call limit.

The reported maintenance-report translation run is a motivating case, not a verified benchmark. Its pasted audit reports no Odoo Boost MCP calls or skill reads, but generated instructions could still have influenced the agent. The original transcript and the installed instructions from that project are needed for causal attribution. Odoo Boost cannot directly limit native editor/shell calls, model turns, client context replay, or compaction.

## Development environment and source layout

The normal workspace is a custom-addon project. Odoo Community core, Enterprise
addons, and other shared addon roots may live elsewhere. Use the effective
Odoo launch configuration (`odoo.conf` and any command-line overrides) to
identify `addons_path`; do not infer that all source is under `project_path`.
`addons_path` lists module directories, while the framework's Python source
may require a separate configured or discovered path. Odoo Boost currently
restricts local MCP file tools to the project root unless additional
`allowed_roots` are configured. Future source resolution should distinguish
custom addons, Community addons and framework, Enterprise, and other
dependencies, and open only the exact external file needed for a task. Odoo's
[module tutorial](https://www.odoo.com/documentation/19.0/developer/tutorials/backend.html)
describes `--addons-path` and custom modules.

Work under the project's Python virtual environment (VENV). Use the configured
VENV interpreter for Odoo Boost and Python-based checks, whether the shell is
activated or an absolute interpreter path is used. The VENV name and location
are project-specific. Resolve them from existing project/agent configuration;
do not search system processes merely to locate an interpreter for a routine
edit. An Odoo command, when authorized, should also use the intended VENV and
target configuration. Odoo's [source-install guide](https://www.odoo.com/documentation/19.0/administration/on_premise/source.html)
documents isolated virtual environments; Odoo Boost's generated stdio MCP
configuration already records an absolute Python interpreter.

## Full custom-module technical surface

Python, JavaScript, Owl, and HTML are examples, not the boundary of Odoo
development. Route by the affected behavior and evidence, across these common
surfaces:

| Surface | Custom-module work that may use it |
|---|---|
| Python and Odoo ORM | Models, fields, compute/onchange methods, wizards, controllers, automation, scheduled jobs, and Python tests. |
| PostgreSQL and SQL | Constraints, indexes, SQL-backed reports/views, migrations, query performance, and stored-data integrity. Prefer ORM for ordinary application behavior. |
| XML and QWeb | Views, inherited XPath, actions, menus, records, security declarations, report templates, email templates, and client templates. |
| CSV and data formats | Access-control lists, imports/exports, demo data, and integration payloads such as JSON or XML. XLSX, EDI, and other formats arise when an addon actually uses them. |
| Gettext localization | POT/PO catalogs, translated labels/messages, plural forms, locales, and right-to-left presentation where relevant. |
| Web client | JavaScript modules, Owl components, registries, services, hooks, widgets, patches, asset bundles, and browser behavior. Website, portal, and point of sale use different frontend bundles. |
| Styling | CSS, SCSS, Bootstrap-based layout, themes, responsive behavior, images, and fonts. |
| Reports and documents | QWeb/HTML and PDF rendering, paper formats, report assets, and optional addon-specific export formats. |
| Interfaces | HTTP controllers, external APIs, webhooks, authentication, and third-party services. |
| Tests and operations | Python/JavaScript tests, browser tours, manifests, `odoo.conf`, VENV dependencies, Odoo server/worker settings, CI, containers, and deployment scripts. |

This is a routing inventory, not a proposal for one skill per language or file
type. Use existing Odoo-specific skills where they add a procedure; add a
focused skill only when repeated tasks expose a knowledge or decision gap.
General syntax is better served by the project's formatter, linter, type
checker, tests, and authoritative language documentation. Odoo's
[assets](https://www.odoo.com/documentation/19.0/developer/reference/frontend/assets.html)
and [testing](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)
references illustrate the multiple frontend and test surfaces. An eventual
small-edit path in the existing Owl skill is a candidate if frontend traces
show the same creation-workflow overhead seen for reports.

## Versioned local documentation

An optional local checkout of the official
[Odoo documentation sources](https://github.com/odoo/documentation), pinned to
the deployed Odoo version, can provide offline and reproducible reference
lookup. Keep it outside custom-addon projects and search the relevant source
page or section; a full HTML build is optional. The documentation repository
supports local builds and can incorporate matching local Odoo source docstrings.
Keep documentation and Community/Enterprise source as distinct roots: docs
explain public behavior, while the exact source resolves a symbol, inheritance
anchor, or version-specific uncertainty. Return concise cited excerpts rather
than putting whole manuals into agent context. Refresh the checkout deliberately
when the deployed Odoo version or chosen documentation revision changes.

## Classification rule

Start on the **routine path** when all of these hold:

1. The requested result and authoritative local target can be identified precisely.
2. The edit reuses existing data, fields, actions, behavior, or a known local pattern.
3. It does not change access, stored data meaning, cross-model behavior, unattended execution, or a migration boundary.
4. A focused static or offline check can catch the realistic failure modes.

Routine path: locate the exact source and relevant reference; inspect the matching range; edit the smallest relevant files; run the cheapest meaningful check and review the diff; stop. The number of files or tool calls is not a classifier. If a condition fails, name the concrete uncertainty or risk and expand only far enough to resolve it. Reassess after a failed check.

### Catalog of routine-path candidates

The catalog is illustrative and open-ended; matching the classification rule matters more than matching an example.

| Area | Common examples when the rule holds |
|---|---|
| Text and i18n | Rename labels, titles, buttons, tabs, menus, actions, report headings and columns, tooltips, help, placeholders, selection display labels, email subjects, and notification text; add or correct specific PO entries. |
| Form views | Move existing fields or buttons; reorder groups or tabs; change a tab title, spacing, columns, or emphasis; display an existing field elsewhere. |
| List views | Add, remove, or reorder existing columns; change a label, widget, optional visibility, decoration, or displayed total. |
| Kanban views | Rearrange an existing card; display an existing field; adjust copy, icon, CSS class, or card layout. |
| Search views | Rename or reorder existing filters and group-by choices; expose an existing searchable field; add a simple filter whose meaning and domain are clear. |
| Navigation | Rename or reorder an existing menu; change an existing action's name or view order; change an existing button's text or icon. |
| Reports and QWeb | Correct static text, translations, headings, columns, spacing, alignment, and presentation of data already available to the template. |
| Website and portal | Correct copy, links, classes, spacing, and existing template layout; show a value already available in context. |
| Frontend assets | Small CSS/SCSS changes and copy or layout changes in an existing OWL template. |
| Model presentation | Change an existing field's `string` or `help`, or a selection option's visible label, without changing its technical value. |
| Existing wizards and mail | Rename labels, rearrange existing fields, or correct static email and wizard text. |
| Project upkeep | Correct documentation, examples, comments, or a narrow test expectation when intended behavior is already known. |

### Bounded changes and escalation signals

Adding a field to an existing model, related/computed field, smart button, new kanban view or grouping behavior, new search domain, view modifier, action, menu, wizard, report, template, default, sequence, scheduled action, or manifest dependency needs targeted checks of its affected model/view/action, install order, data, or access boundary. These can still be efficient; they do not automatically require a full source trace.

Start deeper when the task changes security, public routes, migrations, production data, accounting or stock integrity, or broad cross-module behavior. Also expand when the source occurrence is dynamic, the target or inheritance anchor is ambiguous, a version-specific API is genuinely needed, or the focused check fails. A one-line diff can cross one of these boundaries.

## Proposed package changes

### Decision: rules, skills, agents, and workflows

| Mechanism | Planned role | What to avoid |
|---|---|---|
| **Shared rules** | Put the short classification rule, routine stopping condition, and escalation signals in the generated instructions for every supported client. Keep the existing Odoo version and live-environment boundaries. | Do not add a long per-task catalog, mandatory planning, or a hard call cap to always-loaded instructions. Do not create multiple overlapping always-on rules. |
| **Skills** | Keep technical recipes on demand. Add the focused translation and existing-model skills below, and add small-edit paths to the existing report and view skills. | Do not require a skill read for a self-evident text edit or make a broad workflow skill activate for all Odoo files. |
| **Specialist agents** | Keep source tracing and code review available for ambiguous inheritance, coupled behavior, security, migrations, and other substantive risks. State that a routine edit should be completed by the active agent. | Do not introduce a planner, triage agent, or reviewer handoff for every simple task. Agent handoffs add turns and context and should have a named purpose. |
| **Workflows** | Define three routes in the shared guidance: routine local edit, bounded feature, and deep investigation. Each has an evidence-based exit condition. The route may change as evidence appears. | Do not impose UncleCat's trace-first workflow or a full install/test/review sequence on every edit. |

The rules and routes are model guidance. Odoo Boost can generate them for its supported clients and enforce limits only on calls to its own MCP server. Automatic limits on native calls or per-task token use require a client integration that observes those actions. Adding an Odoo Boost agent would not provide that enforcement.

### 1. Tighten the small always-loaded router

Update `guidelines/composer.py` to state the routine classification, the locate/edit/check/stop sequence, and explicit escalation signals in a few lines. Keep version verification conditional on a version-dependent decision; a PO entry or static label does not justify reading Odoo core translation internals. Put detailed procedures in on-demand references. Keep the router compact and portable to all supported agents.

Align `guidelines/core/operating_rules.md` and `verification.md` with the same decision rule. Do not add a hard maximum of six calls, a mandatory plan, a mandatory skill read, or a blanket upstream-source prohibition. The current operating rules already contain much of this guidance; remove duplication and resolve ambiguity instead of expanding the persistent prompt.

### 2. Add and refine narrowly triggered skills

| Work item | Intended content and boundary |
|---|---|
| New `translation_edits` skill | Edit existing PO translations: identify exact `msgid` and occurrence/context; preserve catalog structure and unrelated entries; edit only requested locales; validate PO syntax, target coverage, and diff. If the source string itself changes, explain when POT regeneration or extraction becomes relevant. No routine database upgrade, global catalog regeneration, or Odoo core investigation. |
| Extend `report_development` | Put an existing-report edit path before creation examples. Cover QWeb text, static headings, columns, formatting, and translation occurrences. Route to full report development only for new templates, actions, or data calculations. |
| Extend `xml_views` | Keep the current small-edit path and add short existing-kanban and smart-button guidance. A purely visual edit stays routine; a new count/action/domain checks the related model and access boundary. |
| New `extending_models` skill | Cover an ordinary field added to an existing model, with optional view use; check type, imports, storage/default, existing records, and access implications. Route computed/related fields to their existing domain skill as needed. Keep `creating_models` for new models. |

Give every skill a narrow activation description. Keep root `SKILL.md` files short and put longer examples in references. Update the loader/catalog, package data, documentation, and skill-install/update tests for new skills. Preserve custom or edited installed files under the current ownership rules.

### 3. Use external skills selectively

Review UncleCat's versioned translation, views, actions, and reports material against official Odoo documentation and target-version source. Borrow only specific accurate examples or bounded-reading ideas that fill a measured gap; pin the reviewed revision and retain required attribution/license notices. Odoo Boost already credits UncleCat ideas in `source_trace`.

Do not import the full pack or make its `odoo-workflow` mandatory. Its current workflow requires source tracing, a cited Context Brief, install/test/i18n steps, and code review for every Odoo Python/XML change. That would add work to the routine path. Keep `source_trace`, review agents, and versioned deep references available for named uncertainty or risk.

### 4. Consider a deterministic helper only after evaluation

If PO editing repeatedly fails despite the focused skill, prototype an offline command that reports missing/ambiguous translation occurrences and validates requested locales with compact output. Evaluate whether an existing parser and a short script suffice before adding an MCP tool. Avoid adding a tool schema to every client for a task solvable locally.

## Evaluation and acceptance

1. **Baseline first.** Inspect the generated instructions and Odoo Boost version installed in the affected project, if available. Obtain the original client trace to distinguish actual input tokens, cached/replayed input, tool calls, compaction, and elapsed time. Do not attribute costs solely to the model or package without that evidence.
2. **Task set.** Add representative cases to `docs/workflow-evaluation.md`: report PO translations; label/title rename; existing form/list/kanban rearrangement; QWeb formatting; simple search filter; field on an existing model; smart button. Include near-misses that require escalation: dynamic report text, uncertain inherited XPath, access-sensitive smart-button action, required field with existing rows, and a failed focused check.
3. **Compare configurations.** Run the same task fixtures with current and candidate instructions in the same client/model. Separate fresh sessions from long-context sessions. Test at least one other supported client if available. Repeat enough runs to expose variance rather than trusting one successful trace.
4. **Record outcomes.** Correctness and first-pass completion are gates. Also record elapsed time; client-reported input/output and cached tokens where available; model/tool turns; files and skills read; specialist-agent handoffs; repeated reads; unrelated upstream-core exploration; verification steps; and compactions. A routine case should end after its relevant check and diff, with no unexplained broad scan or agent handoff. A near-miss must escalate correctly.
5. **Accept or revise.** Keep an instruction or skill change only if routine-task overhead decreases without a correctness regression or missed escalation. Report client-specific differences and any token-accounting limits. Do not use the package unit tests as evidence of model obedience.

## Implementation order

1. Capture baseline and exact installed guidance; expand evaluation fixtures.
2. Revise the compact router and aligned references; run generated-text and agent snapshot tests.
3. Add the translation skill and existing-report path; benchmark the motivating task.
4. Add existing-model and UI paths; benchmark bounded and near-miss cases.
5. Decide whether any deterministic helper is justified by observed failures.
6. Document results and rollout guidance, including the benefit of a fresh client session for unrelated tasks after a very long debugging conversation.

No client-independent prompt rule can guarantee a turn or token budget. If hard limits or automatic telemetry become necessary, they belong in a client integration or opt-in wrapper that can observe native calls, not in the Odoo Boost MCP server alone.

## Delivery status

The compact router, verification guidance, two focused skills, existing-report and view paths, skill routing, documentation, and evaluation cases are implemented in the package. The offline translation helper remains conditional on observed failures. The reported incident cannot be replayed or attributed from this repository alone because its original transcript, project fixture, and installed client instructions are not present. Real-client comparisons remain the next measurement step.

## Next enhancement iteration

The next iteration has two connected workstreams. First, resolve the configured
VENV, effective Odoo launch configuration, custom/Community/Enterprise addon
roots, framework source, and optional version-pinned local documentation. Keep
the returned project-context summary compact and distinguish discovered paths
from paths allowed for MCP file access.

Second, audit **all** common custom-module technical surfaces against the
existing skills, rules, and checks. Use one routine task and one boundary case
per surface. Frontend work is one row in this audit, not its default priority.

| Surface | Coverage question for the next audit |
|---|---|
| Python/ORM | Can an agent modify an existing model, compute, wizard, or controller with the right focused checks? |
| PostgreSQL/SQL | Does it recognize when constraints, SQL views, migrations, or performance work need data-integrity checks? |
| XML/QWeb and CSV | Can it change views, actions, reports, ACLs, and data files while resolving the exact XML ID or inheritance anchor? |
| PO/POT localization | Does it find the source occurrence, update only requested locales, and validate the catalog? |
| JavaScript/Owl and CSS/SCSS | Can it edit an existing component, registry entry, template, or asset bundle without following a new-component scaffold? |
| HTTP and integrations | Does it check authentication, payload, and external API boundaries for a changed route or integration? |
| Reports and exports | Does it distinguish static QWeb/PDF presentation from new calculations, paper formats, and addon-specific export behavior? |
| Tests and deployment configuration | Does it use the project VENV and relevant Python, JS, or browser check; resolve manifests, `odoo.conf`, and addon paths correctly? |

For each row, record existing coverage, a concrete failure or ambiguity, the
smallest useful change (rule, existing skill, new skill, documentation lookup,
or deterministic check), and before/after client evidence. Prioritize by
frequency, failure cost, and observed agent overhead. This keeps the catalog
open to other Odoo technologies and module-specific formats without loading a
generic guide for every language into every task.

### Sources for the next skill review

Use this source order when a coverage gap calls for a skill change:

1. Start with the affected custom module, its project conventions, effective
   configuration, and a real task trace. These establish what the agent must
   do and where it currently spends time or makes mistakes.
2. Check behavior against the [official Odoo documentation](https://github.com/odoo/documentation)
   for the deployed version. Consult the matching
   [Odoo Community source](https://github.com/odoo/odoo), accessible Enterprise
   source, or dependency source when an exact API, inheritance anchor, or
   version-specific behavior needs confirmation. Use
   [OCA maintainer guidance](https://github.com/OCA/maintainer-tools) when the
   project follows OCA conventions; distinguish those conventions from Odoo
   framework requirements.
3. Use the [Agent Skills specification](https://agentskills.io/specification),
   [Anthropic skill examples](https://github.com/anthropics/skills), and
   [OpenAI's current plugin examples](https://github.com/openai/plugins) to
   assess skill packaging, trigger descriptions, progressive disclosure, and
   scripts. The older [OpenAI skills catalog](https://github.com/openai/skills)
   points to the plugin repository as its replacement. These repositories
   supply design patterns, not authority over Odoo behavior.
4. Review individual [UncleCat Odoo guides](https://github.com/unclecatvn/agent-skills)
   or other third-party skills only when they address a named gap. Verify each
   borrowed Odoo claim against the target version and record the reviewed
   revision, applicable license, and attribution. Keep client-specific agents
   and mandatory workflows out of the default routine path.

For each candidate skill, state its triggering task and exit condition, the
version-specific facts it needs, and the smallest focused check it should run.
Compare a routine case and a boundary case with the existing guidance. Adopt
the skill only when it improves correctness or reduces observed overhead
without causing inappropriate activation. Record a source/provenance note and
the comparison result; otherwise improve an existing skill, rule, or lookup
instead. This review applies equally to Python, SQL, XML, localization,
frontend, integration, report, test, and operations work.

### Iteration delivery status

The package now records a detectable project VENV at install time and accepts
explicit paths for the project VENV, `odoo.conf`, launch working directory and `addons_path`
override, Odoo source, and optional local documentation. The read-only
`odoo://project/context` resource reports their resolved state and MCP file
access separately; `search_docs` returns an existing local source page when a
documentation checkout is configured. A separate optional documentation pack
now provides pinned 18.0–20.0 text snapshots; the installer can also use an
existing checkout or download the matching branch into a shared cache.
`search_docs(query=...)` searches its index and returns bounded excerpts with
local and online citations. No path is added to `allowed_roots` automatically.

The [stack coverage audit](stack-skill-audit.md) records a routine and boundary
case for every listed surface. Existing Owl and controller skills now offer a
short edit route before their creation examples. Client traces and before/after
token and time comparisons remain the acceptance gate for any further skill
expansion; this repository does not contain the original incident fixture.
