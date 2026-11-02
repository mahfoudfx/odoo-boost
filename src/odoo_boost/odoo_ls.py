"""Discovery and installation helpers for the official Odoo Language Server.

Odoo LS resolves its Python stubs from a ``typeshed`` directory next to its
(symlink-resolved) executable. Release archives ship only the executable; the
stubs come from the separate ``typeshed.zip`` asset of the same release. Without
them the server stops during initialization and reports no diagnostics, so an
install is only usable when both sit side by side.
"""

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
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

OFFICIAL_REPOSITORY = "https://github.com/odoo/odoo-ls"
_API_ROOT = "https://api.github.com/repos/odoo/odoo-ls/releases"
_DOWNLOAD_PREFIX = "https://github.com/odoo/odoo-ls/releases/download/"
_MAX_DOWNLOAD_BYTES = 250 * 1024 * 1024
TYPESHED_ASSET = "typeshed.zip"
# Marks a directory created by this installer; holds the installed release tag.
MANAGED_MARKER = ".odoo-boost-odoo-ls"
_TYPESHED_ROOTS = {"stdlib", "stubs"}


@dataclass(frozen=True)
class InstallResult:
    """Outcome of :func:`install_official_odoo_ls`."""

    path: Path
    tag: str
    changed: bool
    link: Path | None = None


def find_odoo_ls(configured: str | None = None) -> Path | None:
    """Find the server binary, preferring a usable install over a broken one.

    An explicit configured path always wins. Otherwise PATH candidates and the
    managed install are considered, and the first one with its typeshed stubs is
    returned; a stub-less binary is returned only when nothing usable exists, so
    callers can report it as broken.
    """
    if configured:
        candidate = Path(configured).expanduser()
        return candidate.resolve() if candidate.is_file() else None
    candidates: list[Path] = []
    for name in ("odoo_ls_server", "odoo_ls_server.exe", "odoo-ls"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found).resolve())
    managed = default_install_dir() / executable_name()
    if managed.is_file():
        candidates.append(managed.resolve())
    for candidate in candidates:
        if is_usable(candidate):
            return candidate
    return candidates[0] if candidates else None


def typeshed_dir(binary: Path) -> Path:
    """Return the stub directory Odoo LS loads for ``binary``."""
    return binary.resolve().parent / "typeshed"


def is_usable(binary: Path) -> bool:
    """Return True when the typeshed stdlib stubs sit next to ``binary``."""
    return (typeshed_dir(binary) / "stdlib" / "builtins.pyi").is_file()


def is_managed(binary: Path) -> bool:
    """Return True when ``binary`` lives in a directory created by this installer."""
    return (binary.resolve().parent / MANAGED_MARKER).is_file()


def installed_tag(install_dir: Path) -> str | None:
    """Return the release tag recorded in a managed install directory."""
    try:
        return (install_dir / MANAGED_MARKER).read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def executable_name() -> str:
    return "odoo_ls_server.exe" if platform.system() == "Windows" else "odoo_ls_server"


def default_install_dir() -> Path:
    """Directory holding the managed executable and its typeshed stubs."""
    if platform.system() == "Windows":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return root / "odoo-boost" / "odoo-ls"


def default_link_dir() -> Path | None:
    """User bin directory that receives a PATH symlink (none on Windows)."""
    if platform.system() == "Windows":
        return None
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


def latest_release_tag() -> str:
    """Return the tag of the latest stable official release."""
    tag = str(_read_json(f"{_API_ROOT}/latest").get("tag_name", ""))
    if not tag:
        raise RuntimeError("Official Odoo LS release metadata did not contain a tag")
    return tag


def install_official_odoo_ls(
    destination: Path | None = None,
    *,
    version: str | None = None,
    force: bool = False,
) -> InstallResult:
    """Install, upgrade or repair the official executable with its typeshed stubs.

    The managed directory is rebuilt atomically from the official release
    assets. An install already at the requested tag with its stubs is left as is
    unless ``force`` is set. A non-empty directory not created by this installer
    is never replaced. Without ``destination``, a user-bin symlink is also
    created on POSIX so the server is on PATH.
    """
    if version and not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Odoo LS version must be an exact release tag such as 1.6.1")
    release = _read_json(f"{_API_ROOT}/tags/{version}" if version else f"{_API_ROOT}/latest")
    tag = str(release.get("tag_name", ""))
    if not tag or (version and tag != version):
        raise RuntimeError("Official Odoo LS release metadata did not contain the expected tag")

    install_dir = (destination or default_install_dir()).expanduser().resolve()
    binary = install_dir / executable_name()
    if install_dir.is_dir() and any(install_dir.iterdir()) and installed_tag(install_dir) is None:
        raise FileExistsError(
            f"{install_dir} is not empty and was not created by Odoo Boost; "
            "choose another --destination"
        )
    if not force and installed_tag(install_dir) == tag and is_usable(binary):
        link = _link_on_path(binary) if destination is None else None
        return InstallResult(binary, tag, changed=False, link=link)

    asset_name = official_asset_name(tag)
    executable = _extract_executable(_download(_asset_url(release, asset_name)), asset_name)
    typeshed = _download(_asset_url(release, TYPESHED_ASSET))

    install_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{install_dir.name}-", dir=install_dir.parent))
    try:
        staged_binary = staging / executable_name()
        staged_binary.write_bytes(executable)
        staged_binary.chmod(
            staged_binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        _extract_typeshed(typeshed, staging / "typeshed")
        (staging / MANAGED_MARKER).write_text(f"{tag}\n", encoding="utf-8")
        _swap_directory(staging, install_dir)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    link = _link_on_path(binary) if destination is None else None
    return InstallResult(binary, tag, changed=True, link=link)


def _asset_url(release: dict[str, Any], name: str) -> str:
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise RuntimeError("Official Odoo LS release metadata did not contain assets")
    asset = next((item for item in assets if item.get("name") == name), None)
    if not isinstance(asset, dict):
        raise RuntimeError(
            f"Official Odoo LS release {release.get('tag_name')} has no asset {name}"
        )
    url = str(asset.get("browser_download_url", ""))
    if not url.startswith(_DOWNLOAD_PREFIX):
        raise RuntimeError("Refusing a release asset outside the official odoo/odoo-ls repository")
    return url


def _swap_directory(staging: Path, install_dir: Path) -> None:
    """Replace ``install_dir`` with ``staging``, keeping the old one until the swap."""
    if not install_dir.exists():
        staging.rename(install_dir)
        return
    retired = Path(tempfile.mkdtemp(prefix=f".{install_dir.name}-old-", dir=install_dir.parent))
    retired.rmdir()
    install_dir.rename(retired)
    try:
        staging.rename(install_dir)
    except OSError:
        retired.rename(install_dir)
        raise
    shutil.rmtree(retired, ignore_errors=True)


def _link_on_path(binary: Path) -> Path | None:
    """Point the user-bin entry at ``binary`` without shadowing a working foreign one.

    An existing entry is replaced only when it is unusable (for example a
    stub-less executable left by an older Odoo Boost) or already a symlink into
    the managed directory. Returns the link, or None when none was made.
    """
    link_dir = default_link_dir()
    if link_dir is None:
        return None
    link = link_dir / executable_name()
    target = binary.resolve()
    if link.is_symlink() or link.exists():
        current = link.resolve()
        if current == target:
            return link
        if is_usable(current) and not is_managed(current):
            return None
    link_dir.mkdir(parents=True, exist_ok=True)
    temporary = link_dir / f".{link.name}.{os.getpid()}.tmp"
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(target)
    os.replace(temporary, link)
    return link


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


def _extract_typeshed(payload: bytes, destination: Path) -> None:
    """Extract the stdlib/stubs trees of ``typeshed.zip`` into ``destination``.

    Members outside those trees are ignored; absolute or parent-relative paths
    and archives inflating past the size limit are rejected.
    """
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        if sum(info.file_size for info in members) > _MAX_DOWNLOAD_BYTES:
            raise RuntimeError("Odoo LS typeshed archive exceeded the size limit")
        for info in members:
            parts = PurePosixPath(info.filename.replace("\\", "/")).parts
            if parts and parts[0] == "typeshed":
                parts = parts[1:]
            if not parts or parts[0] not in _TYPESHED_ROOTS:
                continue
            if any(part in {"", ".", ".."} or ":" in part for part in parts):
                raise RuntimeError(f"Unsafe path in typeshed archive: {info.filename!r}")
            target = destination.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))
    if not (destination / "stdlib" / "builtins.pyi").is_file():
        raise RuntimeError("Official typeshed archive did not contain stdlib/builtins.pyi")


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
