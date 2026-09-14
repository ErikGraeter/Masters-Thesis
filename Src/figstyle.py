# Physical figure dimensions in inches.
# Change TEXT_WIDTH_IN once to match the final LaTeX \textwidth.
#
# This module was named ``constants.py`` originally; renamed to ``figstyle``
# to avoid shadowing HZIED's ``src/constants.py`` when the HZIED pipeline is
# imported via ``Src/hzied_bridge.py`` (HZIED's plotting module does
# ``from constants import S_EARTH, ...`` and would find this one first
# because ``Src/`` is prepended to ``sys.path`` in each figure script).

TEXT_WIDTH_IN = 5.8

FIGSIZE_FULL   = (TEXT_WIDTH_IN, 3.6)
FIGSIZE_WIDE   = (TEXT_WIDTH_IN, 3.0)
FIGSIZE_SQUARE = (0.65 * TEXT_WIDTH_IN, 0.65 * TEXT_WIDTH_IN)

# Semantic colors: keep the meaning of colors consistent across the thesis.
COLORS = {
    "fiducial":   "C0",
    "comparison": "C1",
    "highlight":  "C3",
    "neutral":    "0.4",
}
