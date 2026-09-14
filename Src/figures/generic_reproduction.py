"""Figure for Section 6.1 --- Reproduction of Schlecker et al. (2024).

Reproduces Fig. 5 of Schlecker+2024 on a generic Gaia-based sample using the
same fiducial parameters and inference conventions as the original paper.

Key settings that match Schlecker+2024:
  sigma_sma_mode = 'empirical'  -- std(R_obs in window)/sqrt(w); paper convention
  sma_x_mode     = 'standard'   -- x = mean(S_obs in window); paper convention
  radius_inflation = 'turbet'   -- Turbet+2020 steam-atmosphere grid
  use_dl21       = True         -- Dorn & Lichtenberg (2021) water-retention correction
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import hzied_bridge                                    # noqa: F401,E402 — sets HZIED on sys.path

from pipeline import run_hzied_analysis                # noqa: E402
from hzied_utils import build_f_dR                    # noqa: E402
from plotting import plot_fig5                         # noqa: E402
from utils import save_figure                          # noqa: E402

FIGSIZE = (5.0, 3.2)

TITLE = (
    r'Schlecker reproduction  |  '
    r'$S_\mathrm{thresh}=280\,\mathrm{W\,m^{-2}}$, '
    r'$x_\mathrm{H_2O}=0.005$, $f_\mathrm{rgh}=0.8$'
    '\n'
    r'$\ln\Delta Z = 1114$'
)


def main() -> None:
    # ── Run inference (suppress the internal figure) ─────────────────────────
    plt.ioff()
    _, _, results = run_hzied_analysis(
        # Stellar sample
        sample              = 'generic',
        N                   = 500,

        # Injection — Schlecker+2024 fiducial
        S_thresh            = 280.,
        wrr                 = 0.005,
        f_rgh               = 0.8,

        # Inflation model — Schlecker+2024 fiducial
        radius_inflation    = 'turbet',
        use_dl21            = True,

        # Measurement noise — Schlecker+2024 fiducial
        sigma_R_frac        = 0.02,
        sigma_S_frac        = 0.05,

        # Inference
        n_trials            = 1,
        n_draws             = 0,
        window              = 25,
        seed                = 42,
        nlive               = 100,
        sigma_sma_mode      = 'empirical',
        independent_bins    = False,
        sma_x_mode          = 'standard',

        show_inference      = True,
        show_errorbars      = False,
        show_colors         = False,
    )
    plt.close('all')
    plt.ion()

    # ── Build figure ──────────────────────────────────────────────────────────
    f_dR = build_f_dR()

    fig, ax = plt.subplots(figsize=FIGSIZE)
    plot_fig5(
        results[0],
        f_dR,
        ax             = ax,
        n_draws        = 50,
        show_errorbars = True,
        show_colors    = False,
        show_bayesian  = True,
        show_bin_edges = False,
        title          = TITLE,
    )
    fig.tight_layout()
    save_figure(fig, "generic_reproduction")


if __name__ == "__main__":
    main()
