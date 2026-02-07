#!/usr/bin/env python3

from __future__ import annotations

import math
from typing import Dict

import numpy as np

from common import ValidationResult


def log_ig_kernel(s2: float, a: float, b: float) -> float:
    return -(a + 1.0) * math.log(s2) - b / s2


def run(rng: np.random.Generator, n_trials: int = 20) -> ValidationResult:
    max_std = 0.0
    worst: Dict[str, float] = {}

    for _ in range(n_trials):
        n = int(rng.integers(5, 40))
        residuals = rng.normal(loc=0.0, scale=1.7, size=n)
        sse = float(np.sum(residuals**2))
        a0 = float(rng.uniform(1.5, 4.0))
        b0 = float(rng.uniform(0.5, 3.0))

        a1 = a0 + n / 2.0
        b1 = b0 + 0.5 * sse

        grid = np.exp(np.linspace(-3.0, 3.0, 60))
        diffs = []
        for s2 in grid:
            lp_prior_like = (-(n / 2.0) * math.log(s2) - 0.5 * sse / s2) + log_ig_kernel(s2, a0, b0)
            lp_post = log_ig_kernel(s2, a1, b1)
            diffs.append(lp_prior_like - lp_post)

        std_diff = float(np.std(diffs))
        if std_diff > max_std:
            max_std = std_diff
            worst = {
                "n": float(n),
                "sse": sse,
                "a0": a0,
                "b0": b0,
                "a1": a1,
                "b1": b1,
                "std_diff": std_diff,
            }

    passed = max_std < 1e-10
    details = (
        "IG posterior-kernel equivalence failed"
        if not passed
        else "IG conjugate posterior kernel matches prior*likelihood up to additive constant."
    )

    return ValidationResult(
        name="observation_variance_ig_conjugacy",
        passed=passed,
        equation_refs="docs/derivations/sections/04_static_conditionals.tex:eq:cond_sigma",
        details=details,
        diagnostics={"max_std_of_kernel_difference": max_std, "worst_case": worst},
    )
