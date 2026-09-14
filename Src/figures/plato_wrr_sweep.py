"""Figure for Section 6.6.1 — Variation of the water-to-rock ratio.

Sweeps the injected water-to-rock ratio wrr over the AGNI-updated steam
table grid and records the recovered Bayes factor lnΔZ for the PLATO P4
(M-dwarf) and P5 (FGK) samples.

Grid: wrr ∈ {1e-4, 5e-3, 2e-2, 3e-2, 4e-2} — every value supported by the
AGNI+PALEOS ratio-method steam table on the pipeline-side agni_updated
prescription. wrr = 5e-3 is the Schlecker+2024 fiducial.

Produces two figures:
    plato_wrr_sweep_lnk.pdf/.png    — lnΔZ vs wrr for P4 and P5
    plato_wrr_sweep_panels.pdf/.png — scatter panels for representative wrr
                                       values (2 rows × 3 cols)

All other parameters are held fixed at the section-6.6.1 configuration
(see the LaTeX table in the same subsection).
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

WRR_GRID   = [1e-4, 5e-3, 2e-2, 3e-2, 4e-2]
WRR_PANELS = [1e-4, 5e-3, 4e-2]
WRR_FIDUCIAL = 5e-3

N_TRIALS = 10   # independent noise realisations per (sample, wrr)

COMMON = dict(
    S_thresh         = 280.,
    f_rgh            = 0.8,
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


def _draw_panel(ax, r, label, wrr):
    n, n_cold, _, n_infl = _planet_counts(r)
    title = (
        f'{label}  $x_\\mathrm{{H_2O}}={wrr:g}$\n'
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
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='best', fontsize=7, markerscale=0.75,
              handlelength=1.4, borderpad=0.5, labelspacing=0.3,
              frameon=True, framealpha=0.9, edgecolor='0.7')


def main() -> None:
    # Per-sample arrays of shape (len(WRR_GRID), N_TRIALS)
    lnk_p4 = np.zeros((len(WRR_GRID), N_TRIALS))
    lnk_p5 = np.zeros((len(WRR_GRID), N_TRIALS))
    # Per-seed posterior-median S_thresh recovered by dynesty.  chains column 0
    # is S_thresh in the SMA hypothesis (magma_ocean_hypo).
    sth_p4 = np.zeros((len(WRR_GRID), N_TRIALS))
    sth_p5 = np.zeros((len(WRR_GRID), N_TRIALS))
    results = {}   # (sample, wrr) → list of N_TRIALS result dicts

    print(f'\n{"wrr":>8}  {"P4 lnDZ (med [min,max])":>24}  {"P4 S_th":>8}  '
          f'{"P5 lnDZ (med [min,max])":>24}  {"P5 S_th":>8}')
    print('-' * 90)

    plt.ioff()
    for i, wrr in enumerate(WRR_GRID):
        _, _, rp4 = run_hzied_analysis(sample='P4', wrr=wrr, **COMMON)
        _, _, rp5 = run_hzied_analysis(sample='P5', wrr=wrr, **COMMON)
        plt.close('all')
        results[('P4', wrr)] = rp4
        results[('P5', wrr)] = rp5
        lnk_p4[i] = [r['lnK'] for r in rp4]
        lnk_p5[i] = [r['lnK'] for r in rp5]
        sth_p4[i] = [np.median(r['chains'][:, 0]) for r in rp4]
        sth_p5[i] = [np.median(r['chains'][:, 0]) for r in rp5]
        m4 = np.median(lnk_p4[i]); lo4 = lnk_p4[i].min(); hi4 = lnk_p4[i].max()
        m5 = np.median(lnk_p5[i]); lo5 = lnk_p5[i].min(); hi5 = lnk_p5[i].max()
        s4 = np.median(sth_p4[i]); s5 = np.median(sth_p5[i])
        print(f'{wrr:>8.4f}  {m4:>8.1f} [{lo4:>5.1f},{hi4:>5.1f}]  {s4:>8.0f}  '
              f'{m5:>8.1f} [{lo5:>5.1f},{hi5:>5.1f}]  {s5:>8.0f}')
    plt.ion()

    def _band(arr):
        return (np.median(arr, axis=1),
                np.percentile(arr, 16, axis=1),
                np.percentile(arr, 84, axis=1))

    med_p4_lnk, lo_p4_lnk, hi_p4_lnk = _band(lnk_p4)
    med_p5_lnk, lo_p5_lnk, hi_p5_lnk = _band(lnk_p5)
    med_p4_sth, lo_p4_sth, hi_p4_sth = _band(sth_p4)
    med_p5_sth, lo_p5_sth, hi_p5_sth = _band(sth_p5)

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=FIGSIZE_SWEEP)

    # ── Left panel: ln ΔZ ────────────────────────────────────────────────
    ax_l.fill_between(WRR_GRID, lo_p4_lnk, hi_p4_lnk, color='#5C6BC0', alpha=0.25)
    ax_l.plot(WRR_GRID, med_p4_lnk, 'o-', color='#5C6BC0',
              label='P4 (M dwarfs)')
    ax_l.fill_between(WRR_GRID, lo_p5_lnk, hi_p5_lnk, color='#EF5350', alpha=0.25)
    ax_l.plot(WRR_GRID, med_p5_lnk, 's-', color='#EF5350',
              label='P5 (FGK)')
    ax_l.axvline(WRR_FIDUCIAL, color='0.5', ls='--', lw=0.8,
                 label=fr'fiducial $x_\mathrm{{H_2O}}={WRR_FIDUCIAL:g}$')
    ax_l.set_xscale('log')
    ax_l.set_xlabel(r'Water-to-rock ratio $x_\mathrm{H_2O}$')
    ax_l.set_ylabel(r'$\ln\Delta Z$')
    ax_l.set_title(r'Bayes factor $\ln\Delta Z$', fontsize=9)
    ax_l.legend(fontsize=7, loc='upper left')

    # ── Right panel: recovered S_thresh ──────────────────────────────────
    S_INJ = COMMON['S_thresh']
    ax_r.fill_between(WRR_GRID, lo_p4_sth, hi_p4_sth, color='#5C6BC0', alpha=0.25)
    ax_r.plot(WRR_GRID, med_p4_sth, 'o-', color='#5C6BC0', label='P4')
    ax_r.fill_between(WRR_GRID, lo_p5_sth, hi_p5_sth, color='#EF5350', alpha=0.25)
    ax_r.plot(WRR_GRID, med_p5_sth, 's-', color='#EF5350', label='P5')
    ax_r.axhline(S_INJ, color='k', ls=':', lw=0.9,
                 label=fr'injected $S_\mathrm{{thresh}}={S_INJ:.0f}$')
    ax_r.axvline(WRR_FIDUCIAL, color='0.5', ls='--', lw=0.8)
    ax_r.set_xscale('log')
    ax_r.set_xlabel(r'Water-to-rock ratio $x_\mathrm{H_2O}$')
    ax_r.set_ylabel(r'Recovered $\hat{S}_\mathrm{thresh}$ (W m$^{-2}$)')
    ax_r.set_title(r'Best-fit $\hat{S}_\mathrm{thresh}$', fontsize=9)
    ax_r.legend(fontsize=7, loc='best')

    for ax in (ax_l, ax_r):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(which='both', top=False, right=False)

    fig.suptitle(
        fr'\texttt{{agni\_updated}}, depth $\geq 60\,\mathrm{{ppm}}$, '
        fr'median $\pm$ 16--84\% of {N_TRIALS} seeds per point',
        fontsize=9, y=1.02,
    )
    fig.tight_layout()
    save_figure(fig, 'plato_wrr_sweep_lnk')

    # ── Figure B: scatter panels for representative wrr values ─────────────
    fig_b, axes = plt.subplots(2, len(WRR_PANELS), figsize=FIGSIZE_PANELS,
                               sharey='row')

    for col, wrr in enumerate(WRR_PANELS):
        _draw_panel(axes[0, col], results[('P4', wrr)][0], 'P4', wrr)
        _draw_panel(axes[1, col], results[('P5', wrr)][0], 'P5', wrr)
        if col > 0:
            axes[0, col].set_ylabel('')
            axes[1, col].set_ylabel('')

    fig_b.tight_layout()
    save_figure(fig_b, 'plato_wrr_sweep_panels')


if __name__ == "__main__":
    main()
