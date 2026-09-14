"""Figure for Section 6.5.6 — Hycean fraction sweep for the hybrid model.

Sweeps f_hycean ∈ {0, 0.25, 0.5, 0.75, 1.0} and produces:
  (A) lnΔZ vs f_hycean for P4 and P5 (summary line plot)
  (B) scatter panels for f_hycean ∈ {0, 0.5, 1.0} for P4 and P5

Free parameters of the hybrid model:
  f_hycean       : fraction of planets in M ∈ [1.5, 9] M⊕ treated as Hycean
                   (with S_thresh_hycean = 435 W m⁻²); the remainder follow
                   the agni_updated rocky prescription (S_thresh = 280 W m⁻²).
  S_thresh_hycean: runaway greenhouse threshold for Hycean worlds (Innes+2023).

f_hycean = 0 recovers the pure agni_updated result;
f_hycean = 1 assigns every planet in [1.5, 9] M⊕ as Hycean.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import hzied_bridge                          # noqa: F401

from pipeline import run_hzied_analysis      # noqa: E402
from hzied_utils import build_f_dR          # noqa: E402
from plotting import plot_fig5              # noqa: E402
from utils import save_figure               # noqa: E402

FIGSIZE_SWEEP  = (9.0, 3.4)   # 1×2: lnΔZ + recovered S_thresh
FIGSIZE_PANELS = (8.0, 5.5)   # 2 rows × 3 columns scatter

F_HYCEAN_SWEEP  = [0.0, 0.25, 0.5, 0.75, 1.0]
F_HYCEAN_PANELS = [0.0, 0.5, 1.0]

N_TRIALS = 10   # independent noise realisations per (sample, f_hycean)

COMMON = dict(
    S_thresh         = 280.,
    wrr              = 0.005,
    f_rgh            = 0.8,
    radius_inflation = 'hycean_mixed',
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
    S_thresh_hycean  = 435.,
)


def _planet_counts(r):
    df    = r['df_survey']
    S_thr = r['injected'].get('S_thresh', 280.)
    hot   = df['S_abs'].values > S_thr
    mo    = (df['has_magmaocean'].values.astype(bool)
             if 'has_magmaocean' in df.columns else hot.copy())
    return len(df), int((~hot).sum()), int((hot & ~mo).sum()), int(mo.sum())


def _draw_panel(ax, r, label, f_hycean):
    n, n_cold, n_hot, n_infl = _planet_counts(r)
    title = (
        f'{label}  $f_\\mathrm{{hycean}}={f_hycean:.2f}$\n'
        f'$N={n}$ (cold={n_cold}, inflated={n_infl})'
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
    # ── Run sweep ──────────────────────────────────────────────────────────
    lnk_p4 = np.zeros((len(F_HYCEAN_SWEEP), N_TRIALS))
    lnk_p5 = np.zeros((len(F_HYCEAN_SWEEP), N_TRIALS))
    # Column 0 of the SMA hypothesis chain is S_thresh (magma_ocean_hypo).
    sth_p4 = np.zeros((len(F_HYCEAN_SWEEP), N_TRIALS))
    sth_p5 = np.zeros((len(F_HYCEAN_SWEEP), N_TRIALS))
    results = {}   # (sample, f_hycean) → list of N_TRIALS result dicts

    print(f'\n{"f_hycean":>8}  {"P4 lnDZ (med [min,max])":>24}  {"P4 S_th":>8}  '
          f'{"P5 lnDZ (med [min,max])":>24}  {"P5 S_th":>8}')
    print('-' * 92)

    plt.ioff()
    for i, fh in enumerate(F_HYCEAN_SWEEP):
        # Unique seed base per f_hycean to avoid cache collisions when N is
        # constant across the grid (P4 stays at 139 across all f_hycean).
        # Trials within each f_hycean use seed_base + 13k for k = 0..N_TRIALS-1.
        seed_base_i = COMMON['seed'] + i * 200
        kw = {**COMMON, 'seed': seed_base_i}
        _, _, rp4 = run_hzied_analysis(sample='P4', f_hycean=fh, **kw)
        _, _, rp5 = run_hzied_analysis(sample='P5', f_hycean=fh, **kw)
        plt.close('all')
        results[('P4', fh)] = rp4
        results[('P5', fh)] = rp5
        lnk_p4[i] = [r['lnK'] for r in rp4]
        lnk_p5[i] = [r['lnK'] for r in rp5]
        sth_p4[i] = [np.median(r['chains'][:, 0]) for r in rp4]
        sth_p5[i] = [np.median(r['chains'][:, 0]) for r in rp5]
        m4 = np.median(lnk_p4[i]); lo4 = lnk_p4[i].min(); hi4 = lnk_p4[i].max()
        m5 = np.median(lnk_p5[i]); lo5 = lnk_p5[i].min(); hi5 = lnk_p5[i].max()
        s4 = np.median(sth_p4[i]); s5 = np.median(sth_p5[i])
        print(f'{fh:>8.2f}  {m4:>8.1f} [{lo4:>5.1f},{hi4:>5.1f}]  {s4:>8.0f}  '
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

    # ── Figure A: 1×2 lnΔZ + recovered S_thresh ────────────────────────────
    fig_a, (ax_l, ax_r) = plt.subplots(1, 2, figsize=FIGSIZE_SWEEP)

    # Left panel: ln ΔZ
    ax_l.fill_between(F_HYCEAN_SWEEP, lo_p4_lnk, hi_p4_lnk,
                      color='#5C6BC0', alpha=0.25)
    ax_l.plot(F_HYCEAN_SWEEP, med_p4_lnk, 'o-', color='#5C6BC0',
              label='P4 (M dwarfs)')
    ax_l.fill_between(F_HYCEAN_SWEEP, lo_p5_lnk, hi_p5_lnk,
                      color='#EF5350', alpha=0.25)
    ax_l.plot(F_HYCEAN_SWEEP, med_p5_lnk, 's-', color='#EF5350',
              label='P5 (FGK)')
    ax_l.set_xlabel(r'Hycean fraction $f_\mathrm{hycean}$')
    ax_l.set_ylabel(r'$\ln\Delta Z$')
    ax_l.set_title(r'Bayes factor $\ln\Delta Z$', fontsize=9)
    ax_l.legend(fontsize=7, loc='upper left')

    # Right panel: recovered S_thresh
    S_ROCKY  = COMMON['S_thresh']         # 280
    S_HYCEAN = COMMON['S_thresh_hycean']  # 435
    ax_r.fill_between(F_HYCEAN_SWEEP, lo_p4_sth, hi_p4_sth,
                      color='#5C6BC0', alpha=0.25)
    ax_r.plot(F_HYCEAN_SWEEP, med_p4_sth, 'o-', color='#5C6BC0', label='P4')
    ax_r.fill_between(F_HYCEAN_SWEEP, lo_p5_sth, hi_p5_sth,
                      color='#EF5350', alpha=0.25)
    ax_r.plot(F_HYCEAN_SWEEP, med_p5_sth, 's-', color='#EF5350', label='P5')
    ax_r.axhline(S_ROCKY, color='k', ls=':', lw=0.9,
                 label=fr'rocky $S_\mathrm{{thresh}}={S_ROCKY:.0f}$')
    ax_r.axhline(S_HYCEAN, color='k', ls='--', lw=0.9,
                 label=fr'Hycean $S_\mathrm{{thresh}}={S_HYCEAN:.0f}$')
    ax_r.set_xlabel(r'Hycean fraction $f_\mathrm{hycean}$')
    ax_r.set_ylabel(r'Recovered $\hat{S}_\mathrm{thresh}$ (W m$^{-2}$)')
    ax_r.set_title(r'Best-fit $\hat{S}_\mathrm{thresh}$', fontsize=9)
    ax_r.legend(fontsize=7, loc='best')

    for ax in (ax_l, ax_r):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(which='both', top=False, right=False)

    fig_a.suptitle(
        fr'Hybrid rocky-Hycean model, depth $\geq 60\,\mathrm{{ppm}}$, '
        fr'median $\pm$ 16--84\% of {N_TRIALS} seeds per point',
        fontsize=9, y=1.02,
    )
    fig_a.tight_layout()
    save_figure(fig_a, 'plato_hycean_fraction_lnk')

    # ── Figure B: scatter panels for key fractions ─────────────────────────
    fig_b, axes = plt.subplots(2, 3, figsize=FIGSIZE_PANELS, sharey='row')

    for col, fh in enumerate(F_HYCEAN_PANELS):
        _draw_panel(axes[0, col], results[('P4', fh)][0], 'P4', fh)
        _draw_panel(axes[1, col], results[('P5', fh)][0], 'P5', fh)
        if col > 0:
            axes[0, col].set_ylabel('')
            axes[1, col].set_ylabel('')

    fig_b.tight_layout()
    save_figure(fig_b, 'plato_hycean_fraction_panels')


if __name__ == "__main__":
    main()
