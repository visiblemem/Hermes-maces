from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from build_runtime import RUNTIME_FILES, build_runtime

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40


def test_runtime_is_complete_byte_identical_and_deterministic(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    provenance = build_runtime(ROOT, first, REVISION)
    build_runtime(ROOT, second, REVISION)
    files = {p.relative_to(first).as_posix() for p in first.rglob("*") if p.is_file()}
    assert files == set(RUNTIME_FILES) | {"README.md", "SOURCE.json"}
    assert provenance == json.loads((first / "SOURCE.json").read_text())
    for name in RUNTIME_FILES:
        assert (ROOT / name).read_bytes() == (first / name).read_bytes()
        assert provenance["files"][name] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    for name in files:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert not (first / "tests").exists()
    assert not (first / "config.yaml").exists()


def test_existing_destination_is_never_overwritten(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    marker = target / "user.txt"
    marker.write_text("preserve")
    with pytest.raises(FileExistsError):
        build_runtime(ROOT, target, REVISION)
    assert marker.read_text() == "preserve"


@pytest.mark.parametrize("revision", ["main", "a" * 7, "g" * 40, "A" * 40, ""])
def test_revision_must_be_immutable(tmp_path, revision):
    with pytest.raises(ValueError):
        build_runtime(ROOT, tmp_path / "runtime", revision)
    assert not (tmp_path / "runtime").exists()


def test_unreviewed_module_is_not_silently_omitted(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(ROOT / "src", source / "src")
    (source / "src/maces/additional.py").write_text("# review this module\n")
    with pytest.raises(ValueError, match="inventory changed"):
        build_runtime(source, tmp_path / "runtime", REVISION)
    assert not (tmp_path / "runtime").exists()


def test_output_inside_source_is_rejected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ValueError, match="outside"):
        build_runtime(source, source / "runtime", REVISION)


def test_missing_source_does_not_leave_partial_artifact(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(ROOT / "src", source / "src")
    with pytest.raises(ValueError, match="missing"):
        build_runtime(source, tmp_path / "runtime", REVISION)
    assert not (tmp_path / "runtime").exists()


def test_source_symlink_is_rejected(tmp_path):
    source = tmp_path / "source"
    for name in RUNTIME_FILES:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    target = source / "LICENSE"
    target.unlink()
    try:
        target.symlink_to(ROOT / "LICENSE")
    except OSError:
        pytest.skip("creating symlinks is unavailable on this host")
    with pytest.raises(ValueError, match="symlinks"):
        build_runtime(source, tmp_path / "runtime", REVISION)
    assert not (tmp_path / "runtime").exists()
