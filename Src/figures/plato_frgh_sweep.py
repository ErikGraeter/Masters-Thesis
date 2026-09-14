"""Figure for Section 6.8.1 — Variation of the runaway fraction f_rgh.

Sweeps the injected runaway-greenhouse fraction f_rgh ∈ [0, 1] at the
otherwise fiducial agni_updated configuration.  f_rgh absorbs our
ignorance of steam-atmosphere lifetimes: it is the fraction of
hot-side planets (S > S_thresh) currently in an inflated state.
f_rgh = 0 → no planet is inflated (H1 collapses onto H0);
f_rgh = 1 → every hot-side planet is inflated (maximum signal).

The sweep uses 10 independent noise realisations per grid point,
following the same construction as the wrr and Hycean-fraction sweeps.

Grid: f_rgh ∈ {0.2, 0.4, 0.6, 0.8, 1.0} (0.8 is the Schlecker+2024
fiducial).  f_rgh = 0 is omitted from the grid because it degenerates
H1 into H0 and gives ln ΔZ that is identically zero up to sampler
noise; adding it would only compress the plot's y-axis without adding
information.

Produces two figures:
    plato_frgh_sweep_lnk.pdf/.png    — ln ΔZ + recovered S_thresh vs
                                        f_rgh, with 10-seed bands.
    plato_frgh_sweep_panels.pdf/.png — 2 rows × 3 cols scatter panels
                                        for f_rgh ∈ {0.2, 0.8, 1.0}.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import hzied_bridge                          # noqa: F401

from pipeline import run_hzied_analysis      # noqa: E402
from hzied_utils import build_f_dR           # noqa: E402
from plotting import plot_fig5               # noqa: E402
from utils import save_figure                # noqa: E402

FIGSIZE_SWEEP  = (9.0, 3.4)
FIGSIZE_PANELS = (8.0, 5.5)

FRGH_GRID   = [0.2, 0.4, 0.6, 0.8, 1.0]
FRGH_PANELS = [0.2, 0.8, 1.0]
FRGH_FIDUCIAL = 0.8

N_TRIALS = 10

COMMON = dict(
    S_thresh         = 280.,
    wrr              = 0.005,
    radius_inflation = 'agni_updated',
    use_dl21         = True,
    sigma_S_frac     = 0.05,
    seed             = 42,
    nlive            = 100,
    sigma_sma_mode   = 'empirical',
    independent_bins = False,
    sma_x_mode       = 'standard',
    n_trials         = N_TRIALS,
    n_draws          = 0,
    age_mode         = 'sampled',
    show_inference   = True,
    depth_min_ppm    = 60,
)


def _planet_counts(r):
    df    = r['df_survey']
    S_thr = r['injected'].get('S_thresh', 280.)
    hot   = df['S_abs'].values > S_thr
    mo    = (df['has_magmaocean'].values.astype(bool)
             if 'has_magmaocean' in df.columns else hot.copy())
    return len(df), int((~hot).sum()), int((hot & ~mo).sum()), int(mo.sum())


def _draw_panel(ax, r, sample, frgh):
    n, n_cold, _, n_infl = _planet_counts(r)
    title = (
        f'{sample}  $f_\\mathrm{{rgh}}={frgh:g}$\n'
        f'$N={n}$ (cold={n_cold}, inflated={n_infl})   '
        f'$\\ln\\Delta Z = {r["lnK"]:.1f}$'
    )
    f_dR = build_f_dR()
    plot_fig5(
        r, f_dR,
        ax             = ax,
        n_draws        = 0,
        show_errorbars = False,
        show_colors    = True,
        show_bayesian  = False,
        show_bin_edges = False,
        show_inflation = True,
        title          = title,
    )
    df = r['df_survey']
    ax.errorbar(df['S_obs'], df['R_obs'], xerr=df['sigma_S'],
                fmt='none', ecolor='grey', alpha=0.15, lw=0.5, zorder=1)
    ax.title.set_fontsize(8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(which='both', top=False, right=False)


def main() -> None:
    lnk_p4 = np.zeros((len(FRGH_GRID), N_TRIALS))
    lnk_p5 = np.zeros((len(FRGH_GRID), N_TRIALS))
    sth_p4 = np.zeros((len(FRGH_GRID), N_TRIALS))
    sth_p5 = np.zeros((len(FRGH_GRID), N_TRIALS))
    results = {}

    print(f'\n{"f_rgh":>7}  {"P4 lnDZ (med [min,max])":>24}  {"P4 Ŝ_th":>7}  '
          f'{"P5 lnDZ (med [min,max])":>24}  {"P5 Ŝ_th":>7}')
    print('-' * 92)

    plt.ioff()
    for i, frgh in enumerate(FRGH_GRID):
        # Unique seed base per f_rgh to avoid cache collisions when N is
        # constant across the grid (f_rgh doesn't change which planets pass
        # the cuts, so N stays the same for both samples).
        seed_base_i = COMMON['seed'] + i * 200
        kw = {**COMMON, 'seed': seed_base_i, 'f_rgh': frgh}
        _, _, rp4 = run_hzied_analysis(sample='P4', **kw)
        _, _, rp5 = run_hzied_analysis(sample='P5', **kw)
        plt.close('all')
        results[('P4', frgh)] = rp4
        results[('P5', frgh)] = rp5
        lnk_p4[i] = [r['lnK'] for r in rp4]
        lnk_p5[i] = [r['lnK'] for r in rp5]
        sth_p4[i] = [np.median(r['chains'][:, 0]) for r in rp4]
        sth_p5[i] = [np.median(r['chains'][:, 0]) for r in rp5]
        m4 = np.median(lnk_p4[i]); lo4 = lnk_p4[i].min(); hi4 = lnk_p4[i].max()
        m5 = np.median(lnk_p5[i]); lo5 = lnk_p5[i].min(); hi5 = lnk_p5[i].max()
        s4 = np.median(sth_p4[i]); s5 = np.median(sth_p5[i])
        print(f'{frgh:>7.2f}  {m4:>8.1f} [{lo4:>5.1f},{hi4:>5.1f}]  {s4:>7.0f}  '
              f'{m5:>8.1f} [{lo5:>5.1f},{hi5:>5.1f}]  {s5:>7.0f}')
    plt.ion()

    def _band(arr):
        return (np.median(arr, axis=1),
                np.percentile(arr, 16, axis=1),
                np.percentile(arr, 84, axis=1))

    med_p4_lnk, lo_p4_lnk, hi_p4_lnk = _band(lnk_p4)
    med_p5_lnk, lo_p5_lnk, hi_p5_lnk = _band(lnk_p5)
    med_p4_sth, lo_p4_sth, hi_p4_sth = _band(sth_p4)
    med_p5_sth, lo_p5_sth, hi_p5_sth = _band(sth_p5)

    fig_a, (ax_l, ax_r) = plt.subplots(1, 2, figsize=FIGSIZE_SWEEP)

    # ── Left panel: ln ΔZ ───────────────────────────────────────────────
    ax_l.fill_between(FRGH_GRID, lo_p4_lnk, hi_p4_lnk, color='#5C6BC0', alpha=0.25)
    ax_l.plot(FRGH_GRID, med_p4_lnk, 'o-', color='#5C6BC0',
              label='P4 (M dwarfs)')
    ax_l.fill_between(FRGH_GRID, lo_p5_lnk, hi_p5_lnk, color='#EF5350', alpha=0.25)
    ax_l.plot(FRGH_GRID, med_p5_lnk, 's-', color='#EF5350',
              label='P5 (FGK)')
    ax_l.axvline(FRGH_FIDUCIAL, color='0.5', ls='--', lw=0.8,
                 label=fr'fiducial $f_\mathrm{{rgh}}={FRGH_FIDUCIAL:g}$')
    ax_l.set_xlabel(r'Runaway-greenhouse fraction $f_\mathrm{rgh}$')
    ax_l.set_ylabel(r'$\ln\Delta Z$')
    ax_l.set_title(r'Bayes factor $\ln\Delta Z$', fontsize=9)
    ax_l.legend(fontsize=7, loc='upper left')

    # ── Right panel: recovered S_thresh ────────────────────────────────
    S_INJ = COMMON['S_thresh']
    ax_r.fill_between(FRGH_GRID, lo_p4_sth, hi_p4_sth, color='#5C6BC0', alpha=0.25)
    ax_r.plot(FRGH_GRID, med_p4_sth, 'o-', color='#5C6BC0', label='P4')
    ax_r.fill_between(FRGH_GRID, lo_p5_sth, hi_p5_sth, color='#EF5350', alpha=0.25)
    ax_r.plot(FRGH_GRID, med_p5_sth, 's-', color='#EF5350', label='P5')
    ax_r.axhline(S_INJ, color='k', ls=':', lw=0.9,
                 label=fr'injected $S_\mathrm{{thresh}}={S_INJ:.0f}$')
    ax_r.axvline(FRGH_FIDUCIAL, color='0.5', ls='--', lw=0.8)
    ax_r.set_xlabel(r'Runaway-greenhouse fraction $f_\mathrm{rgh}$')
    ax_r.set_ylabel(r'Recovered $\hat{S}_\mathrm{thresh}$ (W m$^{-2}$)')
    ax_r.set_title(r'Best-fit $\hat{S}_\mathrm{thresh}$', fontsize=9)
    ax_r.legend(fontsize=7, loc='best')

    for ax in (ax_l, ax_r):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(which='both', top=False, right=False)

    fig_a.suptitle(
        fr'\texttt{{agni\_updated}}, depth $\geq 60\,\mathrm{{ppm}}$, '
        fr'median $\pm$ 16--84\% of {N_TRIALS} seeds per point',
        fontsize=9, y=1.02,
    )
    fig_a.tight_layout()
    save_figure(fig_a, 'plato_frgh_sweep_lnk')

    # ── Figure B: scatter panels for representative f_rgh values ───────
    fig_b, axes = plt.subplots(2, len(FRGH_PANELS), figsize=FIGSIZE_PANELS,
                               sharey='row')
    for col, frgh in enumerate(FRGH_PANELS):
        _draw_panel(axes[0, col], results[('P4', frgh)][0], 'P4', frgh)
        _draw_panel(axes[1, col], results[('P5', frgh)][0], 'P5', frgh)
        if col > 0:
            axes[0, col].set_ylabel('')
            axes[1, col].set_ylabel('')

    fig_b.tight_layout()
    save_figure(fig_b, 'plato_frgh_sweep_panels')


if __name__ == "__main__":
    main()
