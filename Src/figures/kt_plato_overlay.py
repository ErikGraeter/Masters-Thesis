"""Chapter 3, §3.5 — real vs PLATO-forecast overlay.

Real Kepler+K2+TESS confirmed planets (grey background) with the
simulated PLATO P4 (M-dwarf, blue) and P5 (FGK, red) detectable
populations from `outputs/catalogs/` overlaid.  Uses the fiducial
`agni_updated`, x_H2O = 0.005, depth >= 60 ppm configuration to match
the multi-seed sweeps in Chapter 6.

The point of the plot is to show that the current confirmed-planet
sample and the PLATO forecast populate \\emph{different} regions of
the $R_p$--$S_\\mathrm{abs}$ plane: Kepler+TESS lives at
$S_\\mathrm{abs} \\gtrsim 500\\,\\mathrm{W\\,m^{-2}}$, whereas PLATO
fills in the cold habitable-zone regime where the HZIED test lives.
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

FIGSIZE = (10, 5.5)
PARQUET_REAL = hzied_bridge.HZIED_ROOT / 'real_data' / 'data' / 'kepler_tess_confirmed.parquet'
SIM_ROOT     = hzied_bridge.HZIED_ROOT / 'outputs' / 'catalogs'
SIM_TAG      = 'population_plato_{sample}_thresh280_agni_updated_wrr0.0050_frgh0.80_d60ppm_agesampled.parquet'

S_EARTH = 1361.0


def main() -> None:
    df = pd.read_parquet(PARQUET_REAL)
    df['S_abs'] = df['pl_insol'] * S_EARTH
    print(f'  real sample: {len(df):,} planets')

    sims = {}
    for name in ('P4', 'P5'):
        p = SIM_ROOT / SIM_TAG.format(sample=name)
        if p.exists():
            sims[name] = pd.read_parquet(p)
            print(f'  PLATO {name} simulated: {len(sims[name]):,} planets  ← {p.name}')
        else:
            print(f'  PLATO {name}: parquet missing at {p}; skipping')

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.scatter(df['S_abs'], df['pl_rade'], s=5, alpha=0.25, color='0.5',
               label=f'Real (Kepler+K2+TESS, {len(df):,})')
    for name, col in [('P4', '#5C6BC0'), ('P5', '#EF5350')]:
        if name in sims:
            s = sims[name]
            ax.scatter(s['S_abs'], s['R'], s=10, alpha=0.55,
                       color=col, label=fr'PLATO {name} simulated ({len(s)})')

    for x, ls, col, lbl in [(280, '--', 'red', r'$S_\mathrm{thresh, rocky}$'),
                            (435, ':', 'blue', r'$S_\mathrm{thresh, Hycean}$'),
                            (1361, '-', 'k', r'Earth $S_\oplus$')]:
        ax.axvline(x, color=col, ls=ls, lw=1.0, alpha=0.8, label=lbl)

    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(1e5, 1)
    ax.set_ylim(0.3, 25)
    ax.set_xlabel(r'Instellation $S_\mathrm{abs}$ (W m$^{-2}$)')
    ax.set_ylabel(r'Planet radius $R_p$ ($R_\oplus$)')
    ax.set_title('Real confirmed planets + PLATO forecast', fontsize=10)
    ax.legend(fontsize=8, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save_figure(fig, 'kt_plato_overlay')


if __name__ == "__main__":
    main()
