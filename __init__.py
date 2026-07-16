"""Hermes MACES plugin entrypoint."""
from pathlib import Path
import sys

_SRC = Path(__file__).parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from maces.plugin import register  # noqa: E402,F401
