from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "validate"))

from parity_with_exdqlm import run_parity  # type: ignore


def test_expected_parity_with_reference_repo():
    report = run_parity(
        Path("/data/muscat_data/jaguir26/exDQLM---Ensemble/main.tex"),
        REPO_ROOT / "docs" / "derivations" / "sections",
    )
    assert report["status"] == "PASS", report
