# Legacy Figure-Match Source Audit

Run id: `20260524T123651`

Scope: static and raw-output provenance audit for the legacy MATLAB/RNN `figure_match` line.
This records lightweight derived metadata only; legacy source and raw `.mat` files remain external inputs.

Summary:

```yaml
figure_match_is_formula_faithful: false
nonpaper_tuning_knob_count: 8
nonpaper_tuning_knobs:
- field: orientation_mode
  figure_match_value: normal_only
  formula_faithful_value: force_shortest_arc
  paper_faithful_expected: force_shortest_arc
- field: solver_mode
  figure_match_value: pinv_bounded
  formula_faithful_value: kkt_projection
  paper_faithful_expected: kkt_projection
- field: force_loop_mode
  figure_match_value: admittance_proxy
  formula_faithful_value: paper_literal
  paper_faithful_expected: paper_literal
- field: acceptance_mode
  figure_match_value: landmark
  formula_faithful_value: diagnostic
  paper_faithful_expected: diagnostic
- field: alpha
  figure_match_value: 20.0
  formula_faithful_value: null
  paper_faithful_expected: not configured as formula-faithful tuning knob
- field: maxAngularSpeed
  figure_match_value: 1.5
  formula_faithful_value: null
  paper_faithful_expected: not configured as formula-faithful tuning knob
- field: kp
  figure_match_value: 25.0
  formula_faithful_value: null
  paper_faithful_expected: not configured as formula-faithful tuning knob
- field: q7NullspaceSpeed
  figure_match_value: 0.35
  formula_faithful_value: null
  paper_faithful_expected: not configured as formula-faithful tuning knob
uses_explicit_q7_nullspace_bias: true
figure_match_pins_q7_upper_limit: true
recommended_next_action: implement a separately labeled Python figure-match/admittance_proxy
  candidate or revise the strict parity gate so q7 figure-match remains landmark provenance
figure_match_force_loop_mode: admittance_proxy
figure_match_solver_mode: pinv_bounded
figure_match_orientation_mode: normal_only
figure_match_acceptance_mode: landmark
figure_match_q7_nullspace_speed: 0.35
figure_match_alpha: 20.0
figure_match_kp: 25.0
formula_force_loop_mode: paper_literal
formula_solver_mode: kkt_projection
formula_orientation_mode: force_shortest_arc
raw_figure_match_q7_at_22_s_rad: 2.4999999999358065
raw_figure_match_q7_exact_upper_limit_count: 17829
```

Figure-match tuning fields:

| Field | Value | Source line | Comment |
| --- | ---: | ---: | --- |
| `orientation_mode` | `normal_only` | `194` |  |
| `solver_mode` | `pinv_bounded` | `195` |  |
| `acceptance_mode` | `landmark` | `196` |  |
| `force_loop_mode` | `admittance_proxy` | `197` |  |
| `alpha` | `20.0` | `198` | tuned candidate: makes joint-limit behavior more aggressive |
| `maxAngularSpeed` | `1.5` | `199` | tuned candidate: keep orientation channel within velocity limit scale |
| `kp` | `25.0` | `200` | tuned: recover XY tracking while keeping startup saturation |
| `q7NullspaceSpeed` | `0.35` | `201` | tuned: drive q7 toward the paper 22 s limit landmark |

Formula-faithful fields:

| Field | Value | Source line | Comment |
| --- | ---: | ---: | --- |
| `orientation_mode` | `force_shortest_arc` | `189` |  |
| `solver_mode` | `kkt_projection` | `190` |  |
| `acceptance_mode` | `diagnostic` | `191` |  |
| `force_loop_mode` | `paper_literal` | `192` |  |
| `T` | `0.032` | `193` | resolved ambiguity: controller communication interval for Eq.(17) |

Non-paper-faithful tuning classification:

| Field | Figure-match value | Formula-faithful value | Expected paper-faithful value |
| --- | ---: | ---: | --- |
| `orientation_mode` | `normal_only` | `force_shortest_arc` | force_shortest_arc |
| `solver_mode` | `pinv_bounded` | `kkt_projection` | kkt_projection |
| `force_loop_mode` | `admittance_proxy` | `paper_literal` | paper_literal |
| `acceptance_mode` | `landmark` | `diagnostic` | diagnostic |
| `alpha` | `20.0` | `None` | not configured as formula-faithful tuning knob |
| `maxAngularSpeed` | `1.5` | `None` | not configured as formula-faithful tuning knob |
| `kp` | `25.0` | `None` | not configured as formula-faithful tuning knob |
| `q7NullspaceSpeed` | `0.35` | `None` | not configured as formula-faithful tuning knob |

Raw Fig.6 summaries:

| Variant | Force loop | q7@22 rad | q7 exact upper-limit samples | qdot limit hits |
| --- | --- | ---: | ---: | ---: |
| `formula_faithful` | `paper_literal` | `1.1241793710124022` | `0` | `0` |
| `figure_match` | `admittance_proxy` | `2.4999999999358065` | `17829` | `148` |

Implementation source hits:

| File | Line | Text |
| --- | ---: | --- |
| `simulate_paper_method_branch.m` | `26` | `results.paper_method_notes = notes_for_variant(variant);` |
| `simulate_paper_method_branch.m` | `48` | `cfg.paper_ideal.forceLoopMode = cfg.paper_method.formula_faithful.force_loop_mode;` |
| `simulate_paper_method_branch.m` | `52` | `case 'figure_match'` |
| `simulate_paper_method_branch.m` | `64` | `cfg.paper_ideal.forceLoopMode = cfg.paper_method.figure_match.force_loop_mode;` |
| `simulate_paper_method_branch.m` | `65` | `cfg.paper_ideal.q7NullspaceSpeed = cfg.paper_method.figure_match.q7NullspaceSpeed;` |
| `simulate_paper_method_branch.m` | `97` | `function notes = notes_for_variant(variant)` |
| `simulate_paper_method_branch.m` | `100` | `notes = [ ...` |
| `simulate_paper_method_branch.m` | `106` | `case 'figure_match'` |
| `simulate_paper_method_branch.m` | `107` | `notes = [ ...` |
| `simulate_paper_method_branch.m` | `112` | `notes = '';` |
| `simulate_paper_ideal_branch.m` | `160` | `case 'admittance_proxy'` |
| `simulate_paper_ideal_branch.m` | `161` | `normal_target_accel = (-force_error - kf * force_integral - Bd * normal_target_velocity) / Md;` |
| `simulate_paper_ideal_branch.m` | `162` | `normal_target_velocity = saturate_scalar(normal_target_velocity + dt * normal_target_accel, maxNormalStateVelocity);` |
| `simulate_paper_ideal_branch.m` | `171` | `xdd_p = normal_target_accel * planeNormal;` |
| `simulate_paper_ideal_branch.m` | `174` | `normal_target_accel = 0;` |
| `simulate_paper_ideal_branch.m` | `458` | `if isfield(cfg.paper_ideal, 'q7NullspaceSpeed') && cfg.paper_ideal.q7NullspaceSpeed ~= 0` |
| `simulate_paper_ideal_branch.m` | `459` | `null_projector = eye(size(J, 2)) - pinv(J) * J;` |
| `simulate_paper_ideal_branch.m` | `462` | `bias(7) = min(cfg.paper_ideal.q7NullspaceSpeed, q7_margin / max(cfg.dt, eps));` |
| `simulate_paper_ideal_branch.m` | `463` | `qdot_proj_raw = qdot_proj_raw + null_projector * bias;` |

Interpretation:

- The legacy `figure_match` line is explicitly configured as `landmark` acceptance and uses tuned values for solver, orientation, force loop, gains, and q7 nullspace bias.
- The `q7NullspaceSpeed` knob is wired into the pseudoinverse nullspace branch, so the 2.5 rad q7 landmark is not an emergent formula-faithful consequence.
- The strict paper-platform gate should keep this provenance boundary visible before using q7@22 as a paper-equivalence requirement.
