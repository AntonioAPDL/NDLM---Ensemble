#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import numpy as np

from common import ValidationResult
from conditional_ig import run as run_conditional_ig
from conditional_iw import run as run_conditional_iw
from joint_marginal_consistency import run as run_joint_marginal
from kalman_bruteforce import run as run_kalman_bruteforce
from lambda_grad_hess import run as run_lambda_grad_hess
from likelihood_normalization import run as run_likelihood_normalization
from parity_with_exdqlm import run_parity, write_markdown as write_parity_markdown
from replicate_assimilation import run as run_replicate_assimilation


def run_validators(seed: int = 20260207) -> List[ValidationResult]:
    rng = np.random.default_rng(seed)
    return [
        run_likelihood_normalization(rng),
        run_joint_marginal(rng),
        run_conditional_ig(rng),
        run_conditional_iw(rng),
        run_lambda_grad_hess(rng),
        run_kalman_bruteforce(rng),
        run_replicate_assimilation(rng),
    ]


def write_validation_markdown(results: List[ValidationResult], output_path: Path) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    pass_count = sum(1 for r in results if r.passed)
    fail_count = len(results) - pass_count

    lines: List[str] = []
    lines.append("# Validation Results")
    lines.append("")
    lines.append(f"- Timestamp: {ts}")
    lines.append(f"- Total checks: {len(results)}")
    lines.append(f"- PASS: {pass_count}")
    lines.append(f"- FAIL: {fail_count}")
    lines.append("")

    lines.append("## Validated items")
    lines.append("")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"- {result.name}: {status}")
        lines.append(f"  equation refs: {result.equation_refs}")
        lines.append(f"  details: {result.details}")
        lines.append(f"  diagnostics: {json.dumps(result.diagnostics, sort_keys=True)}")
    lines.append("")

    lines.append("## Code links")
    lines.append("")
    lines.append("- scripts/validate/validate_all.py")
    lines.append("- scripts/validate/likelihood_normalization.py")
    lines.append("- scripts/validate/joint_marginal_consistency.py")
    lines.append("- scripts/validate/conditional_ig.py")
    lines.append("- scripts/validate/conditional_iw.py")
    lines.append("- scripts/validate/lambda_grad_hess.py")
    lines.append("- scripts/validate/kalman_bruteforce.py")
    lines.append("- scripts/validate/replicate_assimilation.py")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    parser.add_argument(
        "--reference-main",
        type=Path,
        default=Path("/data/muscat_data/jaguir26/exDQLM---Ensemble/main.tex"),
    )
    parser.add_argument(
        "--ndlm-sections-root",
        type=Path,
        default=Path("docs/derivations/sections"),
    )
    parser.add_argument(
        "--parity-json-output",
        type=Path,
        default=Path("REPORT/parity_with_exdqlm.json"),
    )
    parser.add_argument(
        "--parity-md-output",
        type=Path,
        default=Path("REPORT/03_parity_with_exDQLM.md"),
    )
    args = parser.parse_args()

    results = run_validators()
    pass_all = all(r.passed for r in results)

    parity_report = run_parity(args.reference_main, args.ndlm_sections_root)
    args.parity_json_output.parent.mkdir(parents=True, exist_ok=True)
    args.parity_json_output.write_text(
        json.dumps(parity_report, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_parity_markdown(parity_report, args.parity_md_output)

    payload = {
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "all_passed": pass_all,
        },
        "results": [r.to_dict() for r in results],
        "parity": parity_report,
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    write_validation_markdown(results, args.md_output)

    print(f"validation summary: {payload['summary']}")


if __name__ == "__main__":
    main()
