"""Conservative updates to agent files shared with user configuration."""

from __future__ import annotations

import hashlib
import importlib.resources
import json
import re
from pathlib import Path
from typing import Any

import yaml

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from odoo_boost.guidelines import composer
from odoo_boost.skills.loader import (
    generate_skills_routing,
    list_skills,
    load_skill_files,
    skill_id,
)

_TOML_TABLE = re.compile(r"(?m)^\[([^\]\n]+)\][ \t]*(?:\n|$)")
_GUIDE_BLOCK = re.compile(
    r"(?ms)^<!-- odoo-boost:start sha256=([0-9a-f]{64}) -->\n(.*?)"
    r"^<!-- odoo-boost:end -->\n?"
)
_CURSOR_FRONTMATTER = (
    "---\ndescription: Odoo development guidelines from Odoo Boost\nglobs:\nalwaysApply: true\n---"
)


def assert_safe_path(path: Path, root: Path) -> None:
    """Reject symlinked output paths and parents below the project root."""
    root = root.resolve()
    path = path.absolute()
    if not path.is_relative_to(root):
        raise ValueError(f"Generated path is outside project: {path}")
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"Generated path uses a symlink: {current}")
        current = current.parent


def _guide_block(content: str) -> str:
    content = content.rstrip() + "\n"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return (
        f"<!-- odoo-boost:start sha256={digest} -->\n{content.rstrip()}\n<!-- odoo-boost:end -->\n"
    )


def update_guidelines(
    path: Path, content: str, *, legacy: str | None = None, remove: bool = False
) -> bool:
    """Replace/remove only an unchanged generated section of an instructions file."""
    generated_frontmatter = re.match(r"\A(---\n.*?\n---\n)", content, re.DOTALL)
    body_content = (
        content[generated_frontmatter.end() :].lstrip("\n") if generated_frontmatter else content
    )
    if not path.exists():
        if remove:
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        prefix = generated_frontmatter.group(1) + "\n" if generated_frontmatter else ""
        path.write_text(prefix + _guide_block(body_content), encoding="utf-8")
        return True
    original = path.read_text(encoding="utf-8")
    match = _GUIDE_BLOCK.search(original)
    if match:
        body = match.group(2)
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != match.group(1):
            return False  # User edited the generated section.
        updated = original[: match.start()] + original[match.end() :]
    elif legacy is not None and original in (legacy, content):
        updated = ""
    else:
        updated = original
        if remove:
            return False
    if not remove:
        block = _guide_block(body_content)
        # Cursor rules require YAML frontmatter as the first document section.
        frontmatter = re.match(r"\A(---\n.*?\n---\n)", updated, re.DOTALL)
        if frontmatter:
            offset = frontmatter.end()
            updated = updated[:offset].rstrip() + "\n\n" + block + updated[offset:].lstrip("\n")
        else:
            prefix = (
                generated_frontmatter.group(1).rstrip() + "\n\n" if generated_frontmatter else ""
            )
            updated = prefix + updated.rstrip() + ("\n\n" if updated.strip() else "") + block
    elif updated.strip() in (
        generated_frontmatter.group(1).strip() if generated_frontmatter else "",
        _CURSOR_FRONTMATTER,
    ):
        updated = ""
    if updated == original:
        return False
    if remove and not updated.strip():
        path.unlink()
    else:
        path.write_text(updated, encoding="utf-8")
    return True


def update_mcp_config(path: Path, content: str, fmt: str, *, remove: bool = False) -> bool:
    """Update only the Odoo Boost server; reject malformed existing configuration.

    Returns whether a file was changed. An empty config is removed on uninstall.
    """
    if not path.exists():
        if remove:
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True
    original = path.read_text(encoding="utf-8")
    if fmt == "codex":
        # Keep unrelated TOML text, including comments and formatting, intact.
        try:
            parsed_original = tomllib.loads(original)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(f"Invalid TOML MCP config: {path}") from exc
        matches = list(_TOML_TABLE.finditer(original))
        start = end = None
        for index, match in enumerate(matches):
            if match.group(1).strip() == "mcp_servers.odoo-boost":
                start = match.start()
                end = matches[index + 1].start() if index + 1 < len(matches) else len(original)
                break
        server_data = parsed_original.get("mcp_servers", {}).get("odoo-boost")
        if server_data is not None and (
            start is None
            or any(
                match.group(1).strip().startswith("mcp_servers.odoo-boost.") for match in matches
            )
        ):
            raise ValueError(
                f"Unsupported Odoo Boost TOML table layout in {path}; "
                "use a single [mcp_servers.odoo-boost] table before regenerating."
            )
        if start is not None and end is not None:
            updated = original[:start].rstrip() + "\n" + original[end:]
            updated = updated.replace("# Odoo Boost MCP configuration for Codex\n", "", 1)
        else:
            updated = original
        if not remove:
            updated = updated.rstrip() + "\n\n" + content.strip() + "\n"
        try:
            parsed_updated = tomllib.loads(updated)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(f"Cannot safely update TOML MCP config: {path}") from exc
        expected_servers = dict(parsed_original.get("mcp_servers", {}))
        if remove:
            expected_servers.pop("odoo-boost", None)
        else:
            expected_servers["odoo-boost"] = tomllib.loads(content)["mcp_servers"]["odoo-boost"]
        if parsed_updated.get("mcp_servers", {}) != expected_servers:
            raise ValueError(f"Cannot preserve TOML MCP server mapping: {path}")
        if updated == original:
            return False
        if remove and not updated.strip():
            path.unlink()
        else:
            path.write_text(updated, encoding="utf-8")
        return True

    try:
        data: Any = yaml.safe_load(original) if fmt == "hermes" else json.loads(original)
        fresh: Any = (
            (yaml.safe_load(content) if fmt == "hermes" else json.loads(content))
            if not remove
            else None
        )
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid MCP config: {path}") from exc
    key = (
        "mcp_servers"
        if fmt == "hermes"
        else "mcp"
        if fmt == "opencode"
        else "servers"
        if fmt == "vscode"
        else "context_servers"
        if fmt == "zed"
        else "mcpServers"
    )
    if not isinstance(data, dict) or (key in data and not isinstance(data[key], dict)):
        raise ValueError(f"Invalid MCP server mapping: {path}")
    servers = data.get(key, {})
    if remove:
        if "odoo-boost" not in servers:
            return False
        del servers["odoo-boost"]
        if not servers:
            data.pop(key, None)
    else:
        data.setdefault(key, {})["odoo-boost"] = fresh[key]["odoo-boost"]
    if remove and not data:
        path.unlink()
    else:
        rendered = (
            yaml.safe_dump(data, sort_keys=False)
            if fmt == "hermes"
            else json.dumps(data, indent=2) + "\n"
        )
        path.write_text(rendered, encoding="utf-8")
    return True


def remove_generated_skills(skills_dir: Path) -> list[Path]:
    """Delete unchanged packaged files, preserving custom and edited skill content."""
    removed: list[Path] = []
    expected = {
        skills_dir / skill_id(name) / relative: content
        for name in list_skills()
        for relative, content in load_skill_files(name).items()
    }
    expected[skills_dir / "SKILLS_ROUTING.md"] = generate_skills_routing()
    reference_dir = skills_dir / "guidelines"
    for filename in composer._CORE_FILES:
        expected[reference_dir / filename] = composer._read_resource(filename)
    # The packaged version notes are discovered from resources, not the active config.
    versions = importlib.resources.files("odoo_boost.guidelines") / "core" / "versions"
    for version in versions.iterdir():
        if version.name.endswith(".md"):
            expected[reference_dir / "versions" / version.name] = version.read_text(
                encoding="utf-8"
            )
    for path, content in expected.items():
        if path.is_symlink() or any(
            parent.is_symlink() for parent in path.parents if parent != skills_dir.parent
        ):
            continue
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            path.unlink()
            removed.append(path)
    for directory in (
        sorted(
            (p for p in skills_dir.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        )
        if skills_dir.is_dir()
        else []
    ):
        if not directory.is_symlink() and not any(directory.iterdir()):
            directory.rmdir()
    if skills_dir.is_dir() and not any(skills_dir.iterdir()):
        skills_dir.rmdir()
        removed.append(skills_dir)
    return removed
