"""Chapter 3, §3.4 — mass--radius diagram, direct-mass subset.

Restricts to planets with `pl_bmassprov = 'Mass'` (directly measured
mass, no M--R inferred values).  Left panel: M--R diagram with
Zeng+2016 rocky, Zeng+2019 pure-water and a rough H/He-envelope
composition track.  Points are flagged as either sitting below the
pure-water curve (may be rocky) or above it (must carry an H/He or
steam envelope).  Right panel: the same flag projected onto the
$R_p$ vs $S_\\mathrm{abs}$ plane so the composition proxy can be
read directly against the HZIED test region.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import hzied_bridge

from utils import save_figure                # noqa: E402

FIGSIZE = (12, 5.0)
PARQUET = hzied_bridge.HZIED_ROOT / 'real_data' / 'data' / 'kepler_tess_confirmed.parquet'

S_EARTH = 1361.0
S_THRESH_ROCKY  = 280.
S_THRESH_HYCEAN = 435.


def main() -> None:
    df = pd.read_parquet(PARQUET)
    df['S_abs'] = df['pl_insol'] * S_EARTH

    gold = df[(df['pl_bmassprov'] == 'Mass') & df['pl_masse'].notna()].copy()
    gold = gold[(gold['pl_masse'] > 0) & (gold['pl_masse'] < 1e4)]
    print(f'  direct-mass planets: {len(gold):,}')

    # Zeng composition tracks (power-law fits)
    M_grid  = np.logspace(-1, 2, 200)
    R_rock  = M_grid ** 0.27
    R_water = M_grid ** 0.30 * 1.30
    R_hhe   = M_grid ** 0.59 * 1.60

    R_water_at_mass = np.interp(gold['pl_masse'], M_grid, R_water)
    gold['above_water'] = gold['pl_rade'] > R_water_at_mass

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=FIGSIZE)

    ax_a.scatter(gold.loc[~gold['above_water'], 'pl_masse'],
                 gold.loc[~gold['above_water'], 'pl_rade'],
                 s=10, alpha=0.5, color='#5C6BC0',
                 label=fr'$\leq$ water track (may be rocky, {(~gold["above_water"]).sum()})')
    ax_a.scatter(gold.loc[gold['above_water'], 'pl_masse'],
                 gold.loc[gold['above_water'], 'pl_rade'],
                 s=10, alpha=0.5, color='#EF5350',
                 label=fr'$>$ water track (must have envelope, {gold["above_water"].sum()})')
    ax_a.plot(M_grid, R_rock,  'k-',  lw=1.2, label='Earth-like rocky (Zeng+16)')
    ax_a.plot(M_grid, R_water, 'b--', lw=1.2, label='100 % water (Zeng+19)')
    ax_a.plot(M_grid, R_hhe,   'g:',  lw=1.2, label='H/He envelope (rough)')
    ax_a.set_xscale('log'); ax_a.set_yscale('log')
    ax_a.set_xlim(0.1, 1e3); ax_a.set_ylim(0.4, 25)
    ax_a.set_xlabel(r'$M_p$ ($M_\oplus$)')
    ax_a.set_ylabel(r'$R_p$ ($R_\oplus$)')
    ax_a.set_title(f'M--R, direct mass only ({len(gold):,})', fontsize=10)
    ax_a.legend(fontsize=7, loc='lower right')

    ax_b.scatter(gold.loc[~gold['above_water'], 'S_abs'],
                 gold.loc[~gold['above_water'], 'pl_rade'],
                 s=10, alpha=0.5, color='#5C6BC0',
                 label=fr'$\leq$ water track ({(~gold["above_water"]).sum()})')
    ax_b.scatter(gold.loc[gold['above_water'], 'S_abs'],
                 gold.loc[gold['above_water'], 'pl_rade'],
                 s=10, alpha=0.5, color='#EF5350',
                 label=fr'$>$ water track ({gold["above_water"].sum()})')
    ax_b.axvline(S_THRESH_ROCKY, color='red', ls='--', lw=1.0)
    ax_b.axvline(S_THRESH_HYCEAN, color='blue', ls=':', lw=1.0)
    ax_b.set_xscale('log'); ax_b.set_yscale('log')
    ax_b.set_xlim(1e5, 1); ax_b.set_ylim(0.3, 25)
    ax_b.set_xlabel(r'$S_\mathrm{abs}$ (W m$^{-2}$)')
    ax_b.set_ylabel(r'$R_p$ ($R_\oplus$)')
    ax_b.set_title('HZIED plane, composition proxy', fontsize=10)
    ax_b.legend(fontsize=7, loc='upper right')

    for ax in (ax_a, ax_b):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save_figure(fig, 'kt_composition_mr')


if __name__ == "__main__":
    main()
