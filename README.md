# NDLM---Ensemble

Gaussian NDLM derivations and validation workflow, organized for reproducibility.

## Repository layout

- `docs/derivations/`: compile-ready LaTeX derivations
- `docs/derivations/sections/`: section-split derivation files
- `docs/derivations/notation.yaml`: notation registry
- `scripts/extract_notation/`: notation extraction/coherence checks
- `scripts/validate/`: mathematical validators
- `tests/`: pytest tests for validators and parity checks
- `REPORT/`: audit trail and generated reports
- `archive/main_raw_2026-02-07.md`: preserved original raw notes

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Common commands

- Safe formatting:

```bash
make format
```

- Notation coherence checks:

```bash
make notation
```

- Derivation validators (machine + markdown reports):

```bash
make validate
```

- Unit tests:

```bash
make test
```

- Compile derivations PDF:

```bash
make compile
```

- Run the hardening gate (build + fatal-log scan):

```bash
bash scripts/latex_gate.sh
```

## Deterministic compile notes

Compilation target is `docs/derivations/main.tex` via `latexmk -pdf -interaction=nonstopmode -halt-on-error`.

## Extending the validators

Add a new module under `scripts/validate/` that returns a structured PASS/FAIL record,
then register it in `scripts/validate/validate_all.py` and add a corresponding pytest in `tests/`.
