"""Chapter 3, §3.2 — radius histogram and the Fulton gap.

Left: linear-radius zoom on the small-planet regime ($R \\leq 5\\,R_\\oplus$)
per facility with the Fulton-gap band shaded.
Right: log-radius histogram covering the full range up to gas giants.

Illustrates the well-known bimodality around 1.6--2.0 $R_\\oplus$
(Fulton et al.\\ 2017) in the Kepler subsample.
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

FIGSIZE = (11, 3.8)
PARQUET = hzied_bridge.HZIED_ROOT / 'real_data' / 'data' / 'kepler_tess_confirmed.parquet'
STYLES = {'Kepler': '#5C6BC0', 'K2': '#66BB6A', 'TESS': '#EF5350'}


def _facility_short(f):
    s = str(f)
    if 'TESS' in s: return 'TESS'
    if 'K2'   in s: return 'K2'
    return 'Kepler'


def main() -> None:
    df = pd.read_parquet(PARQUET)
    df['facility'] = df['disc_facility'].fillna('').map(_facility_short)
    print(f'  loaded {len(df):,} planets')

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=FIGSIZE)

    bins_lin = np.linspace(0.3, 5.0, 60)
    for f, col in STYLES.items():
        sub = df[df['facility'] == f]
        ax_a.hist(sub['pl_rade'], bins=bins_lin, color=col, alpha=0.55,
                  edgecolor='k', lw=0.3, label=f'{f} ({len(sub)})')
    ax_a.axvspan(1.6, 2.0, color='grey', alpha=0.2, label=r'Fulton gap 1.6--2.0 $R_\oplus$')
    ax_a.set_xlabel(r'Planet radius $R_p$ ($R_\oplus$)')
    ax_a.set_ylabel('Planets per bin')
    ax_a.set_title(r'Small-planet zoom ($R_p \leq 5\,R_\oplus$)', fontsize=10)
    ax_a.legend(fontsize=8)

    bins_log = np.logspace(-0.4, 1.5, 60)
    for f, col in STYLES.items():
        sub = df[df['facility'] == f]
        ax_b.hist(sub['pl_rade'], bins=bins_log, color=col, alpha=0.55,
                  edgecolor='k', lw=0.3, label=f'{f} ({len(sub)})')
    ax_b.set_xscale('log')
    ax_b.set_xlabel(r'Planet radius $R_p$ ($R_\oplus$)')
    ax_b.set_ylabel('Planets per bin')
    ax_b.set_title('Full radius range (log)', fontsize=10)
    ax_b.legend(fontsize=8)

    for ax in (ax_a, ax_b):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save_figure(fig, 'kt_radius_gap')


if __name__ == "__main__":
    main()
