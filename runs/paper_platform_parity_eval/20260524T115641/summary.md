# Paper Platform Parity Gate

Run id: `20260524T115641`

Parity pass: `False`

Candidate:

- Label: `python_v43_capped_integral_kkt`
- Metrics: `runs/paper_7dof_section_v/20260524T114736/metrics.yaml`
- Raw arrays: `runs/paper_7dof_section_v/20260524T114736/paper_7dof_section_v_raw.npz`

Strict checks:

| Check | Pass | Detail |
| --- | ---: | --- |
| `candidate_execution_contact_bounds` | `True` |  |
| `legacy_formula_faithful_overall` | `True` |  |
| `legacy_figure_match_overall` | `True` |  |
| `tail_force_error_against_formula` | `True` | `candidate_value=0.06720487008205062`, `reference_value=0.0476436`, `abs_delta=0.019561270082050615`, `delta_tolerance=0.05` |
| `tail_position_error_against_formula` | `True` | `candidate_value=0.00044122814610554124`, `reference_value=0.000583872`, `abs_delta=0.0001426438538944588`, `delta_tolerance=0.001` |
| `tail_orientation_error_against_formula` | `True` | `candidate_value=2.7345108152399078e-05`, `reference_value=7.42197e-05`, `abs_delta=4.6874591847600916e-05`, `delta_tolerance=0.0001` |
| `duration_coverage` | `False` | `candidate_duration_s=5.0`, `required_duration_s=30.0` |
| `fig6_q7_22s_landmark` | `False` | `candidate_q7_rad=None`, `reference_q7_rad=2.5`, `reason=candidate raw arrays end at 5.000 s` |
| `fig5_r_sweep_coverage` | `False` | `missing_r_values=['0.2', '0.4', '0.6', '0.8', '1']` |
| `paper_assumption_compatibility` | `False` | `force_integral_limit=0.1`, `reason=finite force-integral cap is a diagnostic anti-windup assumption` |

Legacy references:

| Reference | Acceptance | Overall | Tail force N | Tail position m | Tail orientation rad |
| --- | --- | ---: | ---: | ---: | ---: |
| `formula_faithful` | `diagnostic` | `True` | `0.0476436` | `0.000583872` | `7.42197e-05` |
| `figure_match` | `landmark` | `True` | `0.000574393` | `0.000907723` | `2.69494e-06` |

Interpretation:

strict paper-platform parity gate failed: duration_coverage, fig6_q7_22s_landmark, fig5_r_sweep_coverage, paper_assumption_compatibility
