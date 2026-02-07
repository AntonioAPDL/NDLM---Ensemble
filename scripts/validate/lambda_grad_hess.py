#!/usr/bin/env python3

from __future__ import annotations

from typing import Dict

import numpy as np

from common import ValidationResult


def log_post_lambda(
    lam: float,
    z_prev: np.ndarray,
    y_lambda: np.ndarray,
    w_zeta: float,
    m0: float,
    c0: float,
) -> float:
    resid = y_lambda - lam * z_prev
    ll = -0.5 / w_zeta * float(np.sum(resid**2))
    lp = -0.5 / c0 * (lam - m0) ** 2
    return ll + lp


def grad_hess_analytic(
    lam: float,
    z_prev: np.ndarray,
    y_lambda: np.ndarray,
    w_zeta: float,
    m0: float,
    c0: float,
) -> Dict[str, float]:
    grad = float(np.sum(z_prev * (y_lambda - lam * z_prev)) / w_zeta - (lam - m0) / c0)
    hess = float(-np.sum(z_prev**2) / w_zeta - 1.0 / c0)
    return {"grad": grad, "hess": hess}


def finite_diff(
    lam: float,
    z_prev: np.ndarray,
    y_lambda: np.ndarray,
    w_zeta: float,
    m0: float,
    c0: float,
    eps: float = 1e-4,
) -> Dict[str, float]:
    f0 = log_post_lambda(lam, z_prev, y_lambda, w_zeta, m0, c0)
    fp = log_post_lambda(lam + eps, z_prev, y_lambda, w_zeta, m0, c0)
    fm = log_post_lambda(lam - eps, z_prev, y_lambda, w_zeta, m0, c0)
    grad = (fp - fm) / (2.0 * eps)
    hess = (fp - 2.0 * f0 + fm) / (eps**2)
    return {"grad": float(grad), "hess": float(hess)}


def run(rng: np.random.Generator, n_trials: int = 25) -> ValidationResult:
    max_grad_err = 0.0
    max_hess_err = 0.0

    for _ in range(n_trials):
        t = int(rng.integers(12, 40))
        z_prev = rng.normal(size=t)
        psi_term = rng.normal(scale=0.5, size=t)
        lam_true = float(rng.normal(scale=0.4))
        w_zeta = float(np.exp(rng.normal(loc=-0.1, scale=0.2)))
        y_lambda = lam_true * z_prev + psi_term + rng.normal(scale=np.sqrt(w_zeta), size=t)

        m0 = float(rng.normal(scale=0.2))
        c0 = float(np.exp(rng.normal(loc=-0.2, scale=0.3)))
        lam_eval = float(rng.normal(scale=0.3))

        ana = grad_hess_analytic(lam_eval, z_prev, y_lambda, w_zeta, m0, c0)
        num = finite_diff(lam_eval, z_prev, y_lambda, w_zeta, m0, c0)

        max_grad_err = max(max_grad_err, abs(ana["grad"] - num["grad"]))
        max_hess_err = max(max_hess_err, abs(ana["hess"] - num["hess"]))

    passed = max_grad_err < 1e-7 and max_hess_err < 1e-4
    details = (
        "Lambda gradient/Hessian mismatch against finite differences"
        if not passed
        else "Lambda block gradient and Hessian match finite-difference checks."
    )

    return ValidationResult(
        name="lambda_gradient_hessian",
        passed=passed,
        equation_refs="docs/derivations/sections/04_static_conditionals.tex:eq:lambda_var,eq:lambda_mean,eq:cond_lambda",
        details=details,
        diagnostics={
            "max_abs_gradient_error": max_grad_err,
            "max_abs_hessian_error": max_hess_err,
        },
    )
