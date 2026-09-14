"""Chapter 3, §3.2 — full-sample R_p vs S_abs scatter + density.

Displays all confirmed Kepler/K2/TESS planets with measured radius and
instellation from the NASA Exoplanet Archive `pscomppars` table.
Left panel: scatter coloured by discovery facility.
Right panel: 2D hexbin density with a log colour scale.

Data source
-----------
`HZIED/real_data/data/kepler_tess_confirmed.parquet`, downloaded by
`HZIED/real_data/scripts/download_confirmed_planets.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import hzied_bridge

from utils import save_figure                # noqa: E402

FIGSIZE = (12, 4.5)
PARQUET = hzied_bridge.HZIED_ROOT / 'real_data' / 'data' / 'kepler_tess_confirmed.parquet'

S_EARTH = 1361.0
STYLES = {'Kepler': ('#5C6BC0', 'o'),
          'K2':     ('#66BB6A', '^'),
          'TESS':   ('#EF5350', 's')}


def _facility_short(f):
    s = str(f)
    if 'TESS' in s: return 'TESS'
    if 'K2'   in s: return 'K2'
    return 'Kepler'


def main() -> None:
    df = pd.read_parquet(PARQUET)
    df['S_abs']    = df['pl_insol'] * S_EARTH
    df['facility'] = df['disc_facility'].fillna('').map(_facility_short)
    print(f'  loaded {len(df):,} planets')

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=FIGSIZE)

    for f, (col, mk) in STYLES.items():
        sub = df[df['facility'] == f]
        ax_a.scatter(sub['S_abs'], sub['pl_rade'], s=6, alpha=0.4,
                     color=col, marker=mk, label=f'{f} ({len(sub)})')
    for x, ls, col in [(280, '--', 'red'), (435, ':', 'blue'), (1361, '-', 'k')]:
        ax_a.axvline(x, color=col, ls=ls, lw=1.0, alpha=0.8)
    ax_a.set_xscale('log'); ax_a.set_yscale('log')
    ax_a.set_xlim(1e5, 1); ax_a.set_ylim(0.3, 25)
    ax_a.set_xlabel(r'Instellation $S_\mathrm{abs}$ (W m$^{-2}$)')
    ax_a.set_ylabel(r'Planet radius $R_p$ ($R_\oplus$)')
    ax_a.set_title('Scatter by discovery facility', fontsize=10)
    ax_a.legend(fontsize=8, loc='upper right')

    hb = ax_b.hexbin(df['S_abs'], df['pl_rade'], gridsize=45,
                     xscale='log', yscale='log',
                     cmap='viridis', mincnt=1, norm=LogNorm())
    for x, ls, col in [(280, '--', 'red'), (435, ':', 'blue'), (1361, '-', 'w')]:
        ax_b.axvline(x, color=col, ls=ls, lw=1.0, alpha=0.9)
    ax_b.set_xlim(1e5, 1); ax_b.set_ylim(0.3, 25)
    ax_b.set_xlabel(r'Instellation $S_\mathrm{abs}$ (W m$^{-2}$)')
    ax_b.set_ylabel(r'Planet radius $R_p$ ($R_\oplus$)')
    ax_b.set_title('Density (log colour scale)', fontsize=10)
    cb = fig.colorbar(hb, ax=ax_b, pad=0.02, fraction=0.045)
    cb.set_label('planets / hex')

    for ax in (ax_a, ax_b):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save_figure(fig, 'kt_full_sample_rs')


if __name__ == "__main__":
    main()
