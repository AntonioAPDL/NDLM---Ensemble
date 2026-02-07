from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "extract_notation"))

from check_notation import run_checks  # type: ignore


def test_notation_checks_have_no_critical_failures():
    summary, _raw = run_checks(
        REPO_ROOT / "docs" / "derivations",
        REPO_ROOT / "docs" / "derivations" / "notation.yaml",
    )
    undefined = [f for f in summary.findings if f.kind == "undefined_macro"]
    assert not undefined, f"Undefined macros found: {undefined}"
