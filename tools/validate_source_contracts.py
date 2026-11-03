"""Run original learning contract tests on a disposable local Odoo database.

This does not install book addons. It uses an existing Odoo source checkout and
PostgreSQL binaries, writes all runtime state under a fresh /tmp directory, and
stops its own PostgreSQL process on exit. No user Odoo configuration is loaded.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MODEL = """from odoo import api, fields, models


class Document(models.Model):
    _name = "learning.document"
    _description = "Disposable learning document"
    name = fields.Char(required=True)
    owner_id = fields.Many2one("res.users", required=True)


class Line(models.Model):
    _name = "learning.line"
    _description = "Disposable learning line"
    name = fields.Char(required=True)
    document_id = fields.Many2one("learning.document", required=True)


class Summary(models.AbstractModel):
    _name = "report.learning_contracts.summary"
    _description = "Disposable custom rendering context"

    @api.model
    def _get_report_values(self, docids, data=None):
        return {"lines": self.env["learning.document"].browse(docids)}
"""

TESTS = """from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class LearningContracts(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Learning ordinary user", "login": "learning_ordinary",
            "groups_id": [Command.set([cls.env.ref("base.group_user").id])],
        })
        cls.documents = cls.env["learning.document"].create([
            {"name": "OWN <document>", "owner_id": cls.user.id},
            {"name": "OTHER document", "owner_id": cls.env.ref("base.user_admin").id},
        ])
        cls.env["learning.line"].create([
            {"name": "Own line", "document_id": cls.documents[0].id},
            {"name": "Other line", "document_id": cls.documents[1].id},
        ])

    def test_parent_rule_does_not_restrict_child_query(self):
        documents = self.env["learning.document"].with_user(self.user)
        lines = self.env["learning.line"].with_user(self.user)
        self.assertEqual(documents.search_count([]), 1)
        self.assertEqual(lines.search_count([]), 2)
        self.env["ir.rule"].create({
            "name": "Learning child owner policy", "model_id":
                self.env["ir.model"]._get_id("learning.line"),
            "domain_force": "[('document_id.owner_id', '=', user.id)]",
            "groups": [Command.link(self.env.ref("base.group_user").id)],
        })
        self.assertEqual(lines.search_count([]), 1)

    def test_custom_report_context_and_escaped_html(self):
        report = self.env.ref("learning_contracts.action_summary")
        renderer = self.env["ir.actions.report"]
        context = renderer._get_rendering_context(report, self.documents.ids, {})
        self.assertIn("lines", context)
        for key in ("docs", "doc_model", "doc_ids"):
            self.assertNotIn(key, context)
        html, output = renderer._render_qweb_html(report.id, self.documents.ids)
        self.assertEqual(output, "html")
        self.assertIn(b"OWN &lt;document&gt;", html)
        self.assertIn(b"OTHER document", html)
        self.assertNotIn(b"OWN <document>", html)
"""

DATA = """<odoo>
    <record id="document_owner_rule" model="ir.rule">
        <field name="name">Learning document owner policy</field>
        <field name="model_id" ref="model_learning_document"/>
        <field name="domain_force">[("owner_id", "=", user.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
    <record id="action_summary" model="ir.actions.report">
        <field name="name">Learning summary</field>
        <field name="model">learning.document</field>
        <field name="report_type">qweb-html</field>
        <field name="report_name">learning_contracts.summary</field>
    </record>
    <template id="summary">
        <div><p t-foreach="lines" t-as="line"><t t-out="line.name"/></p></div>
    </template>
</odoo>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--odoo-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.odoo_root.resolve()
    if not (source / "odoo-bin").is_file():
        parser.error("--odoo-root must contain odoo-bin")
    work = Path(tempfile.mkdtemp(prefix="odoo-boost-learning-", dir="/tmp"))
    cluster, socket, addons = work / "postgres", work / "socket", work / "addons"
    socket.mkdir(mode=0o700)
    addon = addons / "learning_contracts"
    (addon / "tests").mkdir(parents=True)
    files = {
        "__init__.py": "from . import models\nfrom . import tests\n",
        "models.py": MODEL,
        "tests/__init__.py": "from . import test_contracts\n",
        "tests/test_contracts.py": TESTS,
        "data.xml": DATA,
        "ir.model.access.csv": (
            "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
            "document_read,Learning document read,model_learning_document,base.group_user,1,0,0,0\n"
            "line_read,Learning line read,model_learning_line,base.group_user,1,0,0,0\n"
        ),
        "__manifest__.py": repr(
            {
                "name": "Disposable learning contracts",
                "version": "18.0.1.0.0",
                "license": "LGPL-3",
                "depends": ["base"],
                "data": ["ir.model.access.csv", "data.xml"],
                "installable": True,
            }
        )
        + "\n",
    }
    for name, text in files.items():
        if name.endswith(".py"):
            compile(text, name, "exec")
        (addon / name).write_text(text)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    started = False
    result = {"work_dir": str(work), "odoo_root": str(source), "expected_tests": 2}
    print(f"Artifacts: {work}", flush=True)
    try:
        with (work / "initdb.log").open("w") as log:
            subprocess.run(
                ["initdb", "-D", str(cluster), "--auth=trust", "--no-locale", "-E", "UTF8"],
                check=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
            )
        subprocess.run(
            [
                "pg_ctl",
                "-D",
                str(cluster),
                "-l",
                str(work / "postgres.log"),
                "-o",
                f"-k {socket} -p 55439 -h ''",
                "-w",
                "start",
            ],
            check=True,
            env=env,
        )
        started = True
        cmd = [
            sys.executable,
            str(source / "odoo-bin"),
            "-c",
            "/dev/null",
            "--addons-path",
            f"{source / 'addons'},{source / 'odoo/addons'},{addons}",
            "--data-dir",
            str(work / "data"),
            "--db_host",
            str(socket),
            "--db_port",
            "55439",
            "--db_user",
            getpass.getuser(),
            "-d",
            "learning_contracts",
            "-i",
            "learning_contracts",
            "--without-demo",
            "all",
            "--no-http",
            "--workers",
            "0",
            "--test-enable",
            "--test-tags",
            "/learning_contracts",
            "--stop-after-init",
            "--logfile",
            str(work / "odoo.log"),
        ]
        result["command"] = cmd
        completed = subprocess.run(cmd, env=env, timeout=240)
        result["exit_code"] = completed.returncode
        log_text = (work / "odoo.log").read_text()
        summary = re.search(r"(\d+) failed, (\d+) error\(s\) of (\d+) tests", log_text)
        if summary:
            failures, errors, tests = map(int, summary.groups())
            result.update(failures=failures, errors=errors, tests_executed=tests)
            verified = failures == errors == 0 and tests == result["expected_tests"]
        else:
            verified = False
        result["expected_tests_verified"] = verified
        return completed.returncode or (0 if verified else 1)
    finally:
        if started:
            stopped = subprocess.run(["pg_ctl", "-D", str(cluster), "-m", "fast", "-w", "stop"])
            result["postgres_stop_exit_code"] = stopped.returncode
        (work / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"Result: {work / 'result.json'}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
