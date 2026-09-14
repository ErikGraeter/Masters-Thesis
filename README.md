# Master's Thesis — Erik Gräter

**Detectability of the Habitable Zone Inner-Edge Discontinuity with PLATO**
Bioverse forecasts for the PLATO target samples.

European Southern Observatory · Technical University of Munich · Department of Physics
Supervisor: Dr. Martin Schlecker · Co-supervisor: PD Dr. Mathias Garny · Submitted 2027.

---

## For reviewers

The always-current compiled PDF lives on the [`pdf-preview`](https://github.com/ErikGraeter/Masters-Thesis/tree/pdf-preview) branch as `thesis.pdf`. It is rebuilt automatically on every push to `main`.

Direct link:
`https://github.com/ErikGraeter/Masters-Thesis/raw/pdf-preview/thesis.pdf`

Comments are welcome via inline PDF annotations (e.g. Preview, Skim, Adobe Reader) — return the annotated file by email or open a GitHub issue with a section/line reference.

## For local builds

Requirements: a full TeX Live installation with `latexmk`, `biber`, and standard packages.

```bash
latexmk -pdf -output-directory=Build main.tex
```

The PDF is written to `Build/main.pdf`.

## Repository layout

```
Chapters/           Chapter .tex files (01–08)
Frontmatter/        Abstract and acknowledgements
Appendices/         Appendix material
Figures/            Graphics (generated PDFs + logos)
Bibliography/       BibLaTeX references.bib
Src/                Figure-generation Python scripts
main.tex            Entry point
metadata.tex        Title, author, dates, supervisors (edit here to update the title page)
thesis.cls          Custom document class
thesis.sty          Package definitions
```

## CI

`.github/workflows/build.yml` compiles the thesis on every push to `main` and force-pushes the resulting `thesis.pdf` to the `pdf-preview` branch so reviewers always have a stable URL to the latest build.
