# Goal: TASE Finite-Time UR10e Reproduction

Use this file as the long-form goal instructions for the next Codex thread.
The short thread goal should reference this file instead of pasting the full
instructions into the goal text.

## Short Thread Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in `/home/andy/reproduce-tase`. First read `docs/goal.md`, `docs/goal_handoff_v110.md`, `reports/completion_audit.md`, `reports/ITERATION_LOG.md`, and `reports/DECISION_RECORD.md`; then inspect git status before changing anything. Preserve the current v109 claim boundary: formula-faithful Python paper-platform convergence and tuned Fig.6 landmark evidence remain separate, so full paper-equivalent parity is still not achieved. The UR10e adapted line is diagnostic simulation only. V95 classifies strict paper-equivalent full staged feasibility and robustness as non-final offline-actionable, while approved read-only evidence, calibrated contact geometry, orientation-gate acceptance, and hardware readiness remain blocked on explicit approval/evidence. V96 confirms strict setup remains blocked: strict full staged feasibility is `0 / 4`, three-phase setup terminal state is `0 / 10`, and three-phase trajectory feasibility is `8 / 10`. V97 confirms robustness remains incomplete: baseline diagnostic stitched sensitivity is `4 / 9`, positive stitched sensitivity is `37 / 40`, and recovered faces remain diagnostic non-final evidence. V98 defines a diagnostic robustness matrix candidate with 12 cells: 7 diagnostic passes, 1 non-final diagnostic recovery, and 4 failed cells. V99 converts those four failed cells into a planned-not-executed offline experiment matrix and command script. V100 executes `base_z_plus1mm`, V101 executes `positive_fast_timing_0p0075`, V102 executes `positive_orientation_gate_0p119`, and V103 executes `weighted_plus1mm_0p119_gate`; all four remain unresolved. V104 classifies the four remaining `+1.0 mm` signatures. V105 isolates the `positive_fast_timing_0p0075` E2 qdot/usage blocker: at `paper_time_scale = 0.0075`, qdot-limit increases through `0.3 rad/s` remove qdot saturation but still fail orientation; the first tested E2 timing pass is `paper_time_scale = 0.0052`. V106 shows weighted priority clears the isolated E2 row at `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the fixed `0.12 rad` orientation gate. V107 reruns the exact full E1-E4 `+1.0 mm` fast-timing face: the linear-primary baseline still fails E2, while both weighted rows pass `4 / 4`; this remains diagnostic evidence and does not close the original failed cell because weighted priority has not been accepted as canonical. V108 splits `base_z_plus1mm`: broader seeds recover start contact, terminal force/x-y/contact passes, terminal/path are blocked by the current `0.08 rad` orientation gate, and the run-local `0.12 rad` gate recovers Stage A/path but not stitched Stage B. V109 targets that relaxed handoff blocker: the linear-primary baseline still fails E2, while both weighted rows pass `4 / 4` at Stage A durations `15.0 s` and `16.0 s`; this remains diagnostic and does not close the original failed cell. The current execution audit still has executed cells `4`, closed cells `0`, not-executed cells `0`, and all failed cells closed `false`. The next branch should execute only a safe read-only SOP subset after explicit user confirmation using the scaffold, finalizer, and verifier, or continue only non-final offline simulation/paper-platform work identified by the v95-v109 audits. Keep strict paper-equivalent setup, v38 relaxed trajectory-after-setup, and v63-v109 diagnostic staged labels separate. Do not move or configure the real UR10e; real hardware work is read-only unless a separate approved SOP exists.
```

## Objective

Continue the UR10e + OnRobot force/torque sensor project from the current
`v109` repository state. The project goal is to reproduce the T-ASE finite-time
force-motion control paper, then adapt the method to the current UR10e
hardware and simulation stack.

Work from the whole-system plan down to derivations, implementation,
simulation, validation, and iterative experiments. Use MuJoCo as the baseline
simulator. If another simulator or modeling stack is more appropriate, propose
it with tradeoffs, but keep MuJoCo as the first reproducible baseline unless
there is a concrete blocker.

## Required Local Context

Read and audit these files before making assumptions:

- Target GitHub repository for this reproduction:
  `Mingdao007/reproduce-tase`
  `https://github.com/Mingdao007/reproduce-tase`
  Default branch: `main`
- Local authoritative clone:
  `/home/andy/reproduce-tase`
- Current local branch:
  `exp/tase-ur10e-v109-relaxed-base-z-weighted-handoff`
- Current v87 SOP artifact:
  `reports/read_only_calibration_measurement_sop.md`
- Current v88 template/scaffold artifacts:
  `templates/read_only_calibration_measurement/`
  `scripts/create_read_only_calibration_measurement_run.py`
  `runs/read_only_calibration_measurement/20260525T012234`
- Current v89 run-audit artifacts:
  `scripts/audit_read_only_calibration_measurement_run.py`
  `runs/read_only_calibration_measurement_run_audit/20260525T012835`
- Current v90 audit-mode artifacts:
  `runs/read_only_calibration_measurement_run_audit/20260525T013421`
  `reports/read_only_calibration_measurement_audit_modes_report.md`
- Current v91 evidence-finalizer artifacts:
  `scripts/finalize_read_only_calibration_measurement_evidence.py`
  `reports/read_only_calibration_measurement_evidence_finalizer_report.md`
- Current v92 worksheet coverage artifacts:
  `templates/read_only_calibration_measurement/ksm_contact_patch_convention.csv`
  `templates/read_only_calibration_measurement/orientation_gate_semantics.csv`
  `runs/read_only_calibration_measurement/20260525T014755`
  `runs/read_only_calibration_measurement_run_audit/20260525T014756`
  `reports/read_only_calibration_measurement_worksheet_coverage_report.md`
- Current v93 orientation acceptance boundary artifacts:
  `runs/read_only_calibration_measurement/20260525T015400`
  `runs/read_only_calibration_measurement_run_audit/20260525T015401`
  `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- Current v94 orientation gate-acceptance review artifacts:
  `templates/orientation_gate_acceptance_review/`
  `scripts/create_orientation_gate_acceptance_review.py`
  `scripts/audit_orientation_gate_acceptance_review.py`
  `runs/orientation_gate_acceptance_review/20260525T020054`
  `runs/orientation_gate_acceptance_review_audit/20260525T020055`
  `reports/orientation_gate_acceptance_review_template_report.md`
- Current v95 offline completion-blockers artifacts:
  `scripts/audit_offline_completion_blockers.py`
  `runs/offline_completion_blockers/20260525T020734`
  `reports/offline_completion_blockers_report.md`
- Current v96 strict-feasibility blocker artifacts:
  `scripts/audit_strict_feasibility_blockers.py`
  `tests/test_strict_feasibility_blockers.py`
  `runs/strict_feasibility_blockers/20260525T051640`
  `reports/strict_feasibility_blockers_report.md`
- Current v97 robustness blocker artifacts:
  `scripts/audit_robustness_blockers.py`
  `tests/test_robustness_blockers.py`
  `runs/robustness_blockers/20260525T052457`
  `reports/robustness_blockers_report.md`
- Current v98 diagnostic robustness matrix candidate artifacts:
  `scripts/audit_diagnostic_robustness_matrix_candidate.py`
  `tests/test_diagnostic_robustness_matrix_candidate.py`
  `runs/diagnostic_robustness_matrix_candidate/20260525T053101`
  `reports/diagnostic_robustness_matrix_candidate_report.md`
- Current v99 failed-cell experiment matrix artifacts:
  `scripts/create_failed_diagnostic_robustness_experiment_matrix.py`
  `tests/test_failed_diagnostic_robustness_experiment_matrix.py`
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909`
  `reports/failed_diagnostic_robustness_experiment_matrix_report.md`
- Current v100 failed-cell execution artifacts:
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  `tests/test_failed_diagnostic_robustness_experiment_execution.py`
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm`
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T054646`
  `reports/failed_diagnostic_robustness_experiment_execution_report.md`
- Current v101 positive fast-timing failed-cell execution artifacts:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T055322`
  `reports/positive_fast_timing_failed_cell_execution_report.md`
- Current v102 positive orientation-gate failed-cell execution artifacts:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T060119`
  `reports/positive_orientation_gate_failed_cell_execution_report.md`
- Current v103 weighted gate failed-cell execution artifacts:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T061328`
  `reports/weighted_plus1mm_gate_failed_cell_execution_report.md`
- Current v104 `+1.0 mm` unresolved diagnostic probe artifacts:
  `scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
  `tests/test_plus1mm_unresolved_diagnostic_probe.py`
  `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237`
  `reports/plus1mm_unresolved_diagnostic_probe_report.md`
- Current v105 positive fast-timing E2 qdot isolation artifacts:
  `scripts/audit_positive_stage_b_e2_margin.py`
  `tests/test_positive_stage_b_e2_margin.py`
  `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019`
  `reports/positive_fast_timing_e2_qdot_isolation_report.md`
- Current v106 positive fast-timing E2 orientation-margin artifacts:
  `scripts/audit_positive_fast_e2_orientation_margin.py`
  `tests/test_positive_fast_e2_orientation_margin.py`
  `runs/positive_fast_e2_orientation_margin/20260525T063817`
  `reports/positive_fast_e2_orientation_margin_report.md`
- Current v107 positive fast-timing weighted full-cell artifacts:
  `scripts/audit_positive_fast_weighted_full_cell.py`
  `tests/test_positive_fast_weighted_full_cell.py`
  `runs/positive_fast_weighted_full_cell/20260525T064719`
  `reports/positive_fast_weighted_full_cell_report.md`
- Current v108 `base_z_plus1mm` split artifacts:
  `scripts/audit_base_z_plus1mm_split.py`
  `tests/test_base_z_plus1mm_split.py`
  `runs/base_z_plus1mm_split/20260525T071440`
  `reports/base_z_plus1mm_split_report.md`
- Current v109 relaxed `base_z_plus1mm` weighted handoff artifacts:
  `scripts/audit_relaxed_base_z_weighted_handoff.py`
  `tests/test_relaxed_base_z_weighted_handoff.py`
  `runs/relaxed_base_z_weighted_handoff/20260525T073012`
  `reports/relaxed_base_z_weighted_handoff_report.md`
- Paper PDF:
  `/home/andy/Zotero/storage/UZRF97KG/Xu 等 - 2026 - Finite-Time Convergence Neural Network-Based Force-Motion Control for Unknown Surface With Orientati.pdf`
- Legacy source workspace that has been migrated/audited into the repo:
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/`
- Required repository entry points:
  `docs/goal_handoff_v110.md`
  `reports/completion_audit.md`
  `reports/ITERATION_LOG.md`
  `reports/DECISION_RECORD.md`
  `runs/RUN_ARTIFACTS_MANIFEST.md`
- Mandatory plans:
  `plans/MASTER_PLAN.md`
  `plans/PAPER_TRUTH_EXTRACTION.md`
  `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  `plans/MUJOCO_ENVIRONMENT_PLAN.md`
  `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  `plans/EXPERIMENT_MATRIX.md`
  `plans/HARDWARE_GATE_SOP.md`
  `plans/ROLLBACK_AND_CHECKPOINTS.md`
- Current UR10e / OnRobot hardware state source:
  `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/current_hardware_state.md`
- EOAT and TCP notes:
  `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/EOAT_TCP_NOTE.md`
  `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/v13_ksm8n_receiver_5p3mm_side_window_85mm/`

## Current Hardware Facts

- Robot: UR10e, IP `192.168.1.18`, URSoftware `5.11.9.1010452`.
- OnRobot: HEX-E v2 / Compute Box, device identity
  `hex_e_v2_3010007655`, Compute Box IP `192.168.1.1`.
- Installed URCap: `FT-OnRobot` version `4.1.7`; Compute Box observed web
  version `4.1.8`.
- Current topology: UR10e, Compute Box, and Ubuntu are reachable through an
  Ethernet switch.
- Current temporary payload/TCP readback: payload `0.44 kg`, CoG
  `[0.005, -0.005, 0.025] m`, TCP offset
  `[0, 0, 0.12254, 0, 0, 0]`.
- EOAT v13 CAD candidate contact point: `85.0 mm` from design flange face.
  This is unverified and must not be written to the real UR TCP or control
  config without measurement and explicit approval.
- OnRobot direct TCP DAQ force values currently disagree with PolyScope
  variables / UR RTDE by about `-32 N`. Do not use TCP DAQ force values as
  control truth until the reference-frame, zero, or compensation issue is
  resolved.
- Local records mainly say `KSM-8N`. If the user says `FSN-8N`, first verify
  whether this is the same part or a naming error.

## Current Repository State And Claim Boundary

The repository is not at full paper-equivalent completion. Start by reading
`reports/completion_audit.md`; treat it as the current evidence map, not as a
substitute for inspecting files and command output.

Current accepted claims:

- `UR10e adapted slowed tilted-plane E1-E4 simulation`: relaxed setup plus
  trajectory feasibility passes `4 / 4`; strict full staged feasibility
  remains `0 / 4`; hardware readiness is false.
- `paper_platform_7dof_formula_convergence`: passes the v51 split gate.
  Evidence is `reports/paper_platform_split_claim_report.md` and
  `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml`.
- `paper_platform_7dof_tuned_figure_match_candidate`: the separate v52 Python
  tuned candidate reproduces the legacy Fig.6 q7 landmark. Evidence is
  `reports/paper_7dof_tuned_figure_match_candidate_report.md` and
  `reports/paper_7dof_tuned_figure_match_provenance_report.md`.
- `paper_platform_7dof_legacy_strict_all_checks`: still not a full
  paper-equivalent parity claim because formula convergence and tuned
  landmark reproduction are separate evidence lines.
- `ur10e_tcp_contact_model_audit`: v53 verifies that the current 85 mm TCP
  site matches the EOAT-note distance but is coincident with the center of the
  colliding `contact_tip` sphere. The simulated contact surface is one sphere
  radius away, so this model is not hardware-ready.
- `ur10e_tcp_contact_point_model_variant`: v54 adds a separate simulation
  model where the 85 mm site is the intended contact point and the colliding
  sphere center is offset to local `[0, 0, 0.045]`. The strict terminal setup
  audit still fails `0 / 65`.
- `ur10e_broad_terminal_feasibility_audit`: v55 gates setup force/contact on
  `contact_plane` / `contact_tip` only and finds `0 / 513` broad terminal
  passes. This closes a self-collision false-positive path but is not a global
  infeasibility proof.
- `ur10e_contact_manifold_gate_audit`: v56 seeds from target-contact
  neighborhoods and finds `0 / 161` strict passes. The relaxed gate matrix
  shows x/y, target force, and force-normal orientation are mutually in
  tension under the current UR10e 6DOF adapted setup definition.
- `ur10e_adapted_terminal_setup_diagnostic`: v57 adds a diagnostic-only
  terminal setup gate and evaluates the v55 terminal run at `1 / 513` passes.
  This is not a path, trajectory, paper-equivalent, or hardware claim.
- `ur10e_stage_a_target_selection`: v58 selects
  `ur10e_adapted_terminal_setup_diagnostic` as the next Stage A simulation
  prototype target. The selected q target is recorded in
  `configs/ur10e_adapted_stage_a_target.yaml`; this is still not a controller,
  path, trajectory, paper-equivalent, or hardware-readiness claim.
- `ur10e_diagnostic_target_handoff`: v59 starts directly from the selected
  target and evaluates E1-E4 Stage B handoff with target-pair force/contact
  accounting. It reports `0 / 4` handoff passes: target contact, force, x/y,
  and diagnostic orientation stay within bounds, but all rows fail qdot
  saturation gates.
- `ur10e_qdot_aware_diagnostic_handoff`: v60 starts from the same selected
  target and uses slowed timing, lower force gain, and diagnostic-orientation
  hold. It reports `4 / 4` handoff passes under target-pair force/contact
  accounting. This is still direct-target handoff evidence only.
- `ur10e_stage_a_contact_path_audit`: v61 finds an offline 128-knot
  quasi-static contact-manifold path from the ordinary initial q to the
  selected diagnostic target. The path gate and terminal diagnostic gate pass
  with a minimum qdot-limited duration of `14.332635022800167 s`. This is
  offline path evidence only, not an online controller or hardware claim.
- `ur10e_stage_a_contact_path_tracking`: v62 tracks the v61 path with a
  qdot-limited joint-path replay over `15.0 s`. The tracking gate and terminal
  diagnostic gate pass with max qdot `0.14332635022814824 rad/s` and zero qdot
  saturation. This is not a connected Stage A plus Stage B trajectory claim.
- `ur10e_stitched_diagnostic_stage_a_handoff`: v63 runs the v62 Stage A tracker
  and v60 slowed handoff in one script. The stitched gate passes, Stage A
  passes, and Stage B reports `4 / 4` E1-E4 passes. This is diagnostic-label
  simulation evidence only.
- `ur10e_stitched_diagnostic_sensitivity`: v64 runs nine sensitivity cases
  around the v63 stitched policy. The stitched gate passes `4 / 9`: nominal,
  `stage_a_16s`, `force_gain_5e-5`, and `force_gain_2e-4` pass; 1 mm
  base-z/contact perturbations, `stage_a_14s`, `qdot_limit_0p12`, and
  `paper_time_scale_0p02` fail. This prevents a robustness claim.
- `ur10e_stitched_diagnostic_timing_margin`: v65 runs seven timing-margin
  cases. It shows Stage A recovers at `14.5 s`, a `0.12 rad/s` qdot limit
  recovers at `18.0 s`, and Stage B passes at `paper_time_scale = 0.012` but
  not `0.0125`. This does not recover base-z/contact perturbations.
- `ur10e_stage_a_base_z_recovery`: v66 runs three perturbation-aware base-z
  recovery cases. It recovers `base_z_minus_1mm_stage_a_16s_recovery`, while
  the exact `15.0 s` `base_z_minus_1mm` reference and `base_z_plus_1mm` remain
  unresolved. This is still diagnostic-label simulation evidence only.
- `ur10e_stage_a_base_z_bracket`: v67 runs a compact 13-point base-z bracket.
  It recovers nominal, `-0.25 mm`, and `-0.5 mm` at `15.0 s`, recovers
  `-1.0 mm` only at `16.0 s`, finds a `-0.75 mm` path anomaly, and finds no
  positive-delta recovery from `+0.05 mm` through `+1.0 mm`.
- `ur10e_positive_base_z_start_contact`: v68 uses broader deterministic and
  random start-contact seeds and finds positive-delta start contact passes
  `8 / 8` through `+1.0 mm`; terminal orientation still fails `8 / 8`
  positive deltas.
- `ur10e_positive_terminal_orientation`: v69 shows the current contact-point
  model passes positive terminal force/x-y/contact `8 / 8` but diagnostic
  orientation `0 / 8`; full-rotation and force-normal-only errors match to
  numerical precision, and the current model needs about `0.1195 rad` to cover
  all force/x-y/contact-positive terminal cases through `+1.0 mm`.
- `ur10e_positive_relaxed_orientation_recovery`: v70 uses a run-local
  `0.12 rad` diagnostic orientation envelope and recovers positive start,
  terminal, and path feasibility `8 / 8` through `+1.0 mm`, but stitched
  recovery remains `0` because Stage B handoff is `3 / 4` with E2 qdot
  saturation.
- `ur10e_positive_stage_b_e2_margin`: v71 reuses the v70 run-local relaxed
  terminal/path setup and shows E2 passes `0 / 8` positive deltas at
  `paper_time_scale = 0.01`, `7 / 8` at `0.0075`, and `8 / 8` at `0.005`.
  A qdot-limit-only probe on `+1.0 mm` at the original `0.01` timing still
  fails because max orientation error remains just above `0.12 rad`.
- `ur10e_positive_full_stitched_recovery`: v72 combines the v70 run-local
  relaxed terminal/path setup with `paper_time_scale = 0.005` and recovers the
  full positive E1-E4 stitched diagnostic matrix `8 / 8` through `+1.0 mm`.
  This remains relaxed diagnostic simulation evidence only.
- `ur10e_positive_stitched_sensitivity`: v73 stress-tests the v72 recovered
  positive stitched policy across five compact scenarios and eight positive
  deltas. The matrix passes `37 / 40`; nominal v72 and `stage_a_14p5s` pass
  `8 / 8`, while `qdot012_stage_a18s` fails `+0.2 mm` on Stage A final
  tracking, `paper_time_scale_0p0075` fails `+1.0 mm` on E2 qdot/orientation,
  and `orientation_gate_0p119` fails `+1.0 mm` on orientation gates.
- `ur10e_qdot012_stage_a_margin`: v74 isolates the v73
  `qdot012_stage_a18s` `+0.2 mm` failure and shows it is a narrow Stage A
  replay duration margin. Stage B passes `4 / 4` for all tested durations; the
  last failing Stage A duration is `18.03 s`, and the first passing duration is
  `18.035 s`.
- `ur10e_qdot012_positive_stitched_matrix`: v75 folds the v74 `18.035 s`
  duration margin into the full positive qdot012 matrix. All eight positive
  deltas pass stitched recovery through `+1.0 mm`, with Stage B handoff
  `4 / 4` for every row.
- `ur10e_positive_timing_boundary`: v76 isolates the v73
  `paper_time_scale_0p0075` `+1.0 mm` failure. Stage A passes all timing
  cases; the hardest positive E2 row passes through `paper_time_scale =
  0.0052` and first fails at `0.0054` because orientation rises just above the
  `0.12 rad` diagnostic gate. Qdot saturation becomes severe only at `0.007`
  and above.
- `ur10e_positive_orientation_gate_boundary`: v77 isolates the v73
  `orientation_gate_0p119` `+1.0 mm` failure. Stage A terminal orientation
  passes once the gate reaches `0.1195 rad`, but stitched recovery first passes
  at `0.11998 rad` because E2 reaches `0.1199788204275829 rad` under v72
  timing.
- `ur10e_stage_b_orientation_kp_probe`: v78 tests the existing Stage B
  `orientation_kp` feedback hook against the v77 tightened-orientation
  boundary at a `0.11995 rad` gate. Stage A passes all `30 / 30` E2 probe
  cells, but stitched recovery passes `0 / 30`: low gains preserve qdot while
  missing orientation, and gains that satisfy orientation fail qdot saturation
  and/or tail qdot utilization even with qdot limits up to `0.25 rad/s`.
- `ur10e_stage_b_priority_recovery`: v79 tests the redesigned Stage B priority
  formulation against the localized `+1.0 mm`, `0.11995 rad` tightened-gate
  row. Linear-primary controls still fail, but planar-primary priority with
  normal-axis weight `30` recovers E1-E4 stitched recovery `4 / 4` at
  `qdot_limit_rad_s = 0.15` for `orientation_kp = 0.001` and `0.002`.
- `ur10e_positive_planar_priority_matrix`: v80 carries both v79 passing
  planar-primary candidates across the full positive-delta matrix at the same
  `0.11995 rad` gate. Both `orientation_kp = 0.001` and `0.002` scenarios pass
  all eight positive deltas through `+1.0 mm`, for `16 / 16` stitched passes.
- `ur10e_planar_priority_stress`: v81 stress-tests both v80 planar-primary
  candidates against faster timing and the tighter `0.119 rad` orientation
  gate. Both candidates pass the focused `+1.0 mm` timing sweep through
  `paper_time_scale = 0.0065` and first fail at `0.007`; both fail the full
  positive-delta `paper_time_scale = 0.0075` stress `0 / 8`; both pass the
  `0.119 rad` gate through `+0.75 mm` but still fail at `+1.0 mm`.
- `ur10e_weighted_timing_recovery`: v82 shows the v81 faster-timing failure is
  priority-formulation dependent. Weighted zero-angular-command priority
  passes the full positive-delta `paper_time_scale = 0.0075`,
  `0.11995 rad` matrix `8 / 8` for both tested normal weights, and
  `weighted_kp0_normal1` passes the focused `+1.0 mm` timing sweep through
  `paper_time_scale = 0.01`.
- `ur10e_weighted_gate_time_matrix`: v83 shows the focused v82 timing evidence
  generalizes to the full positive-delta `paper_time_scale = 0.01`,
  `0.11995 rad` matrix, with both tested weighted scenarios passing `8 / 8`.
  The tighter `0.119 rad` gate still only passes through `+0.75 mm` and fails
  `+1.0 mm`; the focused `+1.0 mm` row first passes at `0.11955 rad` for
  `paper_time_scale = 0.0075` and `0.1196 rad` for `0.01`.
- `ur10e_weighted_orientation_model_sensitivity`: v84 attributes the remaining
  `+1.0 mm`, `0.119 rad` miss to a small orientation-model margin. Critical
  weighted rows exceed the gate by less than `0.00057 rad` with `0.0` qdot
  saturation, while the contact-point versus legacy-center geometry convention
  shifts +1.0 mm terminal orientation by about `0.024 rad`.
- `ur10e_contact_orientation_calibration_margin`: v85 quantifies the
  calibration/definition correction needed to close the hardest remaining
  weighted row. The worst Stage B excess over the `0.119 rad` gate is
  `0.0005664520369604714 rad` (`0.03245531101442353 deg`), equivalent to
  `0.014963398168061883 mm` (`14.963398168061882 um`) under the v84 terminal
  slope proxy. Existing metrics show recovery at `0.11955`, `0.1196`, and
  `0.11995 rad` in specific diagnostic scopes, but no replacement gate is
  accepted without calibrated geometry/contact-normal evidence.
- `ur10e_measured_geometry_readiness`: v86 inspects current lab-vault and
  simulation records read-only. It finds no measured mounted-stack
  TCP/contact point, no verified KSM contact patch convention, no measured
  robot-base-frame plane normal, and no reconciled force source/frame. The
  existing records do not constrain the v85 `0.03246 deg` / `14.96 um` margin
  tightly enough to support gate relaxation or a hardware claim.
- `ur10e_read_only_calibration_measurement_sop`: v87 converts the v86 missing
  evidence into a read-only measurement/SOP artifact with explicit pass/fail
  gates for mounted-stack TCP/contact point, KSM contact patch convention,
  plane normal in robot base frame, force-source/frame reconciliation, and
  orientation-gate semantics. The SOP was not executed in v87 and does not
  authorize motion, writes, zeroing, force control, gate relaxation, or
  hardware-readiness claims.
- `ur10e_read_only_calibration_measurement_template`: v88 converts the v87 SOP
  into reusable worksheets plus a scaffold command and template-only run. The
  run remains `scaffold_created_not_executed` and keeps all hardware, gate
  relaxation, calibration, and contact-model update claims false.
- `ur10e_read_only_calibration_measurement_run_audit`: v89 adds an offline
  verifier for read-only measurement run folders. The v88 scaffold run passed
  with `audit_passed = true` and `violations = []`; this is consistency and
  claim-boundary evidence only, not collected hardware evidence.
- `ur10e_read_only_calibration_measurement_audit_modes`: v90 splits the run
  audit into `scaffold` and `approved-read-only` modes. The approved mode is
  tested for future user-confirmed read-only worksheet rows while preserving
  hard false gates for motion, writes, zeroing/biasing, force control, gate
  relaxation, and hardware readiness.
- `ur10e_read_only_calibration_measurement_evidence_finalizer`: v91 adds an
  offline finalizer that requires the exact read-only approval phrase,
  approved step ID, operator, explicit live-read metadata flag, matching
  YAML/JSON metrics, default scaffold safety state, and worksheet CSV rows
  before converting a scaffold to `approved_read_only_evidence`.
- `ur10e_read_only_calibration_measurement_worksheet_coverage`: v92 adds
  explicit KSM contact patch convention and orientation-gate semantics
  worksheet CSVs. The audit validates their headers when present and rejects
  rows in scaffold mode; the finalizer derives read-only evidence statuses
  from those optional rows.
- `ur10e_read_only_calibration_measurement_orientation_acceptance_boundary`:
  v93 adds `orientation_gate_acceptance` metrics and audit checks. Orientation
  semantics can be collected as read-only evidence, but the accepted gate stays
  `not_accepted` with all accepted-gate fields null unless a separate future
  gate-acceptance audit exists.
- `ur10e_orientation_gate_acceptance_review_template`: v94 adds a separate
  non-default review scaffold and audit path. It is not invoked by read-only
  finalization, defaults to `not_accepted`, keeps source evidence null, and
  preserves gate relaxation and hardware readiness false.
- `ur10e_offline_completion_blockers`: v95 adds a structured audit that marks
  the overall goal incomplete, classifies strict paper-equivalent feasibility
  and robustness as non-final offline-actionable, and classifies approved
  read-only evidence, calibrated contact geometry, orientation-gate
  acceptance, and hardware readiness as blocked on explicit approval/evidence.
- `ur10e_strict_feasibility_blockers`: v96 audits the strict-feasibility
  offline-actionable item. Strict full staged feasibility remains `0 / 4`; the
  three-phase setup terminal state remains `0 / 10`; trajectory feasibility is
  often recoverable at `8 / 10`, but no row satisfies the strict setup gate.
- `ur10e_robustness_blockers`: v97 audits the robustness offline-actionable
  item. Baseline diagnostic stitched sensitivity remains `4 / 9`; positive
  stitched sensitivity remains `37 / 40`; qdot012 and positive-delta recovery
  faces remain diagnostic non-final evidence, not a robustness proof.
- `ur10e_diagnostic_robustness_matrix_candidate`: v98 defines one diagnostic
  robustness matrix candidate from current evidence. It has 12 cells: 7
  diagnostic passes, 1 non-final diagnostic recovery, and 4 failed cells. It
  is not an accepted robustness proof.
- `ur10e_failed_diagnostic_robustness_experiment_matrix`: v99 converts the
  four failed v98 cells into planned offline experiment commands. The run
  status is `planned_not_executed`; no experiments were run and no robustness
  claim is made.
- `ur10e_failed_diagnostic_robustness_experiment_execution`: v100 executes the
  planned `base_z_plus1mm` command and audits it as `executed_unresolved`.
  Start, terminal, path geometry, and duration recovery all remain `0`; the
  other three failed v98 cells were executed in later iterations and also
  remain unresolved.
- `ur10e_positive_fast_timing_failed_cell_execution`: v101 executes the
  planned `positive_fast_timing_0p0075` command and audits it as
  `executed_unresolved`. Stage A passes, but E2 fails Stage B qdot saturation,
  tail qdot utilization, and orientation; the later failed-cell executions also
  remain unresolved.
- `ur10e_positive_orientation_gate_failed_cell_execution`: v102 executes the
  planned `positive_orientation_gate_0p119` command and audits it as
  `executed_unresolved` at the current `0.119 rad` gate. The diagnostic
  boundary first passes at `0.11998 rad`, which is not accepted; the remaining
  failed v98 cell was executed in v103 and also remains unresolved.
- `ur10e_weighted_plus1mm_gate_failed_cell_execution`: v103 executes the
  planned `weighted_plus1mm_0p119_gate` command and audits it as
  `executed_unresolved` at the current `0.119 rad` gate. Diagnostic boundaries
  first pass at `0.11955 rad` for time `0.0075` and `0.1196 rad` for time
  `0.01`; neither gate is accepted, and all four failed v98 cells are now
  executed but unresolved.
- `ur10e_plus1mm_unresolved_diagnostic_probe`: v104 classifies the four
  executed unresolved `+1.0 mm` signatures from current v100-v103 metrics.
  The only qdot-saturation blocker is `positive_fast_timing_0p0075`; the
  weighted current-gate rows have max qdot saturation `0.0` and remain
  orientation-margin/gate-acceptance blocked, while `base_z_plus1mm` still
  lacks start contact, terminal recovery, path geometry, and duration
  recovery.
- `ur10e_positive_fast_timing_e2_qdot_isolation`: v105 isolates the
  `positive_fast_timing_0p0075` E2 row at `+1.0 mm`. The first tested E2
  timing pass is `paper_time_scale = 0.0052`; raising qdot limit alone at
  `paper_time_scale = 0.0075` through `0.3 rad/s` does not recover the row
  because orientation remains above `0.12 rad`.
- `ur10e_positive_fast_e2_orientation_margin`: v106 probes E2-only priority
  formulations at the same `+1.0 mm`, `paper_time_scale = 0.0075`,
  `qdot_limit = 0.15 rad/s`, and `0.12 rad` orientation gate. Weighted rows
  pass E2 with `max_orientation_error_rad = 0.11954627160547111`, zero qdot
  saturation, and tail qdot utilization `0.5177926211135458`, but this does
  not rerun E1-E4 or make `weighted` a canonical controller default.
- `ur10e_positive_fast_weighted_full_cell`: v107 reruns the exact `+1.0 mm`,
  `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, `0.12 rad` full
  E1-E4 face. The linear-primary baseline still fails E2, while
  `weighted_kp0_normal1` and `weighted_kp0_normal30` each pass `4 / 4`.
  This is a weighted-priority diagnostic recovery candidate, not a canonical
  controller change or closed original failed cell.
- `ur10e_base_z_plus1mm_split`: v108 splits the unresolved
  `base_z_plus1mm` row without rerunning MuJoCo. The planned start miss is
  seed-limited because broader seeds recover contact, terminal force/x-y/contact
  passes, terminal/path recovery is blocked by the current `0.08 rad`
  orientation gate, and the run-local `0.12 rad` gate recovers Stage A/path
  but not stitched Stage B. The original failed cell remains open.
- `ur10e_relaxed_base_z_weighted_handoff`: v109 targets the relaxed
  `base_z_plus1mm` Stage B handoff blocker. The linear-primary baseline still
  fails E2 at Stage A durations `15.0 s` and `16.0 s`, while
  `weighted_kp0_normal1` and `weighted_kp0_normal30` each pass `4 / 4` at both
  durations. This is a non-canonical diagnostic recovery candidate, not a
  closed failed cell.

The v49-v50 provenance audits found that the legacy Fig.6 q7 landmark belongs
to a tuned `admittance_proxy` figure-match line with explicit q7 nullspace
bias, not the formula-faithful controller path. v52 implements that tuned line
in Python and matches the legacy figure-match raw trajectory to numerical
precision. Future work must still keep these claim levels separate.

Current next executable step:

- Continue UR10e adapted work by executing only a safe read-only SOP subset
  after explicit user confirmation, using the v93 scaffold, v91 finalizer, and
  v90/v93 verifier for evidence capture; or continue only non-final offline
  simulation/paper-platform work identified by the v95-v109 blocker audits.
  The next offline probe can audit the acceptance boundary for promoting
  weighted priority into a named diagnostic controller profile using v107 and
  v109 evidence, while preserving canonical controller, gate, robustness, and
  failed-cell closure boundaries. Keep strict paper-equivalent setup, v38
  trajectory-after-relaxed-setup, and v63-v109 diagnostic staged labels
  separate.

## Safety Boundary

Do not move the real robot by default. Do not run real force control. Do not
write TCP, payload, URCap settings, zero/bias/filter, or OnRobot configuration.
Real hardware work is limited to read-only state checks unless the user
explicitly approves a separate SOP.

## Git And Versioning Requirements

Manage this as an iterative Git-backed research project.

The GitHub repository `Mingdao007/reproduce-tase` is the intended home for
the reproduction work. All reproduction code, configs, plans, reports, and
lightweight run metadata should be migrated or committed there. Large raw
artifacts should either use Git LFS or be represented by manifests plus clear
local paths, but they still need repo-tracked documentation so future work can
find and reproduce them.

Before making changes:

- Inspect `git status`, current branch, remotes, and recent commits.
- Verify whether a local clone of `Mingdao007/reproduce-tase` already exists.
  If not, clone it or add it as the target remote before beginning new
  implementation work.
- Treat the existing local experiment directory as source material to audit
  and migrate, not as the long-term authoritative repo unless it is explicitly
  connected to `Mingdao007/reproduce-tase`.
- Create or switch to a dedicated branch such as
  `tase-ur10e-mujoco-repro` or `exp/tase-ur10e-v<N>`.
- Do not mix unrelated UR10e/OnRobot work into the reproduction branch.
- Before each major phase, record the baseline commit SHA and dirty diff.

Use versioned iteration:

- Use branches, tags, or documented checkpoints such as
  `v0-paper-audit`, `v1-math-derivation`, `v2-mujoco-smoke`,
  `v3-force-ladder`, `v4-trajectory-matrix`, and `v5-hardware-gate`.
- Commit small reviewable units. Do not bundle plans, derivations, code,
  configs, run outputs, and reports into one opaque commit.
- Every experiment run must record the exact git commit SHA and dirty-tree
  status in its run folder.

## Mandatory Markdown Artifacts

Create or maintain Markdown planning and rollback artifacts:

- `plans/MASTER_PLAN.md`
- `plans/PAPER_TRUTH_EXTRACTION.md`
- `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
- `plans/MUJOCO_ENVIRONMENT_PLAN.md`
- `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
- `plans/EXPERIMENT_MATRIX.md`
- `plans/HARDWARE_GATE_SOP.md`
- `plans/ROLLBACK_AND_CHECKPOINTS.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`

Each Markdown plan must include:

- scope
- assumptions
- exact files touched
- commands to run
- expected outputs
- pass/fail criteria
- rollback point or recovery command
- unresolved risks
- next executable step

At the end of every iteration:

- Update `reports/ITERATION_LOG.md` with date, branch, commit SHA, command
  history, artifacts, result, and next step.
- Update `reports/DECISION_RECORD.md` for major choices such as simulator,
  force source, controller formulation, contact model, TCP assumptions, and
  hardware gate decisions.
- If a run fails, document the failure instead of deleting it.
- If a plan changes, preserve the old reasoning or link to the commit that
  changed it.

## Workflow

1. Audit the current repository state. Start with `git status`, current
   branch, recent commits, `reports/completion_audit.md`, and the v51 split
   claim artifacts. Identify what is already done, what is synthetic, what is
   PDF-verified, and what is still placeholder.
2. Extract paper truth from the PDF: equations, assumptions, dimensions,
   controller law, finite-time RNN dynamics, constraints, Section V
   parameters, Section VI experiment matrix, metrics, and claimed MIAE
   comparison.
3. Write a math derivation artifact explaining every variable and frame.
   Include force-motion decomposition, surface normal/tangent projection,
   orientation compliance, F/T frame transforms, finite-time convergence
   conditions, discrete-time implementation, and QP/constraint formulation.
4. Derive the transfer from the paper's 7DOF Franka setup to UR10e 6DOF.
   State what disappears without redundancy, what becomes infeasible, what
   gets slack variables, and what must be task-prioritized.
5. Define the UR10e controller architecture: force normal task first,
   tangential trajectory second, orientation compliance third, and joint /
   velocity limits always hard. Do not hide `qdot` clipping.
6. Build or repair the MuJoCo simulation. Verify UR10e MJCF/URDF joint order,
   limits, frames, TCP site, contact plane, OnRobot/EOAT approximation or mesh
   use, and force sign convention.
7. Implement tests before trusting plots: finite-time scalar convergence,
   FK/Jacobian numerical checks, contact sign, frame transform, QP feasibility,
   and saturation/slack logging.
8. Run iterative experiments in this order: Fig.5 scalar finite-time check,
   UR10e MuJoCo load smoke, static contact force ladder `[0.5, 1, 2, 5] N`,
   no-contact trajectories, contact trajectories, then article-level E1-E4
   matrix.
9. Produce reports and raw artifacts under the existing experiment directory.
   Every run needs config, raw data, metrics, plots, command, dependency
   versions, seed, git status, and failure notes.
10. Before proposing real UR10e motion, create a separate hardware gate report
    proving simulation stability, read-only RTDE/OnRobot logging readiness,
    measured TCP/payload/CoG, force source decision, emergency stop path, and
    a low-speed low-force SOP.

## Deliverables

- A concise master plan that supersedes stale assumptions in
  `REPRODUCTION_PLAN.md`.
- `reports/math_derivation_ur10e_transfer.md` or equivalent derivation note.
- The mandatory `plans/*.md` and logging artifacts listed above.
- Updated simulation and experiment reports with command evidence.
- A clear next-step checklist after each iteration.
- A completion audit mapping each requirement to concrete evidence: branch,
  commit, files, commands, run directories, plots, metrics, tests, and
  remaining gaps.
- A final handoff that states the exact claim level achieved and explicitly
  lists any claim levels that remain failed.

## Naming And Claims

Until the paper-faithful 7DOF reproduction and the UR10e adapted line are
clearly separated, never call UR10e results "original paper platform
reproduction." Call them "UR10e adapted reproduction." The v51 split gate also
means that "formula convergence" must not be described as "full
paper-equivalent parity" or "Fig.6 q-trajectory parity."
