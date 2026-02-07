#!/usr/bin/env python3
"""Notation extraction + coherence checks for LaTeX derivation files."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

import yaml


# Common LaTeX commands we treat as built-in/allowed.
ALLOWED_COMMANDS: Set[str] = {
    "documentclass",
    "usepackage",
    "input",
    "title",
    "date",
    "begin",
    "end",
    "maketitle",
    "tableofcontents",
    "section",
    "subsection",
    "subsubsection",
    "section*",
    "paragraph",
    "label",
    "ref",
    "eqref",
    "text",
    "texttt",
    "textrm",
    "textbf",
    "textit",
    "item",
    "itemize",
    "enumerate",
    "left",
    "right",
    "big",
    "Big",
    "quad",
    "qquad",
    "cdot",
    "times",
    "sum",
    "prod",
    "frac",
    "sqrt",
    "log",
    "exp",
    "sim",
    "propto",
    "mid",
    "in",
    "dots",
    "vdots",
    "ldots",
    "to",
    "top",
    "mathbb",
    "mathcal",
    "mathrm",
    "mathbf",
    "bm",
    "tilde",
    "hat",
    "bar",
    "oplus",
    "pm",
    "ge",
    "le",
    "text{",  # harmless fallback if parser catches partially
    "newcommand",
    "DeclareMathOperator",
    "hline",
    "cline",
    "multicolumn",
    "caption",
    "centering",
    "rule",
    "small",
    "footnotesize",
    "normalsize",
    "leftmargin",
    # Greek and common symbols
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "varepsilon",
    "zeta",
    "eta",
    "theta",
    "vartheta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "pi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "varphi",
    "chi",
    "psi",
    "omega",
    "Theta",
    "Lambda",
    "Sigma",
    "Phi",
    "Psi",
    "Omega",
    # Misc math commands frequently present in derivations.
    "approx",
    "equiv",
    "cup",
    "cap",
    "leftarrow",
    "rightarrow",
    "hspace",
    "mathsf",
    "stackrel",
    "arabic",
}

MACRO_DEF_PATTERNS = [
    re.compile(r"\\newcommand\{\\([A-Za-z]+)\}"),
    re.compile(r"\\DeclareMathOperator\{\\([A-Za-z]+)\}"),
    re.compile(r"\\def\\([A-Za-z]+)\b"),
]

COMMAND_USE_RE = re.compile(r"\\([A-Za-z]+)")
INLINE_MATH_RE = re.compile(r"\$(.+?)\$", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
PAREN_MATH_RE = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
ENV_MATH_RE = re.compile(
    r"\\begin\{(align\*?|equation\*?|multline\*?|gather\*?|split)\}(.+?)\\end\{\1\}",
    re.DOTALL,
)
INDEXED_RE = re.compile(r"(\\?[A-Za-z]+)\s*(?:\^\{[^{}]*\}|\^[A-Za-z0-9])?\s*_\{([^{}]+)\}")
INDEXED_SIMPLE_RE = re.compile(r"(\\?[A-Za-z]+)\s*(?:\^\{[^{}]*\}|\^[A-Za-z0-9])?\s*_([A-Za-z0-9])")

STYLE_MACROS = {"bm", "tilde", "hat", "bar", "mathcal", "mathbb", "mathrm"}
INDEX_BASE_IGNORES = {
    "sum",
    "prod",
    "frac",
    "log",
    "exp",
    "tr",
    "diag",
    "BlockDiag",
    "ELBO",
    "KL",
    "label",
    "eqref",
    "ref",
}
INDEX_CHECK_BASES = {
    "x",
    "y",
    "z",
    "theta",
    "delta",
    "psi",
    "zeta",
    "alpha",
    "beta",
    "sigma",
    "lambda",
    "mu",
    "h",
    "r",
    "e",
    "F",
    "G",
    "M",
    "W",
    "m",
    "C",
    "a",
    "R",
}


@dataclass
class Finding:
    kind: str
    detail: str
    location: str


@dataclass
class NotationSummary:
    tex_files: int
    defined_macros: int
    used_macros: int
    undefined_macros: int
    registry_symbols: int
    extracted_indexed_bases: int
    findings: List[Finding]


def strip_comments(text: str) -> str:
    # Remove unescaped comments.
    return re.sub(r"(?<!\\)%.*", "", text)


def read_tex_files(tex_root: Path) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for path in sorted(tex_root.rglob("*.tex")):
        rel = str(path)
        files[rel] = strip_comments(path.read_text(encoding="utf-8"))
    return files


def extract_defined_macros(text: str) -> Set[str]:
    out: Set[str] = set()
    for pattern in MACRO_DEF_PATTERNS:
        out.update(pattern.findall(text))
    return out


def extract_used_macros(text: str) -> Counter:
    return Counter(COMMAND_USE_RE.findall(text))


def extract_math_chunks(text: str) -> List[str]:
    chunks: List[str] = []
    chunks.extend(INLINE_MATH_RE.findall(text))
    chunks.extend(DISPLAY_MATH_RE.findall(text))
    chunks.extend(PAREN_MATH_RE.findall(text))
    for _env, body in ENV_MATH_RE.findall(text):
        chunks.append(body)

    cleaned: List[str] = []
    for chunk in chunks:
        tmp = re.sub(r"\\label\{[^}]+\}", " ", chunk)
        tmp = re.sub(r"\\eqref\{[^}]+\}", " ", tmp)
        cleaned.append(tmp)
    return cleaned


def parse_registry(path: Path) -> Tuple[List[dict], Dict[str, List[dict]]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    symbols = data.get("symbols", []) if isinstance(data, dict) else []
    by_symbol: Dict[str, List[dict]] = defaultdict(list)
    for entry in symbols:
        symbol = str(entry.get("symbol", "")).strip()
        if symbol:
            by_symbol[symbol].append(entry)
    return symbols, by_symbol


def canonical_base(token: str) -> str:
    token = token.strip()
    if token.startswith("\\"):
        token = token[1:]
    return token


def latex_entry_base(entry_text: str) -> str:
    """Extract a notation base from a latex registry entry."""
    left = entry_text.split("_")[0]
    left = left.replace("{", " ").replace("}", " ")
    tokens = re.findall(r"\\[A-Za-z]+|[A-Za-z]+", left)
    for tok in tokens:
        base = canonical_base(tok)
        if base in STYLE_MACROS:
            continue
        return base
    return canonical_base(left.strip())


def index_parts(raw_index: str) -> Tuple[str, ...]:
    parts = [p.strip() for p in raw_index.split(",") if p.strip()]
    return tuple(parts) if parts else (raw_index.strip(),)


def extract_index_usage(math_chunks: Iterable[str]) -> Dict[str, Set[Tuple[str, ...]]]:
    usage: Dict[str, Set[Tuple[str, ...]]] = defaultdict(set)
    for chunk in math_chunks:
        for base, idx in INDEXED_RE.findall(chunk):
            canon = canonical_base(base)
            if canon in INDEX_BASE_IGNORES:
                continue
            usage[canon].add(index_parts(idx))
        for base, idx in INDEXED_SIMPLE_RE.findall(chunk):
            canon = canonical_base(base)
            if canon in INDEX_BASE_IGNORES:
                continue
            usage[canon].add((idx,))
    return usage


def registry_base_indexing(symbol_entry: dict) -> Set[int]:
    indexing = str(symbol_entry.get("indexing", "")).strip()
    if not indexing:
        return set()
    # Heuristic: support alternative index signatures split by "or".
    arities: Set[int] = set()
    segments = [seg.strip() for seg in re.split(r"\bor\b", indexing) if seg.strip()]
    for seg in segments:
        axes = set(re.findall(r"\b([A-Za-z])\s*=", seg))
        if axes:
            arities.add(len(axes))
    return arities


def run_checks(tex_root: Path, notation_path: Path) -> Tuple[NotationSummary, dict]:
    files = read_tex_files(tex_root)

    defined_macros: Set[str] = set()
    used_macros: Counter = Counter()
    all_math_chunks: List[str] = []
    for text in files.values():
        defined_macros.update(extract_defined_macros(text))
        used_macros.update(extract_used_macros(text))
        all_math_chunks.extend(extract_math_chunks(text))

    symbols, registry_by_symbol = parse_registry(notation_path)

    findings: List[Finding] = []

    undefined = sorted(
        m
        for m in used_macros
        if m not in defined_macros and m not in ALLOWED_COMMANDS
    )
    for macro in undefined:
        findings.append(
            Finding(
                kind="undefined_macro",
                detail=f"Macro \\{macro} is used but not defined in project macros/allowed set.",
                location="docs/derivations/*.tex",
            )
        )

    # Registry duplicate symbol meanings.
    for symbol, entries in registry_by_symbol.items():
        meanings = {str(e.get("meaning", "")).strip() for e in entries}
        if len(entries) > 1 and len(meanings) > 1:
            findings.append(
                Finding(
                    kind="registry_conflict",
                    detail=f"Symbol '{symbol}' has multiple meanings: {sorted(meanings)}",
                    location="docs/derivations/notation.yaml",
                )
            )

    # Indexed usage consistency.
    usage = extract_index_usage(all_math_chunks)
    registry_base_to_index_arity: Dict[str, Set[int]] = defaultdict(set)
    for entry in symbols:
        raw_entry = str(entry.get("latex", entry.get("symbol", "")))
        base = latex_entry_base(raw_entry)
        registry_base_to_index_arity[base].update(registry_base_indexing(entry))

    for base, forms in sorted(usage.items()):
        if base not in INDEX_CHECK_BASES:
            continue
        arities = {len(f) for f in forms}
        if len(arities) > 1:
            allowed_arities = registry_base_to_index_arity.get(base, set())
            if not allowed_arities or not arities.issubset(allowed_arities):
                findings.append(
                    Finding(
                        kind="index_inconsistency",
                        detail=(
                            f"Base symbol '{base}' appears with multiple index arities {sorted(arities)} "
                            f"and registry allows {sorted(allowed_arities) if allowed_arities else 'none'}"
                        ),
                        location="docs/derivations/*.tex",
                    )
                )

    # Registry coverage: indexed symbols in tex not represented in registry.
    registry_base_symbols = {
        latex_entry_base(str(e.get("latex", e.get("symbol", "")))
        )
        for e in symbols
        if str(e.get("latex", e.get("symbol", ""))).strip()
    }
    coverage_check_bases = INDEX_CHECK_BASES.union({"SSE", "N"})
    for base in sorted(usage):
        if base not in coverage_check_bases:
            continue
        if base not in registry_base_symbols:
            findings.append(
                Finding(
                    kind="registry_missing_symbol",
                    detail=f"Indexed base symbol '{base}' appears in LaTeX but is absent in notation registry.",
                    location="docs/derivations/notation.yaml",
                )
            )

    # Parameter naming inconsistency check (sigma vs tau)
    joined_math = "\n".join(all_math_chunks)
    uses_sigma = bool(re.search(r"\\sigma", joined_math))
    uses_tau = bool(re.search(r"\\tau", joined_math))
    if uses_sigma and uses_tau:
        findings.append(
            Finding(
                kind="parameter_name_conflict",
                detail="Both \\sigma and \\tau appear in mathematical expressions; verify they are intentionally distinct.",
                location="docs/derivations/*.tex",
            )
        )

    summary = NotationSummary(
        tex_files=len(files),
        defined_macros=len(defined_macros),
        used_macros=len(used_macros),
        undefined_macros=len(undefined),
        registry_symbols=len(symbols),
        extracted_indexed_bases=len(usage),
        findings=findings,
    )

    raw = {
        "files": sorted(files.keys()),
        "defined_macros": sorted(defined_macros),
        "used_macros": used_macros,
        "undefined_macros": undefined,
        "index_usage": {k: [list(v) for v in sorted(vals)] for k, vals in sorted(usage.items())},
        "registry_symbol_count": len(symbols),
        "findings": [asdict(f) for f in findings],
    }
    return summary, raw


def write_markdown(summary: NotationSummary, raw: dict, output_path: Path) -> None:
    lines: List[str] = []
    lines.append("# Notation Coherence Checks")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- TeX files scanned: {summary.tex_files}")
    lines.append(f"- Defined macros: {summary.defined_macros}")
    lines.append(f"- Used macros: {summary.used_macros}")
    lines.append(f"- Undefined macros: {summary.undefined_macros}")
    lines.append(f"- Registry symbol entries: {summary.registry_symbols}")
    lines.append(f"- Indexed symbol bases extracted: {summary.extracted_indexed_bases}")
    lines.append(f"- Findings: {len(summary.findings)}")
    lines.append("")

    lines.append("## Undefined macros")
    lines.append("")
    undefined = raw.get("undefined_macros", [])
    if undefined:
        for macro in undefined:
            lines.append(f"- `\\{macro}`")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    if summary.findings:
        for finding in summary.findings:
            lines.append(f"- [{finding.kind}] {finding.detail} ({finding.location})")
    else:
        lines.append("- No conflicts detected.")
    lines.append("")

    lines.append("## Indexed symbol usage snapshot")
    lines.append("")
    lines.append("```text")
    for base, forms in raw.get("index_usage", {}).items():
        lines.append(f"{base}: {forms}")
    lines.append("```")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tex-root", type=Path, required=True)
    parser.add_argument("--notation", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    args = parser.parse_args()

    summary, raw = run_checks(args.tex_root, args.notation)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(
            {
                "summary": {
                    "tex_files": summary.tex_files,
                    "defined_macros": summary.defined_macros,
                    "used_macros": summary.used_macros,
                    "undefined_macros": summary.undefined_macros,
                    "registry_symbols": summary.registry_symbols,
                    "extracted_indexed_bases": summary.extracted_indexed_bases,
                    "findings": len(summary.findings),
                },
                "raw": {
                    **raw,
                    "used_macros": dict(raw["used_macros"]),
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    write_markdown(summary, raw, args.md_output)

    if summary.findings:
        print(f"Notation checks completed with {len(summary.findings)} finding(s).")
    else:
        print("Notation checks passed with no findings.")


if __name__ == "__main__":
    main()
