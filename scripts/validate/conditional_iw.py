#!/usr/bin/env python3

from __future__ import annotations

import math
from typing import Dict

import numpy as np

from common import ValidationResult


def random_spd(rng: np.random.Generator, d: int) -> np.ndarray:
    a = rng.normal(size=(d, d))
    return a @ a.T + d * np.eye(d)


def log_iw_kernel(w: np.ndarray, nu: float, s: np.ndarray) -> float:
    d = w.shape[0]
    sign_w, logdet_w = np.linalg.slogdet(w)
    if sign_w <= 0:
        return float("-inf")
    winv = np.linalg.inv(w)
    return -0.5 * (nu + d + 1.0) * logdet_w - 0.5 * float(np.trace(s @ winv))


def run(rng: np.random.Generator, n_trials: int = 12) -> ValidationResult:
    max_std = 0.0
    worst: Dict[str, float] = {}

    for _ in range(n_trials):
        d = int(rng.integers(2, 5))
        t = int(rng.integers(6, 25))
        nu0 = float(d + rng.uniform(2.0, 9.0))
        s0 = random_spd(rng, d)

        innovations = rng.normal(size=(t, d))
        scatter = innovations.T @ innovations

        nu1 = nu0 + t
        s1 = s0 + scatter

        diffs = []
        for _sample in range(40):
            w = random_spd(rng, d)
            lp_prior = log_iw_kernel(w, nu0, s0)
            lp_like = -0.5 * t * np.linalg.slogdet(w)[1] - 0.5 * float(np.trace(scatter @ np.linalg.inv(w)))
            lp_post = log_iw_kernel(w, nu1, s1)
            diffs.append(lp_prior + lp_like - lp_post)

        std_diff = float(np.std(diffs))
        if std_diff > max_std:
            max_std = std_diff
            worst = {"d": float(d), "t": float(t), "nu0": nu0, "std_diff": std_diff}

    passed = max_std < 1e-10
    details = (
        "IW posterior-kernel equivalence failed"
        if not passed
        else "IW conjugate posterior kernel matches prior*innovation-likelihood up to additive constant."
    )

    return ValidationResult(
        name="evolution_covariance_iw_conjugacy",
        passed=passed,
        equation_refs="docs/derivations/sections/04_static_conditionals.tex:eq:cond_W",
        details=details,
        diagnostics={"max_std_of_kernel_difference": max_std, "worst_case": worst},
    )
