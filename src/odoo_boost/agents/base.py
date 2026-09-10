"""Abstract Agent base class."""

from __future__ import annotations

import json
import shutil
from abc import ABC
from pathlib import Path
from typing import Any

import yaml

from odoo_boost.agents.spec import AgentSpec
from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.guidelines.composer import compose_guidelines
from odoo_boost.mcp_launcher import build_http_url, build_stdio_command
from odoo_boost.skills.loader import install_skills


class Agent(ABC):
    """Base class for AI coding agent integrations.

    Subclasses only declare a class-level ``spec``; all paths and output
    serialization are derived from it:

    1. Guidelines file (markdown with dev instructions)
    2. MCP config file(s) so the agent can use odoo-boost MCP tools
    3. Skills directory (step-by-step guides for common tasks)
    """

    spec: AgentSpec
    id: str
    display_name: str

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        spec = cls.__dict__.get("spec")
        if spec is not None:
            cls.id = spec.id
            cls.display_name = spec.display_name

    def __init__(self, config: OdooBoostConfig, project_path: Path) -> None:
        if getattr(self, "spec", None) is None:
            raise TypeError("Agent subclasses must define a class-level 'spec'.")
        self.config = config
        self.project_path = project_path

    # -- public API ----------------------------------------------------------

    def install(self) -> list[Path]:
        """Generate all files for this agent. Returns paths created."""
        created: list[Path] = []
        if self.config.generate_ai_files:
            created.append(self._write_guidelines())
            created.extend(self._write_skills())
        if self.config.generate_mcp:
            created.extend(self._write_mcp_config())
        return created

    def uninstall(self) -> None:
        """Remove generated files (best-effort)."""
        for path in [self.guidelines_path, self.mcp_config_path, self.windows_mcp_config_path]:
            if path.is_file():
                path.unlink()
        if self.skills_dir.is_dir():
            shutil.rmtree(self.skills_dir)

    # -- paths derived from the spec -----------------------------------------

    @property
    def guidelines_path(self) -> Path:
        """Absolute path to the generated guidelines file."""
        return self.project_path.joinpath(*self.spec.guidelines_path)

    @property
    def mcp_config_path(self) -> Path:
        """Absolute path to the generated MCP config file."""
        return self.project_path.joinpath(*self.spec.mcp_config_path)

    @property
    def skills_dir(self) -> Path:
        """Absolute path to the skills directory."""
        return self.project_path.joinpath(*self.spec.skills_dir)

    @property
    def windows_mcp_config_path(self) -> Path:
        """Path to the Windows/WSL companion config (``*.windows.*``)."""
        path = self.mcp_config_path
        return path.with_name(f"{path.stem}.windows{path.suffix}")

    # -- helpers -------------------------------------------------------------

    def _should_emit_windows_variant(self) -> bool:
        """Emit a Windows companion when stdio runs through auto detection."""
        return (
            self.config.mcp_transport == "stdio"
            and self.config.mcp_target == "auto"
            and not self.config.mcp_command
            and self.mcp_config_path != self.windows_mcp_config_path
        )

    def _is_http(self) -> bool:
        return self.config.mcp_transport == "http"

    def _http_url(self) -> str:
        return build_http_url(self.config)

    def _mcp_command(self, *, windows: bool = False) -> list[str]:
        """Return the command to start the MCP server.

        Uses the full path to the current Python interpreter so the MCP
        server starts in the correct environment regardless of ``PATH``.
        For Windows targets it wraps the interpreter in ``wsl.exe`` so a
        Windows-native IDE can launch the WSL process.
        """
        return build_stdio_command(self.config, self.project_path, windows=windows)

    def _stdio_server_entry(self, windows: bool) -> dict[str, Any]:
        """Return a ``{command, args}`` mapping for stdio-based clients."""
        cmd = self._mcp_command(windows=windows)
        return {"command": cmd[0], "args": cmd[1:]}

    def _http_server_entry(self, *, server_type: str | None = None) -> dict[str, Any]:
        """Return a ``{url[, headers]}`` mapping for HTTP-based clients."""
        entry: dict[str, Any] = {"url": self._http_url()}
        if self.config.mcp_token:
            entry["headers"] = {"Authorization": f"Bearer {self.config.mcp_token}"}
        if server_type:
            entry = {"type": server_type, **entry}
        return entry

    def _write_guidelines(self) -> Path:
        """Compose and write the guidelines file."""
        content = compose_guidelines(self.config.odoo_version)
        if self.spec.cursor_rules:
            content = (
                "---\n"
                "description: Odoo development guidelines from Odoo Boost\n"
                "globs:\n"
                "alwaysApply: true\n"
                "---\n\n" + content
            )
        self.guidelines_path.parent.mkdir(parents=True, exist_ok=True)
        self.guidelines_path.write_text(content, encoding="utf-8")
        return self.guidelines_path

    def _mcp_config_content(self, *, windows: bool = False) -> str:
        """Serialize the MCP config using the format declared by the spec."""
        match self.spec.mcp_format:
            case "codex":
                return self._render_codex(windows)
            case "hermes":
                return self._render_hermes(windows)
            case "opencode":
                return self._render_opencode(windows)
            case _:
                return self._render_json(windows)

    def _render_json(self, windows: bool) -> str:
        """Render the generic JSON format (``mcpServers`` or VS Code ``servers``)."""
        server = (
            self._http_server_entry(server_type="http")
            if self._is_http()
            else self._stdio_server_entry(windows)
        )
        if self.spec.mcp_format == "vscode":
            return json.dumps({"servers": {"odoo-boost": server}}, indent=2) + "\n"
        return json.dumps({"mcpServers": {"odoo-boost": server}}, indent=2) + "\n"

    def _render_opencode(self, windows: bool) -> str:
        if self._is_http():
            server = {"enabled": True, **self._http_server_entry(server_type="remote")}
        else:
            server = {"type": "local", "command": self._mcp_command(windows=windows)}
        return json.dumps({"mcp": {"odoo-boost": server}}, indent=2) + "\n"

    def _render_hermes(self, windows: bool) -> str:
        server = self._http_server_entry() if self._is_http() else self._stdio_server_entry(windows)
        return str(
            yaml.dump(
                {"mcp_servers": {"odoo-boost": server}},
                default_flow_style=False,
                sort_keys=False,
            )
        )

    def _render_codex(self, windows: bool) -> str:
        header = "# Odoo Boost MCP configuration for Codex\n[mcp_servers.odoo-boost]\n"
        if self._is_http():
            lines = [f'url = "{self._http_url()}"']
            if self.config.mcp_token:
                bearer = _toml_escape(f"Bearer {self.config.mcp_token}")
                lines.append(f'http_headers = {{ Authorization = "{bearer}" }}')
            return header + "\n".join(lines) + "\n"
        cmd = self._mcp_command(windows=windows)
        args_toml = ", ".join(f'"{_toml_escape(a)}"' for a in cmd[1:])
        return f'{header}command = "{_toml_escape(cmd[0])}"\nargs = [{args_toml}]\n'

    def _write_mcp_config(self) -> list[Path]:
        """Write the MCP config file(s) for this agent."""
        return self.write_all_mcp_configs()

    def write_all_mcp_configs(self) -> list[Path]:
        """Write the primary config plus the Windows companion when applicable."""
        created = [self.write_mcp_config()]
        if self._should_emit_windows_variant():
            created.append(self.write_windows_mcp_config())
        return created

    def write_mcp_config(self) -> Path:
        """Write the primary MCP config file."""
        return self._write_text(self.mcp_config_path, self._mcp_config_content())

    def write_windows_mcp_config(self) -> Path:
        """Write the ``wsl.exe`` companion config for Windows-native IDEs."""
        return self._write_text(
            self.windows_mcp_config_path,
            self._mcp_config_content(windows=True),
        )

    def _write_text(self, path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _write_skills(self) -> list[Path]:
        """Install skill files into the skills directory."""
        return install_skills(self.skills_dir)


def _toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
