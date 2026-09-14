"""Figure for Section 6.3.3 — HZIED with relaxed transit depth cut (60 ppm).

Same parameters as the baseline (plato_baseline_hzied.py) but with
depth_min_ppm=60 instead of 80.  This adds sub-Earth-radius planets
around solar-type P5 hosts (depth ~ 60 ppm ↔ R_p ~ 0.85 R_earth for
R_* = 1 R_sun) that are still firmly below the radius gap and detectable
by PLATO's photometric system.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import hzied_bridge                          # noqa: F401 — puts HZIED on sys.path

from pipeline import run_hzied_analysis      # noqa: E402
from hzied_utils import build_f_dR          # noqa: E402
from plotting import plot_fig5              # noqa: E402
from utils import save_figure               # noqa: E402

FIGSIZE = (8.0, 3.2)

COMMON = dict(
    S_thresh         = 280.,
    wrr              = 0.005,
    f_rgh            = 0.8,
    radius_inflation = 'turbet',
    use_dl21         = True,
    sigma_S_frac     = 0.05,
    seed             = 42,
    nlive            = 100,
    sigma_sma_mode   = 'empirical',
    independent_bins = False,
    sma_x_mode       = 'standard',
    n_trials         = 1,
    n_draws          = 0,
    age_mode         = 'sampled',
    show_inference   = True,
    depth_min_ppm    = 60,
)


def _planet_counts(r):
    """Return (n_total, n_cold, n_hot_uninfl, n_infl) from a pipeline result dict."""
    df    = r['df_survey']
    S_thr = r['injected'].get('S_thresh', 280.)
    hot   = df['S_abs'].values > S_thr
    mo    = (df['has_magmaocean'].values.astype(bool)
             if 'has_magmaocean' in df.columns else hot.copy())
    return len(df), int((~hot).sum()), int((hot & ~mo).sum()), int(mo.sum())


def main() -> None:
    # ── Run inference for P4 and P5 ───────────────────────────────────────────
    plt.ioff()
    _, _, res_p4 = run_hzied_analysis(sample='P4', **COMMON)
    _, _, res_p5 = run_hzied_analysis(sample='P5', **COMMON)
    plt.close('all')
    plt.ion()

    f_dR = build_f_dR()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, sharey=True)

    for ax, res, label in zip(axes, [res_p4, res_p5], ['P4', 'P5']):
        r = res[0]
        n, n_cold, n_hot, n_infl = _planet_counts(r)
        title = (
            f'{label}  Turbet, '
            r'$M\in[0.1,\,2.05]\,M_\oplus$, depth $\geq60\,$ppm'
            '\n'
            f'$N={n}$ (cold={n_cold}, hot={n_hot}, inflated={n_infl})'
        )
        plot_fig5(
            r, f_dR,
            ax             = ax,
            n_draws        = 0,
            show_errorbars = True,
            show_colors    = True,
            show_bayesian  = False,
            show_bin_edges = False,
            title          = title,
        )
        ax.title.set_fontsize(8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(which='both', top=False, right=False)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='best', fontsize=7, markerscale=0.75,
                  handlelength=1.4, borderpad=0.5, labelspacing=0.3,
                  frameon=True, framealpha=0.9, edgecolor='0.7')

    axes[1].set_ylabel('')
    fig.tight_layout()
    save_figure(fig, "plato_relaxed_depth_hzied")

    for label, res in [('P4', res_p4), ('P5', res_p5)]:
        n, n_cold, n_hot, n_infl = _planet_counts(res[0])
        print(f'{label}: N={n}, cold={n_cold}, hot={n_hot}, inflated={n_infl}, '
              f'lnDZ={res[0]["lnK"]:.1f}')


if __name__ == "__main__":
    main()
