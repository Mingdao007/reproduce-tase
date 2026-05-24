# Paper Platform Parity Gate

Run id: `20260524T124200`

Legacy strict aggregate pass: `False`
Formula convergence pass: `True`
Figure-match landmark pass: `False`

Candidate:

- Label: `python_v47_30s_uncapped_kkt`
- Metrics: `runs/paper_7dof_section_v/20260524T121503/metrics.yaml`
- Raw arrays: `runs/paper_7dof_section_v/20260524T121503/paper_7dof_section_v_raw.npz`

Claim levels:

| Claim Level | Pass | Boundary |
| --- | ---: | --- |
| `formula_convergence` | `True` | passes execution/contact/bounds, duration, Fig.5 coverage, paper-assumption compatibility, and tail convergence against the formula-faithful legacy reference; does not claim full q-trajectory or Fig.6 landmark parity |
| `figure_match_landmark` | `False` | tracks the tuned legacy figure-match q7 landmark separately from formula-faithful parity because v49-v50 provenance shows that landmark uses explicit figure-match tuning |
| `legacy_strict_all_checks` | `False` | backward-compatible aggregate requiring both formula convergence and the tuned figure-match q7 landmark |

Legacy strict aggregate checks:

| Check | Pass | Detail |
| --- | ---: | --- |
| `candidate_execution_contact_bounds` | `True` |  |
| `legacy_formula_faithful_overall` | `True` |  |
| `tail_force_error_against_formula` | `True` | `candidate_value=0.023282898803479644`, `reference_value=0.0476436`, `abs_delta=0.024360701196520358`, `delta_tolerance=0.05` |
| `tail_position_error_against_formula` | `True` | `candidate_value=0.0005087140069982723`, `reference_value=0.000583872`, `abs_delta=7.515799300172779e-05`, `delta_tolerance=0.001` |
| `tail_orientation_error_against_formula` | `True` | `candidate_value=5.032735496157772e-05`, `reference_value=7.42197e-05`, `abs_delta=2.389234503842228e-05`, `delta_tolerance=0.0001` |
| `duration_coverage` | `True` | `candidate_duration_s=30.0`, `required_duration_s=30.0` |
| `fig5_r_sweep_coverage` | `True` | `required_duration_s=2.0`, `missing_r_values=[]` |
| `paper_assumption_compatibility` | `True` | `force_integral_limit=inf`, `reason=uncapped` |
| `legacy_figure_match_overall` | `True` |  |
| `fig6_q7_22s_landmark` | `False` | `candidate_q7_rad=1.6680622878116045`, `reference_q7_rad=2.5`, `abs_delta_rad=0.8319377121883955`, `tolerance_rad=0.05`, `reason=candidate metric present` |

Legacy references:

| Reference | Acceptance | Overall | Tail force N | Tail position m | Tail orientation rad |
| --- | --- | ---: | ---: | ---: | ---: |
| `formula_faithful` | `diagnostic` | `True` | `0.0476436` | `0.000583872` | `7.42197e-05` |
| `figure_match` | `landmark` | `True` | `0.000574393` | `0.000907723` | `2.69494e-06` |

Interpretation:

formula-convergence claim passed, but legacy strict aggregate remains failed because tuned figure-match landmark checks failed: fig6_q7_22s_landmark
