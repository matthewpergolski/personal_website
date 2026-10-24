"""Keep the deployed lockfile above the versions that fix known advisories."""

import tomllib
from pathlib import Path

from packaging.version import Version

LOCKFILE = Path(__file__).resolve().parent.parent / "uv.lock"

# Lowest version with no known advisory (pip-audit, 2026-10-23).
MINIMUM_VERSIONS = {
    "anyio": "4.14.2",
    "idna": "3.15",
    "oauthlib": "4.0.0",
    "pillow": "13.0.0",
    "python-dotenv": "1.2.2",
    "python-multipart": "0.0.31",
    "soupsieve": "2.9.0",
    "starlette": "1.3.1",
}


def locked_versions() -> dict[str, Version]:
    lock = tomllib.loads(LOCKFILE.read_text())
    return {p["name"]: Version(p["version"]) for p in lock["package"]}


def test_locked_packages_are_at_or_above_fixed_versions():
    locked = locked_versions()
    too_old = {
        name: f"{locked[name]} < {minimum}"
        for name, minimum in MINIMUM_VERSIONS.items()
        if name in locked and locked[name] < Version(minimum)
    }
    assert too_old == {}
