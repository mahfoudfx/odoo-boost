# Translation extraction and loading

Use this procedure when source terms change, a module gains a language, or
translation extraction/loading itself is the task. A bounded translation-only
edit stays on the main skill's shorter path.

1. Identify the module, source occurrence, target language code and Odoo series.
   Separate a translated field's label from its record values: the label can be
   exported without `translate=True`; translatable record content needs the
   appropriate field declaration. In Python/JS, mark literal format strings and
   pass substitution values separately. Keep a sentence together for translators.
2. Export from the intended installed module and database. Retain a POT template
   and locale PO files under the module's `i18n/`. Compare the new source keys
   and references with existing entries before merging; preserve human translations
   and review fuzzy matches. A file's presence alone does not prove its terms are
   current or its language is loaded.
3. Validate syntax, placeholders, plural entries and the requested source terms.
   Where a PO compiler/parser is unavailable, report that limitation. Inspect a
   shared `msgid`'s source references before accepting one translation for all uses.
4. Establish how the matching release loads the file. Odoo 19 documents
   `odoo-bin i18n export <modules> --languages <codes>` and
   `odoo-bin i18n import <files> --language <code>`; import adds new entries by
   default and `--overwrite` replaces existing terms. Select overwrite deliberately
   after reviewing the affected terms. Check the installed command's help for
   other releases rather than copying 19 subcommands into an older deployment.
   Module install/update also loads translations for loaded languages.
5. Verify with a non-admin user in the target language and again in the source
   language. For website JS, confirm the module's translations are exposed to the
   frontend; `_t` calls alone do not establish that. For builder-edited pages,
   inspect the actual edited view and revisit translations after source-language
   edits. For reports, test template strings and translated record data separately:
   `t-lang` on the document call and record language context serve distinct purposes.

Completion: the intended terms are present, the catalog passes available checks,
and loading/rendering results are recorded separately. Offline validation is useful
evidence but does not establish that a database or browser loaded the translations.

Official contracts checked for Odoo 19:

- [Module translations](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/translations.rst)
- [Internationalization CLI](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/cli.rst)
- [Website translations and edited views](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/howtos/website_themes/translations.rst)
- [Translated report documents](https://github.com/odoo/documentation/blob/de94dcddba224a1ece042792fa444e7ba0c31fdf/content/developer/reference/backend/reports.rst)
