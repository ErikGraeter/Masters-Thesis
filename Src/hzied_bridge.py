"""Bridge between the thesis Document repository and the HZIED analysis
repository.

Importing this module has two side effects:

1. Adds ``$HZIED_ROOT/src`` to ``sys.path`` so figure scripts can
   ``from pipeline import run_hzied_analysis``.
2. By default, applies the thesis Matplotlib style
   (``thesis.mplstyle`` in the Document root) to the HZIED plotting
   module, so figures produced through the pipeline render in the same
   fonts (Palatino via ``newpxtext``/``newpxmath``, LaTeX-rendered) as
   the thesis body text.

To use HZIED's own notebook-style rendering instead (STIX serif,
matplotlib-native, no LaTeX pass), call
``hzied_bridge.use_hzied_native_style()`` after importing the module.

Environment
-----------
Set ``HZIED_ROOT`` to override the default HZIED location
(``$HOME/Thesis/HZIED``). Useful for running on another machine.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
DOC_ROOT = Path(__file__).resolve().parents[1]

HZIED_ROOT = Path(
    os.environ.get("HZIED_ROOT", Path.home() / "Thesis" / "HZIED")
).resolve()

_hzied_src = HZIED_ROOT / "src"
if not (_hzied_src / "pipeline.py").exists():
    raise RuntimeError(
        f"HZIED pipeline not found at {_hzied_src / 'pipeline.py'}.\n"
        f"Set the HZIED_ROOT environment variable to the HZIED repository "
        f"root (currently resolves to {HZIED_ROOT})."
    )

# ---------------------------------------------------------------------------
# Extend sys.path
# Append (not prepend) so the Document Src/ modules take precedence over
# any same-named modules inside HZIED/src.
# ---------------------------------------------------------------------------
_hzied_src_str = str(_hzied_src)
if _hzied_src_str not in sys.path:
    sys.path.append(_hzied_src_str)

# ---------------------------------------------------------------------------
# Style paths
# ---------------------------------------------------------------------------
THESIS_STYLE = DOC_ROOT / "thesis.mplstyle"
HZIED_NATIVE_STYLE = HZIED_ROOT / "src" / "thesis.mplstyle"


def use_thesis_style() -> None:
    """Use the thesis Matplotlib style (Palatino via LaTeX)."""
    import plotting as _hz_plotting  # HZIED's plotting module
    _hz_plotting.THESIS_STYLE = THESIS_STYLE


def use_hzied_native_style() -> None:
    """Use HZIED's own notebook style (STIX serif, matplotlib-native)."""
    import plotting as _hz_plotting
    _hz_plotting.THESIS_STYLE = HZIED_NATIVE_STYLE


# ---------------------------------------------------------------------------
# Default behaviour on import: apply the thesis style, unless the
# ``HZIED_USE_NATIVE_STYLE`` environment variable is set.
# ---------------------------------------------------------------------------
if os.environ.get("HZIED_USE_NATIVE_STYLE"):
    use_hzied_native_style()
elif THESIS_STYLE.exists():
    use_thesis_style()
