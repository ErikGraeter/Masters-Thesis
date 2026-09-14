"""Figures for Section 6.5 — steam model comparison on PLATO P4 and P5.

Generates one P4+P5 side-by-side scatter figure per inflation prescription.
All runs use depth_min_ppm=60 (relaxed threshold) and age_mode='sampled'.
Mass limits follow the per-model registry in pipeline._M_MIN / _M_MAX.

Models
------
agni               : 2D AGNI grid_022, M ∈ [0.1, 10] M⊕
agni_updated       : AGNI+PALEOS steam table, M ∈ [0.5, 20] M⊕
aguichine          : Aguichine+2025 irradiated ocean table, M ∈ [0.2, 20] M⊕
hycean_pierrehumbert : Pierrehumbert (2022) pure-water Hycean, M ∈ [1.5, 9] M⊕
hycean_mixed       : agni_updated + Pierrehumbert (f_hycean=0.5), M ∈ [0.5, 20] M⊕
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import hzied_bridge                          # noqa: F401

from pipeline import run_hzied_analysis      # noqa: E402
from hzied_utils import build_f_dR          # noqa: E402
from plotting import plot_fig5              # noqa: E402
from utils import save_figure               # noqa: E402

FIGSIZE = (8.0, 3.2)

COMMON = dict(
    S_thresh         = 280.,
    wrr              = 0.005,
    f_rgh            = 0.8,
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

MODELS = [
    # (radius_inflation,        label,               extra_kwargs)
    ('agni',                 'AGNI',              {}),
    ('agni_updated',         'AGNI\\_updated',    {}),
    ('aguichine',            'Aguichine',         {}),
    ('hycean_pierrehumbert', 'Pierrehumbert',     {'S_thresh': 435.}),
    ('hycean_mixed',         'Hycean mixed',      {'f_hycean': 0.5, 'S_thresh_hycean': 435.}),
]


def _planet_counts(r):
    df    = r['df_survey']
    S_thr = r['injected'].get('S_thresh', 280.)
    hot   = df['S_abs'].values > S_thr
    mo    = (df['has_magmaocean'].values.astype(bool)
             if 'has_magmaocean' in df.columns else hot.copy())
    return len(df), int((~hot).sum()), int((hot & ~mo).sum()), int(mo.sum())


def _make_panel(ax, r, label, model_label, depth_ppm=60):
    n, n_cold, n_hot, n_infl = _planet_counts(r)
    injected = r['injected']
    m_min = injected.get('M_min', 0.1)
    m_max = injected.get('M_max', 2.05)
    s_thr = injected.get('S_thresh', 280.)
    title = (
        f'{label}  {model_label}, '
        f'$M\\in[{m_min},\\,{m_max}]\\,M_\\oplus$, depth $\\geq{depth_ppm}\\,$ppm'
        '\n'
        f'$N={n}$ (cold={n_cold}, hot={n_hot}, inflated={n_infl})'
    )
    f_dR = build_f_dR()
    plot_fig5(
        r, f_dR,
        ax             = ax,
        n_draws        = 0,
        show_errorbars = False,   # y-errorbars suppressed; inflation lines show the shift
        show_colors    = True,
        show_bayesian  = False,
        show_bin_edges = False,
        show_inflation = True,
        title          = title,
    )
    # Draw x-only (σ_S) errorbars so instellation uncertainty is still visible
    df = r['df_survey']
    ax.errorbar(df['S_obs'], df['R_obs'], xerr=df['sigma_S'],
                fmt='none', ecolor='grey', alpha=0.15, lw=0.5, zorder=1)
    ax.title.set_fontsize(8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(which='both', top=False, right=False)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='best', fontsize=7, markerscale=0.75,
              handlelength=1.4, borderpad=0.5, labelspacing=0.3,
              frameon=True, framealpha=0.9, edgecolor='0.7')
    return n, n_cold, n_hot, n_infl, r['lnK']


def main() -> None:
    print('\n' + '='*70)
    print(f'{"Model":<25}  {"Sample":<4}  {"N":>4}  {"cold":>4}  '
          f'{"hot":>4}  {"infl":>4}  {"lnDZ":>8}')
    print('='*70)

    for ri, model_label, extra in MODELS:
        kwargs = {**COMMON, **extra}   # extra overrides COMMON (e.g. S_thresh for Pierrehumbert)
        plt.ioff()
        _, _, res_p4 = run_hzied_analysis(sample='P4', radius_inflation=ri, **kwargs)
        _, _, res_p5 = run_hzied_analysis(sample='P5', radius_inflation=ri, **kwargs)
        plt.close('all')
        plt.ion()

        fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, sharey=True)

        for ax, res, sample_label in zip(axes, [res_p4, res_p5], ['P4', 'P5']):
            if not res:
                ax.text(0.5, 0.5, f'No planets\n({sample_label})',
                        ha='center', va='center', transform=ax.transAxes, fontsize=10)
                ax.set_title(f'{sample_label}  {model_label}', fontsize=8)
                print(f'{ri:<25}  {sample_label:<4}  {"—":>4}  {"—":>4}  '
                      f'{"—":>4}  {"—":>4}  {"—":>8}')
                continue
            r = res[0]
            n, nc, nh, ni, lnk = _make_panel(ax, r, sample_label, model_label)
            print(f'{ri:<25}  {sample_label:<4}  {n:>4}  {nc:>4}  '
                  f'{nh:>4}  {ni:>4}  {lnk:>8.1f}')

        axes[1].set_ylabel('')
        fig.tight_layout()
        save_figure(fig, f'plato_{ri}_hzied')

    print('='*70 + '\n')


if __name__ == "__main__":
    main()
