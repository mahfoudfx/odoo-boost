# Website builder, reporting and translation extraction

Reviewed 2026-11-03. This is an executed, focused source review, not complete
chapter/library coverage. Inputs include v17 Cookbook website prose and examples,
v19 Cookbook translation prose and website/report/translation examples, Cybrosys
18 development pages, and v15 Essentials report prose/examples. The evidence
handoff `/tmp/source-web-evidence.json` gives exact read files and partial EPUB
member/section locators for incorporation into the central coverage ledger.

## What was extracted and retained

| ID | Origin and exact stimulus | Experience extracted | Usefulness and disposition |
|---|---|---|---|
| SW-01 | Both: v17 `OEBPS/B20997_14.xhtml`, dynamic-snippet section; `Chapter14/04_dynamic_snippets/my_hostel/`; v19 `Chapter22/04_dynamic_snippets/my_hostel/` | Treat a snippet as several cooperating contracts: saved XML/DOM, published-page behavior, editor controls and server data policy. Keep frontend and editor assets separate and verify the editor registry against the exact version. The v19 sample's plugin uses `builder-plugins` and a descriptor object, whereas pinned 19 docs show `website-plugins` and `BaseOptionComponent` classes. This is an unresolved compatibility discrepancy, not a verified recipe to copy. | Note retained. Gives concrete migration/review criteria beyond generic Owl guidance. Official 19 building-block docs confirm the separation; exact sample plugin compatibility still needs matching implementation/runtime. |
| SW-02 | Code: v17 dynamic-snippet manifest/JS/XML; v19 dynamic-snippet JS/controller/ACL and builder options | Verify configuration end to end rather than trusting a screenshot. V17's own manifest comments out the JS asset; its JS reads `numberOfRooms` while initial markup writes `number-of-hostel`, and duplicate template IDs need inspection. V19 uses `numberOfHostels`, but the server always limits to five and its style/margin options do not change the count. Client slicing cannot retrieve more records than the server sent. | Note retained as a concrete acceptance scenario: drag, edit, save, reload, duplicate, remove and test as public user. Actual browser behavior was not executed. |
| SW-03 | Both: v17 publication-management section; v19 `Chapter22/09_multiple_websites` and `10_publish_management` controller/model/manifest/security | Publication, website scope and permission to read are separate. The publish recipe loads a public published-only rule, but its list controller calls `sudo().search(domain)` without a published condition. Website scope alone does not enforce publication. Conversely, the earlier dynamic endpoint uses ordinary public-user access while its addon ACL grants access only to managers: public auth does not grant model access. Caller-supplied field names also need an intended projection. | Note retained with exact counterexamples, confirming security/controller guidance. Under the inspected addon policies the patterns conflict with their intended publication behavior; other installed rules/modules and runtime outcomes remain untested. |
| SW-04 | Both: v19 `OEBPS/Text/Chapter_11.xhtml`, export/gettext/import sections; `Chapter11/06_import_translation/my_hostel/i18n/nl_BE.po`; Cybrosys `internationalization*` pages | Separate extraction, catalog maintenance, language loading, overwrite policy and rendered output. Labels are implicitly exportable; record values need appropriate translation support. Literal format strings must remain extractable. A PO file is evidence of catalog content, not proof it was loaded, and the sample header identifies a pre-release export. Review fuzzy matches and preserve existing translations when updating source keys. | Added [translation lifecycle reference](../src/odoo_boost/skills/translation_edits/references/extraction-lifecycle.md), conditionally linked from the existing skill. The bounded translation-edit path remains intact. |
| SW-05 | Book prose: v19 export/import/gettext recipes | Copy versioned commands only after checking the official CLI contract. The v19 book mixes new `i18n export/import` commands with explanations of older flags; its prose also says an output extension must be CSV/PO/TGZ despite showing POT. Pinned official 19 CLI documents positional modules, POT output, one language for an explicit output, and explicit overwrite behavior. | Incorporated version selection and deliberate overwrite into the lifecycle reference. Storage-internal and exact UI claims from the book are excluded because they were not independently verified. |
| SW-06 | Official-only follow-up to translation/website review: pinned 19 website-theme translation chapter | Builder edits can create a distinct edited view, so source-view translations alone do not establish what the published site displays. Review the actual edited view and recheck translations after source-language edits. Frontend JS also needs translation-module exposure; marking a string alone does not prove availability. | Included in the lifecycle reference with explicit 19 evidence. No new claim that every edit in every release destroys all translations; inspect the specific view and target release. |
| SW-07 | Both: v15 report prose `OEBPS/B16119_12_Final_PD_ePub.xhtml` language/custom-data sections and `ch12/library_app/reports/`; v19 `Chapter12/10_qweb_report/my_hostel/` report files/model context | Design report data contract and rendering context together. Custom providers do not automatically receive document defaults unless returned explicitly. Template language and record language are separate: the v15 native-language wrapper sets `t-lang` but does not explicitly re-browse translated fields. The book prose misspells `partner_id` as `parter_id`; companion code uses the correct spelling. The v19 report uses `t-esc` on selection values, which is not the same presentation decision as field-widget label formatting. | Existing report skill confirmed, with new prose/code discrepancy and multilingual/selection-field scenarios retained in this note. Test HTML/PDF, translated data and multiple selected records independently. No unnecessary report-skill rewrite. |
| SW-08 | Both: Cybrosys 18 snippet/dynamic-snippet pages, including embedded XML/JS/Python | Saved text is not always a faithful runnable example. The static snippet contains a malformed heading close; the dynamic page has unscoped `sudo()` product reads and a hardcoded currency symbol. The saved JS card string has lost the HTML structure expected of a card. Consult original HTML/source before attributing missing markup to the author or copying the snippet. Escape dynamic output through the intended renderer and use website pricing/currency policy rather than a fixed symbol. | Research note and source-quality warning retained. Exact pricing API and currency conversion are not prescribed without source checks. Static issue observations are not claims of an executed exploit or rendering failure. |

## Official evidence and scope

Local pinned files supplied actual verification. Documentation revisions:

- Odoo 15: `f6b84ed59624ba8f0db2b1d0f7097e435550bb7e`.
- Odoo 17: `fbf3e3a6ef0bda7c30b28f213848deca17c2a872`.
- Odoo 18: `ca129a822019682bd32552e4cbabba2520d1308e`.
- Odoo 19: `de94dcddba224a1ece042792fa444e7ba0c31fdf`.

Representative exact supporting contracts:

- [19 builder block structure, editor option components/plugins and asset bundle](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/website_themes/building_blocks.rst).
- [19 module translation extraction, interpolation and frontend module exposure](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/translations.rst).
- [19 internationalization CLI](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/cli.rst).
- [19 edited website views and translation workflow](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/website_themes/translations.rst).
- [19 report data/translation contract](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/reports.rst) and [15 counterpart](https://github.com/odoo/documentation/blob/f6b84ed59624ba8f0db2b1d0f7097e435550bb7e/content/developer/reference/backend/reports.rst).
- [19 security contract](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/security.rst).
- [18 QWeb escaping contract](https://github.com/odoo/documentation/blob/ca129a822019682bd32552e4cbabba2520d1308e/content/developer/reference/frontend/qweb.rst).

Only the stated contracts and sample source mismatches were checked. Attempts to
fetch pinned website implementation through the web tool failed with cache misses;
the plugin discrepancy is therefore deliberately unresolved. The pinned docs
themselves include some older JS examples in the general translation chapter;
this review retains the literal/exposure principles, not a universal JS lazy-API
import prescription. No deployment, Odoo server, PO import, browser or PDF renderer
was started. Whole EPUB members stay partial when only named sections were read.

## Validation and next work

`tests/test_skills.py`: **35 passed** after linking the original lifecycle reference.
This verifies package skill loading/installation; it does not verify translation
import or website/report behavior. Source snippets remain unchanged as evidence.
The added reference uses official URLs and no local corpus dependencies.

Remaining: source-verify the v19 builder registry/resource discrepancy, inspect
original Cybrosys HTML where text loses markup, finish surrounding chapter/recipe
snapshots, and run public/editor/report-language cases on matching disposable
servers. Website builder, reporting and translation coverage has advanced; none
is certified exhaustive or runtime-validated by this batch.
