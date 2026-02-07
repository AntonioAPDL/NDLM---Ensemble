.PHONY: format notation validate test compile clean

format:
	bash scripts/format_safe.sh

notation:
	python3 scripts/extract_notation/check_notation.py \
		--tex-root docs/derivations \
		--notation docs/derivations/notation.yaml \
		--json-output REPORT/notation_checks.json \
		--md-output REPORT/02_notation_checks.md

validate:
	python3 scripts/validate/validate_all.py \
		--json-output REPORT/validation_results.json \
		--md-output REPORT/04_validation_results.md

test:
	pytest -q

compile:
	cd docs/derivations && PATH="$(CURDIR)/scripts/bin:$$PATH" latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	find . -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.fls' -o -name '*.fdb_latexmk' -o -name '*.synctex.gz' -o -name '*.run.xml' -o -name '*.pdf' \) -delete
