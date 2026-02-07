#!/usr/bin/env python3

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
from scipy.integrate import quad

from common import ValidationResult


def normal_pdf(y: float, mu: float, sigma2: float) -> float:
    return math.exp(-0.5 * (y - mu) ** 2 / sigma2) / math.sqrt(2.0 * math.pi * sigma2)


def run(rng: np.random.Generator, n_cases: int = 12) -> ValidationResult:
    max_abs_err = 0.0
    case_rows: List[Dict[str, float]] = []
    for _ in range(n_cases):
        mu = rng.normal(loc=0.0, scale=2.0)
        sigma2 = float(np.exp(rng.normal(loc=-0.2, scale=0.7)))
        integral, _ = quad(lambda y: normal_pdf(y, mu, sigma2), -np.inf, np.inf, limit=200)
        err = abs(integral - 1.0)
        max_abs_err = max(max_abs_err, err)
        case_rows.append({"mu": mu, "sigma2": sigma2, "integral": integral, "abs_err": err})

    passed = max_abs_err < 1e-9
    details = (
        "Gaussian likelihood normalization over support R failed"
        if not passed
        else "All tested Gaussian likelihoods integrated to 1 within tolerance."
    )

    return ValidationResult(
        name="gaussian_likelihood_normalization",
        passed=passed,
        equation_refs="docs/derivations/sections/01_notation_and_model.tex:eq:A_obs,eq:B_obs,eq:C_obs",
        details=details,
        diagnostics={"max_abs_error": max_abs_err, "cases": case_rows},
    )
