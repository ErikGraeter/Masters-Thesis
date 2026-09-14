.PHONY: thesis figures clean

# Build the thesis PDF. latexmkrc controls compiler (LuaLaTeX) and out_dir.
thesis:
	latexmk main.tex

# Regenerate every figure script under Src/figures/.
# Add a new figure by dropping a script into Src/figures/ that writes its
# output via save_figure(..) from Src/utils.py.
figures:
	@if ls Src/figures/*.py >/dev/null 2>&1; then \
		for f in Src/figures/*.py; do \
			echo "→ $$f"; \
			python "$$f" || exit 1; \
		done; \
	else \
		echo "No figure scripts in Src/figures/."; \
	fi

clean:
	latexmk -C -outdir=Build
	rm -rf Build
