from pathlib import Path

import pytest

from build_runtime import build_runtime

pytestmark = pytest.mark.e2e


def test_distribution_passes_unmodified_native_plugin_guard(tmp_path):
    guard = pytest.importorskip("tools.plugin_guard")
    target = tmp_path / "runtime"
    build_runtime(Path(__file__).resolve().parents[2], target, "a" * 40)
    result = guard.scan_plugin(target, source="visiblemem/Hermes-maces")
    assert result.verdict == "safe", guard.format_scan_report(result)
    assert result.findings == []
