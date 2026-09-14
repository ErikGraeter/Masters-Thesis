"""Chapter 3, §3.3 — HZ-slab scatter for the current transit sample.

Zooms into the HZIED-relevant window
$S_\\mathrm{abs} \\in [50, 1500]\\,\\mathrm{W\\,m^{-2}}$,
$R_p \\leq 3\\,R_\\oplus$ and shows all confirmed planets that fall
inside. Cold and hot mean bands are overlaid \\emph{only if} at least
three planets exist on each side --- for the current catalogue the
cold side is empty and the bands are suppressed.
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

FIGSIZE = (9, 4.5)
PARQUET = hzied_bridge.HZIED_ROOT / 'real_data' / 'data' / 'kepler_tess_confirmed.parquet'

S_EARTH = 1361.0
S_MIN, S_MAX = 50., 1500.
R_MAX = 3.0
S_THRESH_ROCKY  = 280.
S_THRESH_HYCEAN = 435.
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

    hz = df[(df['S_abs'] >= S_MIN) & (df['S_abs'] <= S_MAX)
            & (df['pl_rade'] <= R_MAX)]
    print(f'  HZ-slab N = {len(hz)}')

    fig, ax = plt.subplots(figsize=FIGSIZE)
    for f, (col, mk) in STYLES.items():
        sub = hz[hz['facility'] == f]
        ax.scatter(sub['S_abs'], sub['pl_rade'], s=32, alpha=0.75,
                   color=col, marker=mk, label=f'{f} ({len(sub)})')

    cold = hz[hz['S_abs'] <= S_THRESH_ROCKY]
    hot  = hz[hz['S_abs'] >  S_THRESH_ROCKY]
    if len(cold) >= 3 and len(hot) >= 3:
        r_c = cold['pl_rade'].mean(); se_c = cold['pl_rade'].std(ddof=1) / np.sqrt(len(cold))
        r_h = hot['pl_rade'].mean();  se_h = hot['pl_rade'].std(ddof=1)  / np.sqrt(len(hot))
        ax.fill_between([S_MIN, S_THRESH_ROCKY], r_c - se_c, r_c + se_c,
                        color='steelblue', alpha=0.25)
        ax.hlines(r_c, S_MIN, S_THRESH_ROCKY, color='steelblue', lw=2,
                  label=fr'cold N={len(cold)}: $\bar R={r_c:.2f}\pm{se_c:.2f}$')
        ax.fill_between([S_THRESH_ROCKY, S_MAX], r_h - se_h, r_h + se_h,
                        color='firebrick', alpha=0.25)
        ax.hlines(r_h, S_THRESH_ROCKY, S_MAX, color='firebrick', lw=2,
                  label=fr'hot N={len(hot)}: $\bar R={r_h:.2f}\pm{se_h:.2f}$')
    else:
        ax.text(0.5, 0.95,
                fr'Cold side has only $N={len(cold)}$ planets --- '
                fr'two-mean test undefined',
                transform=ax.transAxes, ha='center', va='top',
                fontsize=9, color='steelblue', style='italic',
                bbox=dict(facecolor='white', edgecolor='0.6', alpha=0.85))

    ax.axvline(S_THRESH_ROCKY, color='red', ls='--', lw=1.0,
               label=fr'$S_\mathrm{{thresh, rocky}}={S_THRESH_ROCKY:.0f}$')
    ax.axvline(S_THRESH_HYCEAN, color='blue', ls=':', lw=1.0,
               label=fr'$S_\mathrm{{thresh, Hycean}}={S_THRESH_HYCEAN:.0f}$')

    ax.set_xscale('log')
    ax.set_xlim(S_MAX, S_MIN)
    ax.set_ylim(0.4, R_MAX + 0.2)
    ax.set_xlabel(r'Instellation $S_\mathrm{abs}$ (W m$^{-2}$)')
    ax.set_ylabel(r'Planet radius $R_p$ ($R_\oplus$)')
    ax.set_title(fr'HZ-slab: $S \in [{S_MIN:.0f},{S_MAX:.0f}]$ W m$^{{-2}}$, '
                 fr'$R \leq {R_MAX:.1f}\,R_\oplus$', fontsize=10)
    ax.legend(fontsize=8, loc='upper left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save_figure(fig, 'kt_hz_slab')


if __name__ == "__main__":
    main()
