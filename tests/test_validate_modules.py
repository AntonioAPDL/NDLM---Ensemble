from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "validate"))

from validate_all import run_validators  # type: ignore


def test_all_validation_modules_pass():
    results = run_validators(seed=12345)
    assert results, "No validation results produced"
    failed = [r.name for r in results if not r.passed]
    assert not failed, f"Validation modules failed: {failed}"
