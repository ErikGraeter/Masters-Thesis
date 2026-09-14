"""Chapter 3, §3.4 — coarse composition classes from radius alone.

Left: bar chart of the four Fulton-derived radius classes over the
full 4044-planet sample.
Right: the same classes on the HZIED plane $R_p$ vs $S_\\mathrm{abs}$,
with the rocky and Hycean $S_\\mathrm{thresh}$ overlays.

Radius classes follow the community convention:
  Rocky        R < 1.6  R_Earth
  Fulton gap   1.6 <= R < 2.0
  Sub-Neptune  2.0 <= R < 4.0
  Neptunian    4.0 <= R < 10
  Gas giant    R >= 10
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

FIGSIZE = (12, 4.5)
PARQUET = hzied_bridge.HZIED_ROOT / 'real_data' / 'data' / 'kepler_tess_confirmed.parquet'

S_EARTH = 1361.0
S_THRESH_ROCKY  = 280.
S_THRESH_HYCEAN = 435.

RADIUS_CLASSES = [
    ('Rocky',       0.0, 1.6,  '#5C6BC0'),
    ('Fulton gap',  1.6, 2.0,  '#9E9E9E'),
    ('Sub-Neptune', 2.0, 4.0,  '#43A047'),
    ('Neptunian',   4.0, 10.0, '#FB8C00'),
    ('Gas giant',   10.0, np.inf, '#EF5350'),
]


def _radius_class(r):
    for lbl, lo, hi, _ in RADIUS_CLASSES:
        if lo <= r < hi:
            return lbl
    return 'unknown'


def main() -> None:
    df = pd.read_parquet(PARQUET)
    df['S_abs']   = df['pl_insol'] * S_EARTH
    df['R_class'] = df['pl_rade'].apply(_radius_class)
    print(f'  loaded {len(df):,} planets')

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=FIGSIZE)

    # (a) bar chart
    counts = df['R_class'].value_counts().reindex([c[0] for c in RADIUS_CLASSES])
    colors = [c[3] for c in RADIUS_CLASSES]
    ax_a.bar(counts.index, counts.values, color=colors, edgecolor='k', lw=0.5)
    for i, n in enumerate(counts.values):
        ax_a.text(i, n, f' {n:,}', va='bottom', ha='center', fontsize=9)
    ax_a.set_ylabel('Planets')
    ax_a.set_title('Radius-based composition class', fontsize=10)
    ax_a.set_ylim(0, counts.max() * 1.13)
    ax_a.tick_params(axis='x', rotation=15)

    # (b) same classes on the HZIED plane
    for lbl, lo, hi, col in RADIUS_CLASSES:
        sub = df[df['R_class'] == lbl]
        ax_b.scatter(sub['S_abs'], sub['pl_rade'], s=6, alpha=0.5,
                     color=col, label=f'{lbl} ({len(sub)})')
    for x, ls, col in [(S_THRESH_ROCKY, '--', 'red'),
                       (S_THRESH_HYCEAN, ':', 'blue')]:
        ax_b.axvline(x, color=col, ls=ls, lw=1.0)
    ax_b.set_xscale('log'); ax_b.set_yscale('log')
    ax_b.set_xlim(1e5, 1); ax_b.set_ylim(0.3, 25)
    ax_b.set_xlabel(r'$S_\mathrm{abs}$ (W m$^{-2}$)')
    ax_b.set_ylabel(r'$R_p$ ($R_\oplus$)')
    ax_b.set_title('Composition classes on the HZIED plane', fontsize=10)
    ax_b.legend(fontsize=8, loc='upper right')

    for ax in (ax_a, ax_b):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save_figure(fig, 'kt_composition_classes')


if __name__ == "__main__":
    main()
