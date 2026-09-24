"""Build a reproducible text-only Odoo documentation pack from a checkout."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def _write(zip_file: ZipFile, name: str, data: bytes) -> None:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zip_file.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)


def build_pack(checkout: Path, series: str, output: Path) -> tuple[int, str]:
    content = checkout / "content"
    license_file = checkout / "LICENSE"
    if not content.is_dir() or not license_file.is_file():
        raise ValueError("Checkout must contain content/ and LICENSE")
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    branch = subprocess.check_output(
        ["git", "-C", str(checkout), "branch", "--show-current"], text=True
    ).strip()
    if branch and branch != series:
        raise ValueError(f"Checkout branch {branch} does not match Odoo {series}")
    pages = sorted(content.rglob("*.rst"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w") as archive:
        manifest = {
            "series": series,
            "revision": revision,
            "source": "https://github.com/odoo/documentation",
            "format": "rst-text-v1",
            "page_count": len(pages),
        }
        _write(archive, "manifest.json", json.dumps(manifest, sort_keys=True).encode())
        _write(archive, "LICENSE", license_file.read_bytes())
        for page in pages:
            _write(archive, page.relative_to(checkout).as_posix(), page.read_bytes())
    return len(pages), revision


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("series")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    count, commit = build_pack(args.checkout, args.series, args.output)
    print(f"{args.series}: {count} pages, revision {commit}, {args.output.stat().st_size} bytes")
