# Legacy Figure-Match Source Audit Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v50-legacy-figure-match-source-audit`

## Scope

This branch audits the legacy MATLAB/RNN source path that produced the
`figure_match` q7-at-22 s landmark. It answers whether the `2.5 rad` q7 value
comes from paper-faithful dynamics or from explicitly configured figure-match
tuning.

Raw MATLAB source and `.mat` files remain external inputs. The tracked run
records derived lightweight metadata only.

## Run

- Command:
  `scripts/audit_legacy_figure_match_source.py`
- Output:
  `runs/legacy_figure_match_source_audit/20260524T123651`
- Code commit recorded by the run:
  `deaf21d52abb86e52ed146ddafe7a80e147dd773`
- Git state at run time:
  clean

## Inputs

- Legacy root:
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2`
- Source files:
  `config_audit.m`, `simulate_paper_method_branch.m`,
  `simulate_paper_ideal_branch.m`
- Raw Fig.6 files:
  `formula_faithful_fig6_results.mat`, `figure_match_fig6_results.mat`

## Result

- `figure_match_is_formula_faithful = false`
- `nonpaper_tuning_knob_count = 8`
- `uses_explicit_q7_nullspace_bias = true`
- `figure_match_pins_q7_upper_limit = true`
- `figure_match_force_loop_mode = admittance_proxy`
- `figure_match_solver_mode = pinv_bounded`
- `figure_match_orientation_mode = normal_only`
- `figure_match_acceptance_mode = landmark`
- `figure_match_q7_nullspace_speed = 0.35`
- `figure_match_alpha = 20.0`
- `figure_match_kp = 25.0`
- `formula_force_loop_mode = paper_literal`
- `formula_solver_mode = kkt_projection`
- `formula_orientation_mode = force_shortest_arc`
- `raw_figure_match_q7_at_22_s_rad = 2.4999999999358065`
- `raw_figure_match_q7_exact_upper_limit_count = 17829`

Figure-match tuning fields:

| Field | Figure-match value | Formula-faithful value |
| --- | ---: | ---: |
| `orientation_mode` | `normal_only` | `force_shortest_arc` |
| `solver_mode` | `pinv_bounded` | `kkt_projection` |
| `force_loop_mode` | `admittance_proxy` | `paper_literal` |
| `acceptance_mode` | `landmark` | `diagnostic` |
| `alpha` | `20.0` | not configured |
| `maxAngularSpeed` | `1.5` | not configured |
| `kp` | `25.0` | not configured |
| `q7NullspaceSpeed` | `0.35` | not configured |

The audited implementation wires `q7NullspaceSpeed` into the pseudoinverse
nullspace branch through a q7-only bias. Therefore the `2.5 rad` q7 landmark
is not an emergent result of the formula-faithful KKT/paper-literal line.

## Gate Implication

The current strict gate still fails because it compares the Python
formula-faithful candidate against a q7 landmark produced by the tuned legacy
figure-match line. The gate should be revised before any stronger
paper-equivalence claim:

- keep formula-faithful parity primary and demote q7 figure-match to
  separately labeled landmark evidence; or
- implement a separate Python `figure_match` candidate with
  `admittance_proxy` and q7 nullspace bias, explicitly labeled as tuned
  landmark matching rather than formula-faithful parity.

## Next Step

Revise the paper-platform parity gate into explicit claim levels:
formula-faithful parity, figure-match landmark reproduction, and UR10e
adapted simulation. Do not use the figure-match q7 landmark as a
paper-equivalence blocker without its tuning provenance.
