"""Build a byte-identical, runtime-only Hermes distribution; never edits the source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MODULES = (
    "__init__", "engine", "feedback", "influence", "models", "plugin",
    "policy", "secure_store", "store", "validation",
)
RUNTIME_FILES = (
    "__init__.py", "plugin.yaml", "config.example.yaml", "LICENSE", "docs/SECURITY.md",
    *(f"src/maces/{name}.py" for name in MODULES),
)
README = """# MACES Hermes runtime distribution

Generated from the development repository; see SOURCE.json for the exact source
commit and SHA-256 of every shipped source file. Runtime code is copied unchanged.
Tests, CI, and build tooling remain in the development source commit, not here.

This is a Public Beta preview, not a stable release. Install one profile first.
Keep shadow_mode: true and learnable_tool_fields: {}. No automatic activation.
Observe for at least seven days and complete separate local validation before
considering advisory influence. Each profile owns its own data/maces database.

Operator commands: /maces-status, /maces-top, /maces-feedback.
Chinese feedback previews do not write preferences. Explicit confirmation is required.
MACES does not replace Hermes memory or Hindsight, and registers no model tools.

Use the native Hermes installer with a fixed commit and its security scan enabled.
Disabling hermes-maces through the native plugin registry removes its hooks on
the next runtime startup; preserve its database when diagnosing an issue.
"""


def build_runtime(source: Path, destination: Path, source_revision: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ValueError("source_revision must be a full lowercase Git commit SHA")
    source = source.resolve(strict=True)
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("destination must not exist; nothing will be overwritten")
    if destination.resolve().is_relative_to(source):
        raise ValueError("build outside the development checkout")
    actual_modules = {
        p.relative_to(source).as_posix() for p in (source / "src/maces").rglob("*.py")
    }
    expected_modules = {p for p in RUNTIME_FILES if p.startswith("src/maces/")}
    if actual_modules != expected_modules:
        raise ValueError("runtime module inventory changed; review the distribution manifest")
    payload = {}
    for relative in RUNTIME_FILES:
        path = source / relative
        if any(p.is_symlink() for p in (path, *path.parents) if p != source):
            raise ValueError("source symlinks are not supported")
        if not path.is_file() or not path.resolve().is_relative_to(source):
            raise ValueError(f"missing or invalid runtime source: {relative}")
        payload[relative] = path.read_bytes()
    provenance = {
        "format": 1,
        "repository": "https://github.com/visiblemem/Hermes-maces",
        "source_commit": source_revision,
        "files": {p: hashlib.sha256(data).hexdigest() for p, data in payload.items()},
    }
    destination.mkdir(parents=True, exist_ok=False)
    for relative, data in payload.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    (destination / "README.md").write_text(README, encoding="utf-8", newline="\n")
    (destination / "SOURCE.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n",
    )
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    build_runtime(args.source, args.destination, args.source_commit)
    print("Runtime distribution created; verify provenance, test, and scan before installation.")
