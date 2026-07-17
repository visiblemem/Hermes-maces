from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "LICENSE",
    "docs/SECURITY.md",
    "docs/INSTALLATION.md",
    "docs/ROLL_OUT.md",
    "docs/PUBLIC_RELEASE_GUIDE.md",
    "docs/PUBLIC_BETA_VALIDATION.md",
    "docs/releases/v1.2.0.md",
)

FORBIDDEN_TRACKED_PARTS = (
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "subconscious.db",
    "subconscious.db-wal",
    "subconscious.db-shm",
)

SCAN_EXCLUSIONS = {
    ".github/workflows/test.yml",
    "docs/PUBLIC_RELEASE_GUIDE.md",
    "scripts/check_public_boundary.py",
}

PRIVATE_PATH = re.compile(r"/Users/[^/\s]+/|[A-Za-z]:\\\\Users\\\\")
PRIVATE_KEY = re.compile(r"BEGIN\s+[^\n]*PRIVATE KEY")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> None:
    errors: list[str] = []

    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required release file: {relative}")

    if (ROOT / "config.yaml").exists():
        errors.append("repository-owned config.yaml is forbidden")
    if (ROOT / "data").exists():
        errors.append("repository data/ directory is forbidden")

    for relative in tracked_files():
        normalized = relative.replace("\\", "/")
        if normalized.endswith((".pyc", ".pyo")) or any(
            part in normalized for part in FORBIDDEN_TRACKED_PARTS
        ):
            errors.append(f"tracked local/runtime artifact: {relative}")

        path = ROOT / relative
        if not path.is_file():
            continue
        if normalized.startswith("tests/") or normalized in SCAN_EXCLUSIONS:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if PRIVATE_PATH.search(text):
            errors.append(f"possible private absolute user path in {relative}")
        if PRIVATE_KEY.search(text):
            errors.append(f"possible private-key material in {relative}")

    if errors:
        raise SystemExit("Public boundary contract failed:\n- " + "\n- ".join(errors))

    print("Public boundary contract passed")


if __name__ == "__main__":
    main()
