"""Test rendering of the Section 6.1 reproduction figure in HZIED's native
notebook style (STIX serif, matplotlib-native --- no LaTeX pass).

Otherwise identical to ``generic_reproduction.py``; provided for a
side-by-side comparison of the two style choices.  Output:
``Figures/generated/generic_reproduction_native.pdf``.
"""

from __future__ import annotations

# Make Src/ importable when this file is run directly.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hzied_bridge                                              # noqa: E402
hzied_bridge.use_hzied_native_style()                            # opt out of thesis fonts

from pipeline import run_hzied_analysis                          # noqa: E402
from utils import save_figure                                    # noqa: E402


def main() -> None:
    fig, _ax, _results = run_hzied_analysis(
        sample           = "generic",
        N                = 500,
        S_thresh         = 280.0,
        wrr              = 0.005,
        f_rgh            = 0.8,
        radius_inflation = "turbet",
        sigma_R_frac     = 0.02,
        sigma_S_frac     = 0.05,
        n_trials         = 1,
        n_draws          = 50,
        nlive            = 100,
        seed             = 42,
        show_inference   = True,
        show_errorbars   = True,
        show_colors      = False,
    )
    save_figure(fig, "generic_reproduction_native")


if __name__ == "__main__":
    main()
