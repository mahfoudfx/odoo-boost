# Odoo Boost offline documentation packs

Optional text snapshots of the official Odoo documentation for 18.0, 19.0, and
20.0. They contain the `.rst` sources under `content/` (applications/user,
administration, and developer) and each branch's `LICENSE`. Images and built
HTML are not included. Odoo Boost expands only the selected version into its
shared documentation cache.

The source is [odoo/documentation](https://github.com/odoo/documentation).
Each archive's `manifest.json` records its Odoo series and upstream commit.
The documentation is licensed under CC BY-SA 4.0; see the `LICENSE` inside
each archive. The snapshots are separate from the core Odoo Boost wheel.

Install this package in the same VENV as Odoo Boost, then choose the packaged
snapshot in `odoo-boost install` or run `odoo-boost docs install --source packed`.
Builds are attached to Odoo Boost GitHub Releases; this package is not
published by the core PyPI release step.
