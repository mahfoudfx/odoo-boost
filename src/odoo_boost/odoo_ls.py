"""Discovery and installation helpers for the official Odoo Language Server."""

from __future__ import annotations

import io
import json
import os
import platform
import re
import shutil
import stat
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

OFFICIAL_REPOSITORY = "https://github.com/odoo/odoo-ls"
_API_ROOT = "https://api.github.com/repos/odoo/odoo-ls/releases"
_MAX_DOWNLOAD_BYTES = 250 * 1024 * 1024


def find_odoo_ls(configured: str | None = None) -> Path | None:
    """Find the official server binary, honoring an explicit configured path."""
    if configured:
        candidate = Path(configured).expanduser()
        return candidate.resolve() if candidate.is_file() else None
    for name in ("odoo_ls_server", "odoo_ls_server.exe", "odoo-ls"):
        found = shutil.which(name)
        if found:
            return Path(found).resolve()
    managed = default_install_dir() / executable_name()
    return managed.resolve() if managed.is_file() else None


def executable_name() -> str:
    return "odoo_ls_server.exe" if platform.system() == "Windows" else "odoo_ls_server"


def default_install_dir() -> Path:
    if platform.system() == "Windows":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "odoo-boost" / "bin"
    return Path.home() / ".local" / "bin"


def official_asset_name(tag: str) -> str:
    """Return the exact asset name produced by the official release workflow."""
    system = platform.system()
    machine = platform.machine().lower()
    arch = "aarch64" if machine in {"aarch64", "arm64"} else "x86_64"
    if machine not in {"aarch64", "arm64", "x86_64", "amd64"}:
        raise RuntimeError(f"Odoo LS has no supported release asset for architecture {machine!r}")
    if system == "Linux":
        target, suffix = "linux", ".tar.gz"
    elif system == "Darwin":
        target, suffix = "darwin", ".tar.gz"
    elif system == "Windows":
        target, suffix = "win32", ".zip"
    else:
        raise RuntimeError(f"Odoo LS has no supported release asset for {system!r}")
    return f"odoo-{target}-{arch}-{tag}{suffix}"


def install_official_odoo_ls(
    destination: Path | None = None,
    *,
    version: str | None = None,
    force: bool = False,
) -> tuple[Path, str]:
    """Download and install an official GitHub release asset atomically."""
    if version and not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Odoo LS version must be an exact release tag such as 1.4.0")
    release = _read_json(f"{_API_ROOT}/tags/{version}" if version else f"{_API_ROOT}/latest")
    tag = str(release.get("tag_name", ""))
    if not tag or (version and tag != version):
        raise RuntimeError("Official Odoo LS release metadata did not contain the expected tag")
    expected = official_asset_name(tag)
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise RuntimeError("Official Odoo LS release metadata did not contain assets")
    asset = next((item for item in assets if item.get("name") == expected), None)
    if not isinstance(asset, dict):
        raise RuntimeError(f"Official Odoo LS release {tag} has no asset {expected}")
    url = str(asset.get("browser_download_url", ""))
    if not url.startswith("https://github.com/odoo/odoo-ls/releases/download/"):
        raise RuntimeError("Refusing a release asset outside the official odoo/odoo-ls repository")

    install_dir = (destination or default_install_dir()).expanduser().resolve()
    target = install_dir / executable_name()
    if target.exists() and not force:
        raise FileExistsError(f"{target} already exists; pass --force to replace it")
    archive = _download(url)
    executable = _extract_executable(archive, expected)
    install_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=install_dir, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(executable)
    temporary.chmod(temporary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    temporary.replace(target)
    return target, tag


def _read_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "odoo-boost"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310
        payload = response.read(_MAX_DOWNLOAD_BYTES + 1)
    if len(payload) > _MAX_DOWNLOAD_BYTES:
        raise RuntimeError("Odoo LS release metadata exceeded the download limit")
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise RuntimeError("Invalid Odoo LS release metadata")
    return value


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "odoo-boost"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        payload = response.read(_MAX_DOWNLOAD_BYTES + 1)
    if len(payload) > _MAX_DOWNLOAD_BYTES:
        raise RuntimeError("Odoo LS release asset exceeded the 250 MiB limit")
    return bytes(payload)


def _extract_executable(payload: bytes, asset_name: str) -> bytes:
    expected = executable_name()
    if asset_name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            zip_matches = [name for name in archive.namelist() if Path(name).name == expected]
            if len(zip_matches) != 1:
                raise RuntimeError(f"Official archive did not contain exactly one {expected}")
            executable = bytes(archive.read(zip_matches[0]))
            if len(executable) > _MAX_DOWNLOAD_BYTES:
                raise RuntimeError("Odoo LS executable exceeded the size limit")
            return executable
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        tar_matches = [
            member for member in archive.getmembers() if Path(member.name).name == expected
        ]
        if len(tar_matches) != 1 or not tar_matches[0].isfile():
            raise RuntimeError(f"Official archive did not contain exactly one {expected}")
        extracted = archive.extractfile(tar_matches[0])
        if extracted is None:
            raise RuntimeError(f"Could not read {expected} from official archive")
        executable = extracted.read(_MAX_DOWNLOAD_BYTES + 1)
        if len(executable) > _MAX_DOWNLOAD_BYTES:
            raise RuntimeError("Odoo LS executable exceeded the size limit")
        return executable
