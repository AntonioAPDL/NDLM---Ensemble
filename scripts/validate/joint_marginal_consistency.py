#!/usr/bin/env python3

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
from scipy.integrate import quad

from common import ValidationResult


def normal_pdf(x: float, mu: float, var: float) -> float:
    return math.exp(-0.5 * (x - mu) ** 2 / var) / math.sqrt(2.0 * math.pi * var)


def run(rng: np.random.Generator, n_cases: int = 10) -> ValidationResult:
    max_rel_err = 0.0
    case_rows: List[Dict[str, float]] = []

    for _ in range(n_cases):
        m = float(rng.normal(scale=1.2))
        c = float(np.exp(rng.normal(loc=-0.3, scale=0.4)))
        h = float(rng.normal(loc=1.0, scale=0.3))
        r = float(np.exp(rng.normal(loc=-0.4, scale=0.3)))
        y = float(rng.normal(scale=1.0))

        # Numerical marginal by integrating out latent x.
        num, _ = quad(
            lambda x: normal_pdf(y, h * x, r) * normal_pdf(x, m, c),
            -np.inf,
            np.inf,
            limit=200,
        )

        # Closed-form marginal.
        mean_cf = h * m
        var_cf = h * h * c + r
        den = normal_pdf(y, mean_cf, var_cf)
        rel_err = abs(num - den) / max(1e-12, abs(den))
        max_rel_err = max(max_rel_err, rel_err)

        case_rows.append(
            {
                "m": m,
                "c": c,
                "h": h,
                "r": r,
                "y": y,
                "numerical": num,
                "closed_form": den,
                "rel_err": rel_err,
            }
        )

    passed = max_rel_err < 1e-9
    details = (
        "Joint-to-marginal Gaussian consistency failed"
        if not passed
        else "Integrated latent-state joint recovers closed-form Gaussian marginal likelihood."
    )

    return ValidationResult(
        name="joint_marginal_gaussian_consistency",
        passed=passed,
        equation_refs="docs/derivations/sections/02_joint_density.tex:eq:joint_A,eq:joint_B,eq:joint_C",
        details=details,
        diagnostics={"max_relative_error": max_rel_err, "cases": case_rows},
    )
