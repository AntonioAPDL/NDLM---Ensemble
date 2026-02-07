# Structure Mapping: exDQLM (reference) -> NDLM (target)

## Scope

- Reference repo (read-only): `/data/muscat_data/jaguir26/exDQLM---Ensemble`
- Target repo: `/data/muscat_data/jaguir26/NDLM---Ensemble`
- Date: 2026-02-07

## Reference inventory (exDQLM)

Observed layout:

- Single LaTeX manuscript: `main.tex`
- Generated artifacts mixed in root: `main.pdf`, `main.aux`, `main.log`, `main.out`
- Minimal hygiene file: `.gitignore`
- No explicit scripts/tests/Makefile in repository root

Derivation style inferred from `main.tex`:

- Monolithic article with package preamble + macro block
- Section order:
  1. Notation
  2. Model A/B/C
  3. Augmentation and full conditionals
  4. IW/Wishart blocks
  5. Algorithms (MCMC + VB)
  6. ELBO decomposition
- Heavy equation labeling and source-wise derivation structure

## Current NDLM inventory (before reorganization)

Observed layout:

- Single raw notes file named `main.tex` (not compilable LaTeX manuscript)
- No scripts/tests/automation/hygiene files
- Content already contains intended Gaussian NDLM sections (Notation, Model A/B/C, Joint, FFBS, conditionals, MCMC, VB, ELBO, validation checklist)

## Mapping table

| Reference major section / artifact | NDLM current equivalent | Target NDLM path after reorg | Action |
|---|---|---|---|
| `main.tex` preamble/macros + sectioned manuscript | Raw mixed-format notes in `main.tex` | `docs/derivations/main.tex`, `docs/derivations/macros.tex`, `docs/derivations/sections/*.tex` | Create clean multi-file manuscript; preserve semantics; archive raw source |
| Notation and dimensions | Present in raw notes (`Section 1`) | `docs/derivations/sections/01_notation_and_model.tex` + `docs/derivations/notation.yaml` | Normalize notation and add machine-readable registry |
| Model A/B/C hierarchy | Present in raw notes | `docs/derivations/sections/01_notation_and_model.tex` and `docs/derivations/sections/02_joint_density.tex` | Keep hierarchy; adapt to Gaussian likelihood |
| Full conditional derivations | Present in raw notes (`Section 3/4`) | `docs/derivations/sections/03_state_posterior_ffbs.tex` and `docs/derivations/sections/04_static_conditionals.tex` | Convert into compile-ready LaTeX with equation labels |
| Algorithms (MCMC + VB) | Present in raw notes (`Section 5/6`) | `docs/derivations/sections/05_mcmc.tex`, `docs/derivations/sections/06_vb_cavi.tex` | Preserve algorithm structure |
| ELBO decomposition | Present in raw notes (`Section 7`) | `docs/derivations/sections/07_elbo.tex` | Keep trace/logdet decomposition |
| Computational notes + validation checklist | Present in raw notes (`Section 8`) | `docs/derivations/sections/08_computational_notes.tex` | Keep computability-focused constraints |
| Posterior predictive + sufficient-statistics sections | Present in raw notes (`Section 9/10`) | `docs/derivations/sections/09_predictive.tex`, `docs/derivations/sections/10_sufficient_statistics.tex` | Preserve formulas and implementation orientation |
| Repo hygiene (`.gitignore`) | Missing | `.gitignore`, `.editorconfig` | Add |
| Build/test entrypoints | Missing | `Makefile` | Add (`format`, `validate`, `test`, `compile`) |
| Validation implementation | Missing | `scripts/validate/`, `tests/` | Add rigorous symbolic/numeric checks |
| Notation extraction/coherence checks | Missing | `scripts/extract_notation/` | Add automated checks + reports |
| Audit trail | Missing | `REPORT/*.md` | Add incremental reports |

## Notes on fidelity

- Reference repo is monolithic; target NDLM will be modularized for reproducibility while preserving the same derivational flow.
- Main conceptual delta is enforced as requested: Gaussian NDLM likelihood replaces exAL-specific likelihood/augmentation blocks.
