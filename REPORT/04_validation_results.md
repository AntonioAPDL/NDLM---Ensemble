# Validation Results

- Timestamp: 2026-02-07 21:34:31 UTC
- Total checks: 7
- PASS: 7
- FAIL: 0

## Validated items

- gaussian_likelihood_normalization: PASS
  equation refs: docs/derivations/sections/01_notation_and_model.tex:eq:A_obs,eq:B_obs,eq:C_obs
  details: All tested Gaussian likelihoods integrated to 1 within tolerance.
  diagnostics: {"cases": [{"abs_err": 2.220446049250313e-16, "integral": 0.9999999999999998, "mu": -0.5796700312470088, "sigma2": 2.5835864727412403}, {"abs_err": 2.220446049250313e-16, "integral": 1.0000000000000002, "mu": 1.7132449253108792, "sigma2": 0.4844229112074354}, {"abs_err": 6.661338147750939e-16, "integral": 1.0000000000000007, "mu": -0.7294883499219125, "sigma2": 0.653922702867068}, {"abs_err": 0.0, "integral": 1.0, "mu": 0.5619384591872246, "sigma2": 1.2494390048465889}, {"abs_err": 0.0, "integral": 1.0, "mu": -0.35278280515466637, "sigma2": 0.3739435422668831}, {"abs_err": 6.661338147750939e-16, "integral": 1.0000000000000007, "mu": 2.2816778702621834, "sigma2": 2.651449472154443}, {"abs_err": 1.1102230246251565e-16, "integral": 0.9999999999999999, "mu": -2.3195293167447693, "sigma2": 0.41173891975909627}, {"abs_err": 6.661338147750939e-16, "integral": 1.0000000000000007, "mu": -0.5810067256328881, "sigma2": 1.0739027528984095}, {"abs_err": 5.551115123125783e-16, "integral": 0.9999999999999994, "mu": -0.24649798166023545, "sigma2": 0.3542208198298516}, {"abs_err": 4.440892098500626e-16, "integral": 1.0000000000000004, "mu": 0.10940630773542319, "sigma2": 0.7389070101101725}, {"abs_err": 0.0, "integral": 1.0, "mu": -2.0922715271160466, "sigma2": 0.9262894381343071}, {"abs_err": 0.0, "integral": 1.0, "mu": 1.3980328854099358, "sigma2": 1.0411335343943915}], "max_abs_error": 6.661338147750939e-16}
- joint_marginal_gaussian_consistency: PASS
  equation refs: docs/derivations/sections/02_joint_density.tex:eq:joint_A,eq:joint_B,eq:joint_C
  details: Integrated latent-state joint recovers closed-form Gaussian marginal likelihood.
  diagnostics: {"cases": [{"c": 0.6531109172204936, "closed_form": 0.2404573579760242, "h": 0.7046848188710417, "m": 3.0163511695784035, "numerical": 0.24045735797602197, "r": 1.0248723802266844, "rel_err": 9.234261192671476e-15, "y": 1.1447456573557244}, {"c": 0.3372545326095113, "closed_form": 0.24820392679990674, "h": 1.0690023122510413, "m": 1.1655208876030554, "numerical": 0.24820392679990672, "r": 1.71486326419632, "rel_err": 1.1182569096904127e-16, "y": 0.5864766423993963}, {"c": 0.8084742568183032, "closed_form": 0.22383387884740683, "h": 0.5285237473664974, "m": -0.06256390211975997, "numerical": 0.22383387884740769, "r": 0.48105412215168486, "rel_err": 3.844024186665094e-15, "y": 0.9975876510394852}, {"c": 0.561057614888068, "closed_form": 0.1227539293924885, "h": 1.2446104813920609, "m": 2.394344675468611, "numerical": 0.12275392939248851, "r": 1.0500780835318748, "rel_err": 1.1305371548182523e-16, "y": 1.1709049078261178}, {"c": 0.9988424790544816, "closed_form": 0.044112362360736665, "h": 1.2050795523724922, "m": 0.7783105774085914, "numerical": 0.04411236236073793, "r": 0.3868441643297729, "rel_err": 2.862867964729935e-14, "y": -1.702973331363046}, {"c": 1.8684972937087838, "closed_form": 0.05376655768533982, "h": 1.507324628650953, "m": 1.1655488147380222, "numerical": 0.053766557685340124, "r": 0.5795956872381339, "rel_err": 5.6784615738039954e-15, "y": -1.6704379171324457}, {"c": 0.3778986533557759, "closed_form": 0.1967015575490116, "h": 0.9072731191962092, "m": 0.6976827162189244, "numerical": 0.19670155754901128, "r": 1.012458593845831, "rel_err": 1.693260142612534e-15, "y": -0.5920923177053355}, {"c": 0.6279059423995965, "closed_form": 0.18918255300609366, "h": 1.1721869480652796, "m": -1.7720426645589376, "numerical": 0.18918255300609366, "r": 0.8813519253574867, "rel_err": 0.0, "y": -0.7995015398163503}, {"c": 0.4570064195972628, "closed_form": 0.027123591079549546, "h": 0.7590471172608727, "m": -1.0484511719182796, "numerical": 0.027123591079549477, "r": 0.5870250491868805, "rel_err": 2.558250448311384e-15, "y": 1.3744164590123014}, {"c": 0.6300095982345651, "closed_form": 0.5149738851088875, "h": 0.61303342298735, "m": -0.6146284042107717, "numerical": 0.5149738851088876, "r": 0.35990061185993344, "rel_err": 2.1558821849585788e-16, "y": -0.3179533217412057}], "max_relative_error": 2.862867964729935e-14}
- observation_variance_ig_conjugacy: PASS
  equation refs: docs/derivations/sections/04_static_conditionals.tex:eq:cond_sigma
  details: IG conjugate posterior kernel matches prior*likelihood up to additive constant.
  diagnostics: {"max_std_of_kernel_difference": 3.3132216575727064e-14, "worst_case": {"a0": 2.7158257923759686, "a1": 17.71582579237597, "b0": 2.7273590608495866, "b1": 51.16257164862803, "n": 30.0, "sse": 96.87042517555689, "std_diff": 3.3132216575727064e-14}}
- evolution_covariance_iw_conjugacy: PASS
  equation refs: docs/derivations/sections/04_static_conditionals.tex:eq:cond_W
  details: IW conjugate posterior kernel matches prior*innovation-likelihood up to additive constant.
  diagnostics: {"max_std_of_kernel_difference": 1.5550987078142447e-14, "worst_case": {"d": 4.0, "nu0": 6.896185811753835, "std_diff": 1.5550987078142447e-14, "t": 23.0}}
- lambda_gradient_hessian: PASS
  equation refs: docs/derivations/sections/04_static_conditionals.tex:eq:lambda_var,eq:lambda_mean,eq:cond_lambda
  details: Lambda block gradient and Hessian match finite-difference checks.
  diagnostics: {"max_abs_gradient_error": 3.806555071150797e-11, "max_abs_hessian_error": 2.0450517226322518e-06}
- kalman_ffbs_vs_bruteforce: PASS
  equation refs: docs/derivations/sections/03_state_posterior_ffbs.tex:eq:kf_f,eq:kf_K,eq:kf_m,eq:kf_C,eq:ffbs_cond
  details: Kalman/FFBS smoother moments match brute-force Gaussian conditioning on toy system.
  diagnostics: {"max_abs_cov_error": 1.942890293094024e-16, "max_abs_mean_error": 4.996003610813204e-16}
- replicate_sufficient_statistic_assimilation: PASS
  equation refs: docs/derivations/sections/10_sufficient_statistics.tex:eq:replicate_sufficient,eq:sse_decomposition
  details: Replicate sequential assimilation equals sufficient-statistic aggregated update.
  diagnostics: {"max_abs_cov_error": 3.552713678800501e-15, "max_abs_mean_error": 2.220446049250313e-15, "worst_case": {"cov_err": 2.886579864025407e-15, "mean_err": 2.220446049250313e-15, "replicates": 3.0}}

## Code links

- scripts/validate/validate_all.py
- scripts/validate/likelihood_normalization.py
- scripts/validate/joint_marginal_consistency.py
- scripts/validate/conditional_ig.py
- scripts/validate/conditional_iw.py
- scripts/validate/lambda_grad_hess.py
- scripts/validate/kalman_bruteforce.py
- scripts/validate/replicate_assimilation.py