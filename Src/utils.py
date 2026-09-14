from pathlib import Path
import matplotlib.pyplot as plt

# Src/ sits one level below the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR   = PROJECT_ROOT / "Figures" / "generated"
STYLE_FILE   = PROJECT_ROOT / "thesis.mplstyle"


def use_thesis_style():
    """Load the project-wide Matplotlib style from thesis.mplstyle."""
    plt.style.use(STYLE_FILE)


def save_figure(fig, name, png=True):
    """Save `fig` to Figures/generated/<name>.pdf (and optional .png)."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{name}.pdf")
    if png:
        fig.savefig(FIGURE_DIR / f"{name}.png", dpi=300)
