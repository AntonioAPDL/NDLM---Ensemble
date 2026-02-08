#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from common import ValidationResult


@dataclass
class KFStore:
    a: List[np.ndarray]
    r: List[np.ndarray]
    m: List[np.ndarray]
    c: List[np.ndarray]


def block_index(t: int, d: int) -> slice:
    return slice(t * d, (t + 1) * d)


def simulate_system(rng: np.random.Generator, t_max: int, d: int) -> Tuple[np.ndarray, List[List[float]]]:
    g = np.array([[0.9, 0.1], [0.0, 0.8]])
    q = np.array([[0.15, 0.02], [0.02, 0.1]])
    h1 = np.array([1.0, -0.3])
    h2 = np.array([0.2, 1.1])
    r1, r2 = 0.3, 0.45

    x = np.zeros((t_max + 1, d))
    x[0] = rng.multivariate_normal(mean=np.array([0.4, -0.2]), cov=np.array([[0.7, 0.1], [0.1, 0.6]]))
    for t in range(1, t_max + 1):
        x[t] = g @ x[t - 1] + rng.multivariate_normal(np.zeros(d), q)

    y: List[List[float]] = []
    for t in range(1, t_max + 1):
        y_t1 = float(h1 @ x[t] + rng.normal(scale=np.sqrt(r1)))
        y_t2 = float(h2 @ x[t] + rng.normal(scale=np.sqrt(r2)))
        y.append([y_t1, y_t2])

    return x, y


def kalman_smoother(y: List[List[float]]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    t_max = len(y)
    d = 2

    g = np.array([[0.9, 0.1], [0.0, 0.8]])
    q = np.array([[0.15, 0.02], [0.02, 0.1]])
    h_list = [np.array([1.0, -0.3]), np.array([0.2, 1.1])]
    r_list = [0.3, 0.45]

    m_prev = np.array([0.4, -0.2])
    c_prev = np.array([[0.7, 0.1], [0.1, 0.6]])

    a_store: List[np.ndarray] = [np.zeros(d)]
    r_store: List[np.ndarray] = [np.zeros((d, d))]
    m_store: List[np.ndarray] = [m_prev.copy()]
    c_store: List[np.ndarray] = [c_prev.copy()]

    for t in range(1, t_max + 1):
        a_t = g @ m_prev
        r_t = g @ c_prev @ g.T + q

        m_curr = a_t.copy()
        c_curr = r_t.copy()
        for obs_idx in range(2):
            h = h_list[obs_idx]
            rv = r_list[obs_idx]
            f = float(h @ c_curr @ h + rv)
            k = c_curr @ h / f
            innovation = y[t - 1][obs_idx] - float(h @ m_curr)
            m_curr = m_curr + k * innovation
            c_curr = c_curr - np.outer(k, h) @ c_curr
            c_curr = 0.5 * (c_curr + c_curr.T)

        a_store.append(a_t)
        r_store.append(r_t)
        m_store.append(m_curr)
        c_store.append(c_curr)

        m_prev = m_curr
        c_prev = c_curr

    # RTS smoother
    ms: List[np.ndarray] = [np.zeros(d) for _ in range(t_max + 1)]
    cs: List[np.ndarray] = [np.zeros((d, d)) for _ in range(t_max + 1)]
    ms[t_max] = m_store[t_max]
    cs[t_max] = c_store[t_max]

    for t in range(t_max - 1, -1, -1):
        b_t = c_store[t] @ g.T @ np.linalg.inv(r_store[t + 1])
        ms[t] = m_store[t] + b_t @ (ms[t + 1] - a_store[t + 1])
        cs[t] = c_store[t] + b_t @ (cs[t + 1] - r_store[t + 1]) @ b_t.T
        cs[t] = 0.5 * (cs[t] + cs[t].T)

    return ms, cs


def brute_force_posterior(y: List[List[float]]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    t_max = len(y)
    d = 2
    d_big = (t_max + 1) * d

    g = np.array([[0.9, 0.1], [0.0, 0.8]])
    q = np.array([[0.15, 0.02], [0.02, 0.1]])
    h_list = [np.array([1.0, -0.3]), np.array([0.2, 1.1])]
    r_list = [0.3, 0.45]

    m0 = np.array([0.4, -0.2])
    c0 = np.array([[0.7, 0.1], [0.1, 0.6]])

    m_blocks = [np.zeros(d) for _ in range(t_max + 1)]
    p_blocks = [[np.zeros((d, d)) for _ in range(t_max + 1)] for _ in range(t_max + 1)]

    m_blocks[0] = m0
    p_blocks[0][0] = c0
    for t in range(1, t_max + 1):
        m_blocks[t] = g @ m_blocks[t - 1]
        p_blocks[t][t] = g @ p_blocks[t - 1][t - 1] @ g.T + q
        for s in range(0, t):
            p_blocks[t][s] = g @ p_blocks[t - 1][s]
            p_blocks[s][t] = p_blocks[t][s].T

    m_big = np.concatenate(m_blocks)
    c_big = np.zeros((d_big, d_big))
    for t in range(t_max + 1):
        for s in range(t_max + 1):
            c_big[block_index(t, d), block_index(s, d)] = p_blocks[t][s]

    obs_dim = t_max * 2
    h_big = np.zeros((obs_dim, d_big))
    r_big = np.zeros((obs_dim, obs_dim))
    y_vec = np.zeros(obs_dim)

    row = 0
    for t in range(1, t_max + 1):
        for obs_idx in range(2):
            h_big[row, block_index(t, d)] = h_list[obs_idx]
            r_big[row, row] = r_list[obs_idx]
            y_vec[row] = y[t - 1][obs_idx]
            row += 1

    s_mat = h_big @ c_big @ h_big.T + r_big
    k_big = c_big @ h_big.T @ np.linalg.inv(s_mat)
    m_post = m_big + k_big @ (y_vec - h_big @ m_big)
    c_post = c_big - k_big @ h_big @ c_big
    c_post = 0.5 * (c_post + c_post.T)

    ms: List[np.ndarray] = []
    cs: List[np.ndarray] = []
    for t in range(t_max + 1):
        sl = block_index(t, d)
        ms.append(m_post[sl])
        cs.append(c_post[sl, sl])

    return ms, cs


def run(rng: np.random.Generator) -> ValidationResult:
    _x_true, y = simulate_system(rng, t_max=4, d=2)
    ms_kf, cs_kf = kalman_smoother(y)
    ms_bf, cs_bf = brute_force_posterior(y)

    max_mean_err = 0.0
    max_cov_err = 0.0
    for t in range(len(ms_kf)):
        max_mean_err = max(max_mean_err, float(np.max(np.abs(ms_kf[t] - ms_bf[t]))))
        max_cov_err = max(max_cov_err, float(np.max(np.abs(cs_kf[t] - cs_bf[t]))))

    passed = max_mean_err < 1e-8 and max_cov_err < 1e-8
    details = (
        "Kalman/FFBS smoother moments do not match brute-force Gaussian conditioning"
        if not passed
        else "Kalman/FFBS smoother moments match brute-force Gaussian conditioning on toy system."
    )

    return ValidationResult(
        name="kalman_ffbs_vs_bruteforce",
        passed=passed,
        equation_refs=(
            "docs/derivations/sections/03_state_posterior_ffbs.tex:"
            "eq:kf_f,eq:kf_K,eq:kf_m,eq:kf_C,eq:ffbs_cond"
        ),
        details=details,
        diagnostics={"max_abs_mean_error": max_mean_err, "max_abs_cov_error": max_cov_err},
    )
