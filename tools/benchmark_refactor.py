"""Repeatable synthetic offline measurements; no Odoo or network access."""

import json
import os
from collections.abc import Callable
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any
from unittest.mock import patch

from odoo_boost import agents
from odoo_boost.agents import AGENTS
from odoo_boost.agents import files as agent_files
from odoo_boost.ast_scanner import analyzer
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection


def measured(operation: Callable[[], Any], repeats: int = 5) -> float:
    times = []
    for _ in range(repeats):
        start = perf_counter()
        operation()
        times.append((perf_counter() - start) * 1000)
    return round(median(times), 3)


with TemporaryDirectory(prefix="odoo-boost-benchmark-") as temporary:
    root = Path(temporary)
    addon = root / "addon"
    addon.mkdir()
    (addon / "__manifest__.py").write_text("{'name': 'Benchmark', 'version': '18.0'}")
    for index in range(20):
        folder = addon / f"part_{index}"
        folder.mkdir()
        for item in range(10):
            (folder / f"model_{item}.py").write_text(
                f"class Model:\n    _name = 'x.m{index}_{item}'\n"
            )
            (folder / f"view_{item}.xml").write_text(
                f'<odoo><record id="r{index}_{item}" model="ir.ui.view"/></odoo>'
            )
    for index in range(100):
        folder = addon / "build" / str(index)
        folder.mkdir(parents=True)
        for item in range(10):
            (folder / f"ignored_{item}.py").write_text("pass\n")

    analyzer.scan_addon_cached(addon)
    result = {"cached_scan_ms": measured(lambda: analyzer.scan_addon_cached(addon))}
    original_scandir = os.scandir
    with patch("os.scandir", wraps=original_scandir) as scandir:
        analyzer.scan_addon_cached(addon)
        result["cached_scan_directory_reads"] = scandir.call_count

    project = root / "project"
    project.mkdir()
    config = OdooBoostConfig(
        connection=OdooConnection(url="http://localhost:8069", database="benchmark"),
        project_path=str(project),
        odoo_version="18.0",
        agents=list(AGENTS),
    )

    def generate() -> None:
        install_batch = getattr(agents, "install_agents", None)
        if install_batch is None:
            for agent_class in AGENTS.values():
                agent_class(config, project).install()
        else:
            install_batch(config, project)

    generate()
    result["all_agents_update_ms"] = measured(generate)
    original_write = Path.write_text
    with (
        patch.object(Path, "write_text", autospec=True, side_effect=original_write) as write,
        patch.object(
            agent_files, "_write_private_config", wraps=agent_files._write_private_config
        ) as private,
    ):
        generate()
        result["all_agents_update_file_writes"] = write.call_count + private.call_count
    print(json.dumps(result, indent=2))
