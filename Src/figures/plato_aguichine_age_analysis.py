"""Figure for Section 6.5.4 — Aguichine age-dependent HZIED analysis.

The Aguichine et al.\ (2025) irradiated-ocean model is the only steam
prescription used in this thesis for which the tabulated radius depends
explicitly on planet age (via water-layer contraction and envelope loss).
This script quantifies how the recovered HZIED signal changes when the
host-star age assignment is varied across four schemes:

  * strict     — keep only stars with a Gaia FLAME age
                 (Creevey+2023); drop the rest.
  * sampled    — FLAME where available; bootstrap-fill missing ages from
                 the empirical FLAME distribution of the same sample.
  * flame_flat — FLAME where available; fill missing ages from a uniform
                 [0, 10] Gyr prior (new mode, added for this analysis).
  * flat       — uniform [0, 10] Gyr prior for every star; FLAME ignored.

For each age mode we run 10 independent noise realisations per sample
(P4 and P5) and record the Bayes factor ln ΔZ and the recovered
posterior median $\\hat{S}_\\mathrm{thresh}$.  All non-age parameters are
held at the section 6.6.1 baseline (agni_updated `wrr`, `f_rgh`, depth
cut, inference settings).

Produces two figures:
  plato_aguichine_age_lnk.pdf/.png    — lnΔZ + recovered S_thresh vs
                                         age_mode, with 10-seed bands.
  plato_aguichine_age_panels.pdf/.png — 2 rows × 4 cols scatter panels
                                         showing one representative trial
                                         per (sample, age_mode).
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
FIGSIZE_PANELS = (10.5, 5.5)

AGE_MODES = ['strict', 'sampled', 'flame_flat', 'flat']

N_TRIALS = 10

COMMON = dict(
    S_thresh         = 280.,
    wrr              = 0.005,
    f_rgh            = 0.8,
    radius_inflation = 'aguichine',
    use_dl21          = True,
    sigma_S_frac     = 0.05,
    seed             = 42,
    nlive            = 100,
    sigma_sma_mode   = 'empirical',
    independent_bins = False,
    sma_x_mode       = 'standard',
    n_trials         = N_TRIALS,
    n_draws          = 0,
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


def _draw_panel(ax, r, sample, mode):
    n, n_cold, _, n_infl = _planet_counts(r)
    title = (
        f'{sample}  {mode}\n'
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
    ax.title.set_fontsize(7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(which='both', top=False, right=False)


def main() -> None:
    lnk_p4 = np.zeros((len(AGE_MODES), N_TRIALS))
    lnk_p5 = np.zeros((len(AGE_MODES), N_TRIALS))
    sth_p4 = np.zeros((len(AGE_MODES), N_TRIALS))
    sth_p5 = np.zeros((len(AGE_MODES), N_TRIALS))
    n_p4   = np.zeros(len(AGE_MODES), dtype=int)
    n_p5   = np.zeros(len(AGE_MODES), dtype=int)
    results = {}   # (sample, mode) → list of N_TRIALS result dicts

    print(f'\n{"age_mode":>12}  {"P4 N":>4}  {"P4 lnDZ (med [min,max])":>24}  '
          f'{"P4 Ŝ_th":>7}  {"P5 N":>4}  {"P5 lnDZ (med [min,max])":>24}  '
          f'{"P5 Ŝ_th":>7}')
    print('-' * 108)

    plt.ioff()
    for i, mode in enumerate(AGE_MODES):
        # Unique seed base per age mode so caches don't collide when N
        # happens to coincide across modes.
        seed_base_i = COMMON['seed'] + i * 200
        kw = {**COMMON, 'seed': seed_base_i, 'age_mode': mode}
        _, _, rp4 = run_hzied_analysis(sample='P4', **kw)
        _, _, rp5 = run_hzied_analysis(sample='P5', **kw)
        plt.close('all')
        results[('P4', mode)] = rp4
        results[('P5', mode)] = rp5
        lnk_p4[i] = [r['lnK'] for r in rp4]
        lnk_p5[i] = [r['lnK'] for r in rp5]
        sth_p4[i] = [np.median(r['chains'][:, 0]) for r in rp4]
        sth_p5[i] = [np.median(r['chains'][:, 0]) for r in rp5]
        n_p4[i] = len(rp4[0]['df_survey'])
        n_p5[i] = len(rp5[0]['df_survey'])
        m4 = np.median(lnk_p4[i]); lo4 = lnk_p4[i].min(); hi4 = lnk_p4[i].max()
        m5 = np.median(lnk_p5[i]); lo5 = lnk_p5[i].min(); hi5 = lnk_p5[i].max()
        s4 = np.median(sth_p4[i]); s5 = np.median(sth_p5[i])
        print(f'{mode:>12}  {n_p4[i]:>4}  {m4:>8.1f} [{lo4:>5.1f},{hi4:>5.1f}]  '
              f'{s4:>7.0f}  {n_p5[i]:>4}  {m5:>8.1f} [{lo5:>5.1f},{hi5:>5.1f}]  {s5:>7.0f}')
    plt.ion()

    def _band(arr):
        return (np.median(arr, axis=1),
                np.percentile(arr, 16, axis=1),
                np.percentile(arr, 84, axis=1))

    med_p4_lnk, lo_p4_lnk, hi_p4_lnk = _band(lnk_p4)
    med_p5_lnk, lo_p5_lnk, hi_p5_lnk = _band(lnk_p5)
    med_p4_sth, lo_p4_sth, hi_p4_sth = _band(sth_p4)
    med_p5_sth, lo_p5_sth, hi_p5_sth = _band(sth_p5)

    x = np.arange(len(AGE_MODES))

    # ── Figure A: 1×2 lnΔZ + recovered S_thresh ────────────────────────────
    fig_a, (ax_l, ax_r) = plt.subplots(1, 2, figsize=FIGSIZE_SWEEP)

    # Left panel: ln ΔZ
    ax_l.fill_between(x, lo_p4_lnk, hi_p4_lnk, color='#5C6BC0', alpha=0.25, step='mid')
    ax_l.plot(x, med_p4_lnk, 'o-', color='#5C6BC0', label='P4 (M dwarfs)')
    ax_l.fill_between(x, lo_p5_lnk, hi_p5_lnk, color='#EF5350', alpha=0.25, step='mid')
    ax_l.plot(x, med_p5_lnk, 's-', color='#EF5350', label='P5 (FGK)')
    ax_l.set_xticks(x); ax_l.set_xticklabels(AGE_MODES, rotation=15, ha='right')
    ax_l.set_xlabel(r'Age-assignment mode')
    ax_l.set_ylabel(r'$\ln\Delta Z$')
    ax_l.set_title(r'Bayes factor $\ln\Delta Z$', fontsize=9)
    ax_l.legend(fontsize=7, loc='best')

    # Right panel: recovered S_thresh
    S_INJ = COMMON['S_thresh']
    ax_r.fill_between(x, lo_p4_sth, hi_p4_sth, color='#5C6BC0', alpha=0.25, step='mid')
    ax_r.plot(x, med_p4_sth, 'o-', color='#5C6BC0', label='P4')
    ax_r.fill_between(x, lo_p5_sth, hi_p5_sth, color='#EF5350', alpha=0.25, step='mid')
    ax_r.plot(x, med_p5_sth, 's-', color='#EF5350', label='P5')
    ax_r.axhline(S_INJ, color='k', ls=':', lw=0.9,
                 label=fr'injected $S_\mathrm{{thresh}}={S_INJ:.0f}$')
    ax_r.set_xticks(x); ax_r.set_xticklabels(AGE_MODES, rotation=15, ha='right')
    ax_r.set_xlabel(r'Age-assignment mode')
    ax_r.set_ylabel(r'Recovered $\hat{S}_\mathrm{thresh}$ (W m$^{-2}$)')
    ax_r.set_title(r'Best-fit $\hat{S}_\mathrm{thresh}$', fontsize=9)
    ax_r.legend(fontsize=7, loc='best')

    for ax in (ax_l, ax_r):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(which='both', top=False, right=False)

    fig_a.suptitle(
        fr'Aguichine (2025) irradiated ocean planets, depth $\geq 60\,\mathrm{{ppm}}$, '
        fr'median $\pm$ 16--84\% of {N_TRIALS} seeds per point',
        fontsize=9, y=1.02,
    )
    fig_a.tight_layout()
    save_figure(fig_a, 'plato_aguichine_age_lnk')

    # ── Figure B: 2 rows × 4 cols scatter panels ────────────────────────────
    fig_b, axes = plt.subplots(2, len(AGE_MODES), figsize=FIGSIZE_PANELS,
                               sharey='row')
    for col, mode in enumerate(AGE_MODES):
        _draw_panel(axes[0, col], results[('P4', mode)][0], 'P4', mode)
        _draw_panel(axes[1, col], results[('P5', mode)][0], 'P5', mode)
        if col > 0:
            axes[0, col].set_ylabel('')
            axes[1, col].set_ylabel('')

    fig_b.tight_layout()
    save_figure(fig_b, 'plato_aguichine_age_panels')


if __name__ == "__main__":
    main()
