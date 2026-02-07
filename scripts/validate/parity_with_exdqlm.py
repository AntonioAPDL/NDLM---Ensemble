#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


SECTION_RE = re.compile(r"^\\section\{(.+?)\}", re.MULTILINE)
SUBSECTION_RE = re.compile(r"^\\subsection\{(.+?)\}", re.MULTILINE)
ENV_RE = re.compile(
    r"\\begin\{(align\*?|equation\*?|multline\*?)\}(.+?)\\end\{\1\}",
    re.DOTALL,
)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")


def canonicalize(tex: str) -> str:
    out = tex
    out = out.replace("\\given", "\\mid")
    out = out.replace("\\!", "")
    out = out.replace("\\;", "")
    out = out.replace("\\big", "")
    out = out.replace("\\Big", "")
    out = out.replace("\\bigg", "")
    out = out.replace("\\Bigg", "")
    out = re.sub(r"\s+", "", out)
    out = out.replace("\n", "")
    return out


def read_tex(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_sections(tex: str) -> List[str]:
    return SECTION_RE.findall(tex)


def collect_subsections(tex: str) -> List[str]:
    return SUBSECTION_RE.findall(tex)


def labeled_equations(tex: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for _env, body in ENV_RE.findall(tex):
        parts = re.split(r"\\\\", body)
        for part in parts:
            labels = LABEL_RE.findall(part)
            if not labels:
                continue
            part_c = canonicalize(part)
            for label in labels:
                out[label] = part_c
    return out


def run_parity(reference_main: Path, ndlm_sections_root: Path) -> Dict[str, object]:
    ref_tex = read_tex(reference_main)
    ndlm_tex_parts: List[str] = []
    for path in sorted(ndlm_sections_root.glob("*.tex")):
        ndlm_tex_parts.append(read_tex(path))
    ndlm_tex = "\n".join(ndlm_tex_parts)

    ref_sections = collect_sections(ref_tex)
    ndlm_sections = collect_sections(ndlm_tex)
    ref_headings = ref_sections + collect_subsections(ref_tex)
    ndlm_headings = ndlm_sections + collect_subsections(ndlm_tex)

    ref_eq = labeled_equations(ref_tex)
    ndlm_eq = labeled_equations(ndlm_tex)

    shared_labels = ["eq:A_theta", "eq:A_zeta", "eq:A_psi", "eq:B_delta"]
    expected_different_labels = ["eq:A_obs", "eq:B_obs", "eq:C_obs"]

    shared_matches: List[str] = []
    shared_mismatches: List[str] = []
    for label in shared_labels:
        if label not in ref_eq or label not in ndlm_eq:
            shared_mismatches.append(f"{label} (missing in one repo)")
            continue
        if ref_eq[label] == ndlm_eq[label]:
            shared_matches.append(label)
        else:
            shared_mismatches.append(label)

    expected_differences_ok: List[str] = []
    unexpected_equal: List[str] = []
    for label in expected_different_labels:
        if label not in ref_eq or label not in ndlm_eq:
            unexpected_equal.append(f"{label} (missing in one repo)")
            continue
        if ref_eq[label] != ndlm_eq[label]:
            expected_differences_ok.append(label)
        else:
            unexpected_equal.append(label)

    # Section-level fuzzy parity by keyword overlap.
    keywords = [
        "Notation",
        "Model A",
        "Model B",
        "Model C",
        "Full conditional",
        "Algorithm",
        "Mean-field",
        "ELBO",
    ]
    section_matches: List[Tuple[str, bool]] = []
    for kw in keywords:
        ref_has = any(kw.lower() in s.lower() for s in ref_headings)
        ndlm_has = any(kw.lower() in s.lower() for s in ndlm_headings)
        section_matches.append((kw, ref_has and ndlm_has))

    unexpected_differences = []
    if shared_mismatches:
        unexpected_differences.extend(shared_mismatches)
    if unexpected_equal:
        unexpected_differences.extend(unexpected_equal)

    return {
        "ref_sections_count": len(ref_sections),
        "ndlm_sections_count": len(ndlm_sections),
        "section_keyword_matches": [{"keyword": k, "matched": m} for k, m in section_matches],
        "shared_equation_labels_expected_equal": shared_labels,
        "shared_equation_labels_matched": shared_matches,
        "expected_likelihood_difference_labels": expected_different_labels,
        "expected_likelihood_difference_confirmed": expected_differences_ok,
        "unexpected_differences": unexpected_differences,
        "status": "PASS" if not unexpected_differences else "FAIL",
    }


def write_markdown(report: Dict[str, object], output_path: Path) -> None:
    lines: List[str] = []
    lines.append("# Parity With exDQLM")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Status: {report['status']}")
    lines.append(f"- exDQLM sections: {report['ref_sections_count']}")
    lines.append(f"- NDLM sections: {report['ndlm_sections_count']}")
    lines.append("")

    lines.append("## Matched section themes")
    lines.append("")
    for row in report["section_keyword_matches"]:  # type: ignore[index]
        mark = "YES" if row["matched"] else "NO"
        lines.append(f"- {row['keyword']}: {mark}")
    lines.append("")

    lines.append("## Equation labels expected to match")
    lines.append("")
    for label in report["shared_equation_labels_matched"]:  # type: ignore[index]
        lines.append(f"- {label}: matched")
    missing_or_mismatch = set(report["shared_equation_labels_expected_equal"]) - set(report["shared_equation_labels_matched"])  # type: ignore[index]
    for label in sorted(missing_or_mismatch):
        lines.append(f"- {label}: mismatch or missing")
    lines.append("")

    lines.append("## Expected likelihood differences")
    lines.append("")
    for label in report["expected_likelihood_difference_confirmed"]:  # type: ignore[index]
        lines.append(f"- {label}: confirmed different (expected)")
    not_confirmed = set(report["expected_likelihood_difference_labels"]) - set(report["expected_likelihood_difference_confirmed"])  # type: ignore[index]
    for label in sorted(not_confirmed):
        lines.append(f"- {label}: not confirmed (unexpected)")
    lines.append("")

    lines.append("## Unexpected differences")
    lines.append("")
    unexpected = report["unexpected_differences"]  # type: ignore[index]
    if unexpected:
        for item in unexpected:
            lines.append(f"- {item}")
    else:
        lines.append("- None")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-main", type=Path, required=True)
    parser.add_argument("--ndlm-sections-root", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    args = parser.parse_args()

    report = run_parity(args.reference_main, args.ndlm_sections_root)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report, args.md_output)

    print(f"parity status: {report['status']}")


if __name__ == "__main__":
    main()
