# Paper 7DOF q7 Variant Probe

Run id: `20260524T122345`

Scope: supported Python 7DOF Section V variants for isolating the Fig.6 q7-at-22 s mismatch.
This is a diagnostic sensitivity probe, not a strict parity gate update.

Summary:

```yaml
all_execution_success: true
all_q7_available: true
q7_min_rad: 1.661263839866546
q7_max_rad: 1.6835894792145727
q7_range_rad: 0.02232563934802667
figure_match_q7_rad: 2.5
figure_match_tolerance_rad: 0.05
figure_match_pass_count: 0
variant_count: 8
closest_variant: pinv_force_cap0p1
closest_variant_q7_rad: 1.6835894792145727
closest_variant_abs_error_to_figure_match_rad: 0.8164105207854273
```

| Variant | Solver | Orientation | Force integral | q7@22 rad | Delta to figure-match rad | Tail force error N | Execution |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `kkt_force_uncapped` | `kkt_projection` | `force_shortest_arc` | `inf` | `1.6680622878116045` | `0.8319377121883955` | `0.023282898803479644` | `True` |
| `kkt_force_cap0p1` | `kkt_projection` | `force_shortest_arc` | `0.1` | `1.6755097668200787` | `0.8244902331799213` | `0.07253258857158651` | `True` |
| `kkt_normal_uncapped` | `kkt_projection` | `normal_only` | `inf` | `1.6677473123331963` | `0.8322526876668037` | `0.023240532668525615` | `True` |
| `kkt_normal_cap0p1` | `kkt_projection` | `normal_only` | `0.1` | `1.6751976272672546` | `0.8248023727327454` | `0.07246008363175997` | `True` |
| `pinv_force_uncapped` | `pinv_bounded` | `force_shortest_arc` | `inf` | `1.6818497721293582` | `0.8181502278706418` | `0.0006321261374228985` | `True` |
| `pinv_force_cap0p1` | `pinv_bounded` | `force_shortest_arc` | `0.1` | `1.6835894792145727` | `0.8164105207854273` | `0.003688206107040649` | `True` |
| `pinv_normal_uncapped` | `pinv_bounded` | `normal_only` | `inf` | `1.661263839866546` | `0.838736160133454` | `0.006717510310330816` | `True` |
| `pinv_normal_cap0p1` | `pinv_bounded` | `normal_only` | `0.1` | `1.6821932683797627` | `0.8178067316202373` | `0.003690067691211803` | `True` |

Legacy q7 references:

```yaml
primary_convergence_reference: formula_faithful
fig6_landmark_reference: figure_match
q7_at_22_abs_error_rad_vs_figure_match: 0.05
references:
  formula_faithful:
    label: paper_method_formula_faithful
    verification_path: runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful/paper_method_formula_faithful_verification.md
    q7_sample_time_s: 22.0
    q7_at_22_s_rad: 1.124179
  figure_match:
    label: paper_method_figure_match
    verification_path: runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_figure_match/paper_method_figure_match_verification.md
    q7_sample_time_s: 22.0
    q7_at_22_s_rad: 2.5
```

Interpretation:

- If `figure_match_pass_count` is zero, the q7 landmark mismatch persists across this supported variant matrix.
- This probe does not validate Panda/Franka DH provenance or the legacy figure-match tuning source.
