#!/usr/bin/env python3

from __future__ import annotations

from typing import Dict, List

import numpy as np

from common import ValidationResult


def sequential_update(m: np.ndarray, c: np.ndarray, h: np.ndarray, r: float, ys: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    m_curr = m.copy()
    c_curr = c.copy()
    for y in ys:
        f = float(h @ c_curr @ h + r)
        k = c_curr @ h / f
        innov = float(y - h @ m_curr)
        m_curr = m_curr + k * innov
        c_curr = c_curr - np.outer(k, h) @ c_curr
        c_curr = 0.5 * (c_curr + c_curr.T)
    return m_curr, c_curr


def aggregated_update(m: np.ndarray, c: np.ndarray, h: np.ndarray, r: float, ys: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    i = ys.shape[0]
    ybar = float(np.mean(ys))
    rbar = r / i
    f = float(h @ c @ h + rbar)
    k = c @ h / f
    innov = ybar - float(h @ m)
    m_new = m + k * innov
    c_new = c - np.outer(k, h) @ c
    c_new = 0.5 * (c_new + c_new.T)
    return m_new, c_new


def run(rng: np.random.Generator, n_trials: int = 25) -> ValidationResult:
    max_mean_err = 0.0
    max_cov_err = 0.0
    worst: Dict[str, float] = {}

    for _ in range(n_trials):
        d = 3
        a = rng.normal(size=(d, d))
        c = a @ a.T + d * np.eye(d)
        m = rng.normal(size=d)
        h = rng.normal(size=d)
        r = float(np.exp(rng.normal(loc=-0.2, scale=0.3)))
        i = int(rng.integers(2, 10))

        true_x = rng.multivariate_normal(m, c)
        ys = (h @ true_x) + rng.normal(scale=np.sqrt(r), size=i)

        ms, cs = sequential_update(m, c, h, r, ys)
        ma, ca = aggregated_update(m, c, h, r, ys)

        mean_err = float(np.max(np.abs(ms - ma)))
        cov_err = float(np.max(np.abs(cs - ca)))
        if mean_err > max_mean_err or cov_err > max_cov_err:
            max_mean_err = max(max_mean_err, mean_err)
            max_cov_err = max(max_cov_err, cov_err)
            worst = {"replicates": float(i), "mean_err": mean_err, "cov_err": cov_err}

    passed = max_mean_err < 1e-10 and max_cov_err < 1e-10
    details = (
        "Replicate sequential assimilation and aggregated assimilation differ"
        if not passed
        else "Replicate sequential assimilation equals sufficient-statistic aggregated update."
    )

    return ValidationResult(
        name="replicate_sufficient_statistic_assimilation",
        passed=passed,
        equation_refs="docs/derivations/sections/10_sufficient_statistics.tex:eq:replicate_sufficient,eq:sse_decomposition",
        details=details,
        diagnostics={"max_abs_mean_error": max_mean_err, "max_abs_cov_error": max_cov_err, "worst_case": worst},
    )
