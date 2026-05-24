# Completion Audit

Date: 2026-05-24

Branch: `exp/tase-ur10e-v61-contact-path-to-diagnostic-target`

## Objective Restatement

The goal is to manage the TASE finite-time force-motion reproduction as a
Git-backed project in `Mingdao007/reproduce-tase`, migrate and audit existing
UR10e/OnRobot/MuJoCo artifacts, maintain plans/logs/decision records, derive
the 7DOF paper method for UR10e 6DOF, verify MuJoCo baselines, run staged
simulations, obey the real-robot safety boundary, and finish with
evidence-backed audits.

The objective has two separate technical claim levels:

1. `paper_equivalent_full_staged_feasibility`: strict setup and trajectory
   gates. This is not achieved.
2. `ur10e_adapted_trajectory_after_relaxed_setup`: relaxed setup budget plus
   strict Stage B trajectory gate. This is achieved for the slowed tilted-plane
   E1-E4 simulation matrix only.

## Evidence Inspected

- `git status --short --branch`
- `git log --oneline --decorate -n 10`
- mandatory plan/report file existence checks
- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.yaml`
- `runs/staged_orientation_three_phase_settle/20260524T110039/summary.yaml`
- `runs/setup_terminal_ik_audit/20260524T111150/metrics.yaml`
- `runs/relaxed_setup_budget_eval/20260524T111859/metrics.yaml`
- `configs/paper_truth.yaml`
- `reports/section_v_z0_audit.md`
- `reports/paper_7dof_executable_diagnostic_report.md`
- `runs/paper_7dof_section_v/20260524T113608/metrics.yaml`
- `reports/paper_7dof_contact_loop_report.md`
- `runs/paper_7dof_section_v/20260524T114244/metrics.yaml`
- `reports/paper_7dof_kkt_contact_recovery_report.md`
- `runs/paper_7dof_section_v/20260524T114736/metrics.yaml`
- `configs/paper_platform_parity.yaml`
- `reports/paper_7dof_30s_candidate_report.md`
- `runs/paper_7dof_section_v/20260524T120439/metrics.yaml`
- `reports/paper_7dof_fig5_sweep_report.md`
- `runs/paper_7dof_fig5_r_sweep/20260524T121033/summary.yaml`
- `reports/paper_7dof_uncapped_candidate_report.md`
- `runs/paper_7dof_section_v/20260524T121503/metrics.yaml`
- `reports/paper_7dof_q7_variant_probe_report.md`
- `runs/paper_7dof_q7_variant_probe/20260524T122345/summary.yaml`
- `reports/paper_7dof_fig6_raw_provenance_report.md`
- `runs/paper_7dof_fig6_raw_provenance/20260524T123130/metrics.yaml`
- `reports/legacy_figure_match_source_audit_report.md`
- `runs/legacy_figure_match_source_audit/20260524T123651/metrics.yaml`
- `reports/paper_platform_split_claim_report.md`
- `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml`
- `reports/paper_7dof_tuned_figure_match_candidate_report.md`
- `runs/paper_7dof_section_v/20260524T134441/metrics.yaml`
- `reports/paper_7dof_tuned_figure_match_provenance_report.md`
- `runs/paper_7dof_fig6_raw_provenance/20260524T134549/metrics.yaml`
- `reports/paper_platform_split_evidence_report.md`
- `reports/tcp_contact_model_audit_report.md`
- `runs/tcp_contact_model_audit/20260524T135607/metrics.yaml`
- `runs/setup_terminal_ik_audit/20260524T135619/metrics.yaml`
- `reports/tcp_contact_point_model_variant_report.md`
- `runs/tcp_contact_model_audit/20260524T140535/metrics.yaml`
- `runs/setup_terminal_ik_audit/20260524T140539/metrics.yaml`
- `reports/broad_terminal_feasibility_audit_report.md`
- `runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml`
- `reports/contact_manifold_gate_audit_report.md`
- `runs/contact_manifold_gate_audit/20260524T142404/metrics.yaml`
- `reports/adapted_terminal_setup_gate_report.md`
- `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml`
- `configs/ur10e_adapted_stage_a_target.yaml`
- `reports/stage_a_target_selection_report.md`
- `reports/stage_a_target_handoff_report.md`
- `runs/stage_a_target_handoff_eval/20260524T144654/metrics.yaml`
- `reports/qdot_aware_diagnostic_handoff_report.md`
- `runs/stage_a_target_handoff_eval/20260524T145433/metrics.yaml`
- `reports/paper_platform_parity_gate_report.md`
- `runs/paper_platform_parity_eval/20260524T121542/metrics.yaml`
- `plans/HARDWARE_GATE_SOP.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Prompt-To-Artifact Checklist

| Requirement | Evidence | Status |
|---|---|---|
| Use `Mingdao007/reproduce-tase` as target repo | `origin` is `git@github.com:Mingdao007/reproduce-tase.git`; decisions D001-D003; v37-v60 branches pushed and GitHub-verified; v61 is the current iteration branch | Done |
| Keep work Git-backed with dedicated branches | Iteration branches through `exp/tase-ur10e-v61-contact-path-to-diagnostic-target`; latest local branch is `exp/tase-ur10e-v61-contact-path-to-diagnostic-target` | Done |
| Maintain mandatory plans | All required `plans/*.md` files exist: master, paper truth, math transfer, MuJoCo, controller, experiment matrix, hardware gate, rollback | Done |
| Preserve next-thread goal prompt | `docs/goal.md` includes the short prompt, authoritative local clone, v61 branch/code commit, claim boundary, and next executable controller target | Done |
| Maintain iteration log and decision record | `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`; decisions through D066 as of v61 | Done |
| Migrate reproduction code/configs/reports/lightweight metadata | Repo contains `src/tase_repro`, `scripts`, `configs`, `reports`, `runs/*` summaries, and `runs/RUN_ARTIFACTS_MANIFEST.md` | Done |
| Keep raw/heavy artifacts out of ordinary Git or manifest them | `.npz` raw arrays remain ignored; manifest documents tracked summaries and omitted raw artifacts | Done |
| Extract paper truth from PDF | `reports/paper_truth_extraction.md`, `reports/orientation_signal_ambiguity_audit.md`, `reports/section_v_z0_audit.md`, `configs/paper_truth.yaml` | Done for extraction fields; Section V orientation and `z0` remain paper ambiguities |
| Derive paper 7DOF method to UR10e 6DOF | `reports/math_derivation_ur10e_transfer.md` includes force-motion decomposition, orientation, slack/priority, and v38 implication | Done for current adapted line |
| Verify MuJoCo baseline | Smoke, force ladder, force-feedback, trajectory, tilted-plane, and staged reports in `reports/*`; run manifest lists artifacts | Done for approximate simulation baseline |
| Implement tests before trusting plots | `scripts/run_tests.sh` used throughout; latest v61 validation was `100 passed in 2.55s`; `git diff --check` passed | Done for current code |
| Run staged simulations | v29-v38 staged runs and reports; v33 slowed E1-E4 matrix; v35-v37 setup probes | Done |
| Separate UR10e adapted results from paper-platform reproduction | README claim boundary plus D043; relaxed label explicitly says not paper-equivalent | Done |
| Paper-platform 7DOF executable line | `src/tase_repro/panda_kinematics.py`, `src/tase_repro/paper_7dof.py`, `scripts/run_paper_7dof_section_v.py`, v41 KKT run `20260524T113608`, v42 pinv run `20260524T114244`, v43 capped-integral KKT run `20260524T114736` | Diagnostic line exists and capped-integral KKT contact passes; not paper-equivalent parity |
| Paper-platform parity gate | `configs/paper_platform_parity.yaml`, `src/tase_repro/paper_platform_parity.py`, `scripts/evaluate_paper_platform_parity.py`, `runs/paper_platform_parity_eval/20260524T121542/metrics.yaml` | Gate exists; v47 passes duration, Fig.5 coverage, tail convergence, and paper-assumption checks but strict parity fails |
| Paper-platform q7 variant probe | `scripts/run_paper_7dof_q7_variant_probe.py`, `reports/paper_7dof_q7_variant_probe_report.md`, `runs/paper_7dof_q7_variant_probe/20260524T122345/summary.yaml` | v48 shows q7 mismatch persists across current supported Python solver/orientation/cap variants |
| Paper-platform Fig.6 raw provenance audit | `scripts/compare_paper_7dof_fig6_raw_provenance.py`, `reports/paper_7dof_fig6_raw_provenance_report.md`, `runs/paper_7dof_fig6_raw_provenance/20260524T123130/metrics.yaml` | v49 shows Python Panda FK/Jacobian matches sampled legacy raw states; figure-match q7 is tied to legacy `admittance_proxy` landmark line |
| Legacy figure-match source audit | `scripts/audit_legacy_figure_match_source.py`, `reports/legacy_figure_match_source_audit_report.md`, `runs/legacy_figure_match_source_audit/20260524T123651/metrics.yaml` | v50 shows figure-match has eight non-paper-faithful tuning knobs and explicit q7 nullspace bias |
| Split paper-platform claim gate | `src/tase_repro/paper_platform_parity.py`, `reports/paper_platform_split_claim_report.md`, `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml` | v51 separates formula convergence from tuned figure-match landmark evidence; formula convergence passes, tuned landmark fails, old strict aggregate fails |
| Python tuned figure-match candidate | `src/tase_repro/paper_7dof.py`, `reports/paper_7dof_tuned_figure_match_candidate_report.md`, `runs/paper_7dof_section_v/20260524T134441/metrics.yaml` | v52 implements the explicitly tuned candidate and reproduces q7@22s with error `6.681366571115177e-11 rad` |
| Tuned figure-match raw provenance | `scripts/compare_paper_7dof_fig6_raw_provenance.py`, `reports/paper_7dof_tuned_figure_match_provenance_report.md`, `runs/paper_7dof_fig6_raw_provenance/20260524T134549/metrics.yaml` | v52 matches legacy `figure_match` with joint RMSE `6.081574510252252e-09 rad`; this is tuned landmark evidence only |
| Formalize split paper-platform evidence | `reports/paper_platform_split_evidence_report.md` | Done; accepted wording keeps formula-convergence and tuned-landmark claims separate and leaves full paper-equivalent numerical parity unclaimed |
| UR10e TCP/contact model audit | `reports/tcp_contact_model_audit_report.md`, `runs/tcp_contact_model_audit/20260524T135607/metrics.yaml` | v53 validates the current convention problem: the 85 mm site is coincident with the sphere center, while the simulated contact surface is about 45 mm farther along the contact normal |
| UR10e TCP contact-point model variant | `reports/tcp_contact_point_model_variant_report.md`, `runs/tcp_contact_model_audit/20260524T140535/metrics.yaml` | v54 adds a named contact-point convention where the 85 mm site is separated from the sphere center; still simulation-only and not hardware-ready |
| Broad terminal feasibility audit | `reports/broad_terminal_feasibility_audit_report.md`, `runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml` | v55 gates force/contact on the target `contact_plane` / `contact_tip` pair and finds `0 / 513` broad terminal passes |
| Contact-manifold gate audit | `reports/contact_manifold_gate_audit_report.md`, `runs/contact_manifold_gate_audit/20260524T142404/metrics.yaml` | v56 finds `0 / 161` strict passes from target-contact neighborhoods and identifies x/y, force, and orientation as a gate-definition conflict |
| Adapted terminal setup diagnostic gate | `configs/ur10e_adapted_acceptance.yaml`, `reports/adapted_terminal_setup_gate_report.md`, `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml` | v57 adds a diagnostic-only terminal setup label and finds `1 / 513` passing candidates; no path, trajectory, paper-equivalent, or hardware claim |
| Stage A target selection | `configs/ur10e_adapted_stage_a_target.yaml`, `reports/stage_a_target_selection_report.md`, `reports/DECISION_RECORD.md` D063 | v58 selects `ur10e_adapted_terminal_setup_diagnostic` as the next Stage A simulation prototype target; not a controller, path, trajectory, paper-equivalent, or hardware claim |
| Diagnostic target handoff audit | `src/tase_repro/stage_a_target_handoff.py`, `scripts/evaluate_stage_a_target_handoff.py`, `reports/stage_a_target_handoff_report.md`, `runs/stage_a_target_handoff_eval/20260524T144654/metrics.yaml` | v59 starts from the selected diagnostic q and finds `0 / 4` handoff passes; target contact, force, x/y, and diagnostic orientation stay within bounds, but qdot saturation gates fail |
| Qdot-aware diagnostic handoff | `reports/qdot_aware_diagnostic_handoff_report.md`, `runs/stage_a_target_handoff_eval/20260524T145433/metrics.yaml` | v60 starts from the selected diagnostic q and finds `4 / 4` handoff passes with slowed timing, lower force gain, diagnostic-orientation hold, target-pair contact accounting, and no qdot saturation; still not a Stage A path |
| Stage A contact path audit | `src/tase_repro/stage_a_contact_path.py`, `scripts/audit_stage_a_contact_path.py`, `reports/stage_a_contact_path_audit_report.md`, `runs/stage_a_contact_path_audit/20260524T151201/metrics.yaml` | v61 finds an offline 128-knot quasi-static contact path from ordinary initial q to the selected diagnostic target; path gate and terminal diagnostic gate pass with minimum qdot-limited duration `14.332635022800167 s`; still not an online controller or hardware claim |
| Strict full staged feasibility | v33 strict full staged `0 / 4`; v35 setup gate `0 / 10`; v36 setup gate `0 / 10`; v37 terminal IK `0 / 65`; v53 terminal IK rerun `0 / 65`; v54 terminal IK rerun `0 / 65`; v55 broad terminal IK `0 / 513`; v56 contact-manifold gate audit `0 / 161` | Not achieved |
| UR10e adapted relaxed simulation claim | v38 evaluation: relaxed setup `4 / 4`, trajectory feasibility `4 / 4`, adapted label `4 / 4`, strict full staged `0 / 4` | Achieved for slowed tilted-plane E1-E4 only |
| Hardware safety boundary | `plans/HARDWARE_GATE_SOP.md`; reports repeatedly state no motion/writes; no hardware commands were run in these iterations | Maintained |
| Hardware gate before real motion | Only SOP exists; no `reports/hardware_gate_report.md`; TCP/payload/force source unresolved | Not achieved |
| Finish with evidence-backed audit | This file maps the objective to evidence and gaps | Done for current state |

## Current Accepted Claim

The project can currently claim:

```text
UR10e adapted slowed tilted-plane E1-E4 simulation:
  trajectory-after-relaxed-setup pass count = 4 / 4
  strict full staged feasibility pass count = 0 / 4
  hardware readiness = false
```

Evidence:

- `reports/relaxed_setup_budget_report.md`
- `configs/ur10e_adapted_acceptance.yaml`
- `runs/relaxed_setup_budget_eval/20260524T111859/metrics.yaml`

The separate paper-platform line can additionally claim:

```text
paper_platform_7dof_contact_stabilized_diagnostic:
  contact-force tail pass = true
  tail contact fraction = 1.0
  tail mean force error = 0.013764149103712913 N
  paper-faithful KKT parity = false
```

Evidence:

- `reports/paper_7dof_contact_loop_report.md`
- `runs/paper_7dof_section_v/20260524T114244/metrics.yaml`

The KKT paper-platform line can additionally claim:

```text
paper_platform_7dof_capped_integral_kkt_contact_diagnostic:
  contact-force tail pass = true
  tail contact fraction = 1.0
  tail mean force error = 0.06720487008205062 N
  paper-equivalent numerical parity = false
```

Evidence:

- `reports/paper_7dof_kkt_contact_recovery_report.md`
- `runs/paper_7dof_section_v/20260524T114736/metrics.yaml`

The split paper-platform gate can additionally claim:

```text
paper_platform_7dof_split_claims:
  formula convergence pass = true
  figure-match landmark pass = false
  legacy strict aggregate pass = false
  tail convergence against formula-faithful legacy reference = pass
  duration coverage = true
  Fig.6 q7-at-22 s landmark = false
  Python Fig.5 r-sweep coverage = true
  force-integral assumption compatibility = true
```

Evidence:

- `reports/paper_platform_parity_gate_report.md`
- `reports/paper_platform_split_claim_report.md`
- `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml`

The 30 s paper-platform candidate can additionally claim:

```text
paper_platform_7dof_30s_capped_integral_kkt_candidate:
  execution_success = true
  contact-force tail pass = true
  duration = 30.0 s
  q7 at 22 s = 1.6755097668200787 rad
  q7 error to figure-match 2.5 rad = 0.8244902331799213 rad
```

Evidence:

- `reports/paper_7dof_30s_candidate_report.md`
- `runs/paper_7dof_section_v/20260524T120439/metrics.yaml`

The Fig.5 paper-platform sweep can additionally claim:

```text
paper_platform_7dof_fig5_r_sweep_coverage:
  r values covered = 0.2, 0.4, 0.6, 0.8, 1.0
  per-r execution_success = true
  required window = 2.0 s
  Fig.5 numerical parity = false
```

Evidence:

- `reports/paper_7dof_fig5_sweep_report.md`
- `runs/paper_7dof_fig5_r_sweep/20260524T121033/summary.yaml`

The uncapped paper-platform candidate can additionally claim:

```text
paper_platform_7dof_uncapped_kkt_candidate:
  execution_success = true
  contact-force tail pass = true
  force_integral_limit = infinity
  q7 at 22 s = 1.6680622878116045 rad
  q7 error to figure-match 2.5 rad = 0.8319377121883955 rad
```

Evidence:

- `reports/paper_7dof_uncapped_candidate_report.md`
- `runs/paper_7dof_section_v/20260524T121503/metrics.yaml`

The q7 variant probe can additionally claim:

```text
paper_platform_7dof_q7_variant_probe:
  variant count = 8
  all execution success = true
  q7 range at 22 s = 1.661263839866546 to 1.6835894792145727 rad
  q7 range width = 0.02232563934802667 rad
  closest q7 error to figure-match 2.5 rad = 0.8164105207854273 rad
  figure-match tolerance pass count = 0 / 8
```

Evidence:

- `reports/paper_7dof_q7_variant_probe_report.md`
- `runs/paper_7dof_q7_variant_probe/20260524T122345/summary.yaml`

The Fig.6 raw provenance audit can additionally claim:

```text
paper_platform_7dof_fig6_raw_provenance:
  Python FK/Jacobian matches sampled legacy raw states = true
  legacy formula force loop = paper_literal
  legacy figure-match force loop = admittance_proxy
  Python candidate force loop = paper_literal
  legacy figure-match q7@22s = 2.4999999999358065 rad
  Python candidate q7@22s = 1.6680622878116045 rad
  legacy figure-match q7 upper-limit exact samples = 17829
  legacy figure-match first near-upper-limit time = 11.872999999998859 s
```

Evidence:

- `reports/paper_7dof_fig6_raw_provenance_report.md`
- `runs/paper_7dof_fig6_raw_provenance/20260524T123130/metrics.yaml`

The legacy figure-match source audit can additionally claim:

```text
paper_platform_7dof_legacy_figure_match_source_audit:
  figure_match_is_formula_faithful = false
  non-paper-faithful tuning knob count = 8
  explicit q7 nullspace bias = true
  figure_match_force_loop_mode = admittance_proxy
  figure_match_solver_mode = pinv_bounded
  figure_match_orientation_mode = normal_only
  figure_match_q7_nullspace_speed = 0.35
  raw figure-match q7 upper-limit exact samples = 17829
```

Evidence:

- `reports/legacy_figure_match_source_audit_report.md`
- `runs/legacy_figure_match_source_audit/20260524T123651/metrics.yaml`

The split claim-level gate can additionally claim:

```text
paper_platform_7dof_formula_convergence:
  pass = true
  boundary = tail convergence and coverage only; not full q-trajectory parity
paper_platform_7dof_figure_match_landmark:
  pass = false
paper_platform_7dof_legacy_strict_all_checks:
  pass = false
```

Evidence:

- `reports/paper_platform_split_claim_report.md`
- `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml`

The tuned figure-match candidate can additionally claim:

```text
paper_platform_7dof_tuned_figure_match_candidate:
  execution_success = true
  contact_force_tail_success = true
  q7@22s error to 2.5 rad = 6.681366571115177e-11
  legacy figure-match q7@22s delta = 2.6201263381153694e-12 rad
  legacy figure-match joint RMSE = 6.081574510252252e-09 rad
  formula-faithful parity = false by claim boundary
```

Evidence:

- `reports/paper_7dof_tuned_figure_match_candidate_report.md`
- `reports/paper_7dof_tuned_figure_match_provenance_report.md`
- `runs/paper_7dof_section_v/20260524T134441/metrics.yaml`
- `runs/paper_7dof_fig6_raw_provenance/20260524T134549/metrics.yaml`

The UR10e TCP/contact model audit can additionally claim:

```text
ur10e_tcp_contact_model_audit:
  config TCP guess matches EOAT note distance = true
  site coincident with contact geom center = true
  contact sphere radius = 0.045 m
  simulated parent-to-sphere-surface distance = 0.12955222618906498 m
  strict terminal setup rerun pass count = 0 / 65
  hardware-ready TCP/contact model = false
```

Evidence:

- `reports/tcp_contact_model_audit_report.md`
- `runs/tcp_contact_model_audit/20260524T135607/metrics.yaml`
- `runs/setup_terminal_ik_audit/20260524T135619/metrics.yaml`

The UR10e TCP contact-point model variant can additionally claim:

```text
ur10e_tcp_contact_point_model_variant:
  85 mm TCP site separated from sphere center = true
  contact sphere center local position = [0, 0, 0.045] m
  contact-surface offset unresolved flag = false
  site-to-sphere-surface projection at initial tilted posture = 0.0006836511144550518 m
  strict terminal setup rerun pass count = 0 / 65
  hardware-ready TCP/contact model = false
```

Evidence:

- `reports/tcp_contact_point_model_variant_report.md`
- `runs/tcp_contact_model_audit/20260524T140535/metrics.yaml`
- `runs/setup_terminal_ik_audit/20260524T140539/metrics.yaml`

The broad terminal feasibility audit can additionally claim:

```text
ur10e_broad_terminal_feasibility_audit:
  target contact pair enforced = contact_plane / contact_tip
  broad candidate count = 513
  strict terminal setup pass count = 0 / 513
  self-collision force false-positive path closed = true
  global infeasibility proof = false
```

Evidence:

- `reports/broad_terminal_feasibility_audit_report.md`
- `runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml`

The contact-manifold gate audit can additionally claim:

```text
ur10e_contact_manifold_gate_audit:
  target-contact neighborhood seed count = 161
  strict xy_force_orientation pass count = 0 / 161
  xy_force residual = orientation error 0.14697007178233126 rad
  xy_orientation residual = target contact absent and force error 5.0 N
  force_orientation residual = x/y error 0.014127706733724453 m
  gate-definition conflict identified = true
  global infeasibility proof = false
```

Evidence:

- `reports/contact_manifold_gate_audit_report.md`
- `runs/contact_manifold_gate_audit/20260524T142404/metrics.yaml`

The adapted terminal setup diagnostic gate can additionally claim:

```text
ur10e_adapted_terminal_setup_diagnostic:
  claim scope = diagnostic terminal setup only
  pass count = 1 / 513
  max terminal x/y error = 0.004 m
  max terminal orientation error = 0.08 rad
  max terminal force error = 0.25 N
  path feasibility = false
  trajectory feasibility = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/adapted_terminal_setup_gate_report.md`
- `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml`

The Stage A target selection can additionally claim:

```text
ur10e_stage_a_target_selection:
  selected target label = ur10e_adapted_terminal_setup_diagnostic
  source diagnostic gate pass count = 1 / 513
  source target seed label = initial
  controller implementation = false
  path feasibility = false
  trajectory feasibility = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `configs/ur10e_adapted_stage_a_target.yaml`
- `reports/stage_a_target_selection_report.md`
- `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml`

The diagnostic target handoff audit can additionally claim:

```text
ur10e_diagnostic_target_handoff:
  selected target label = ur10e_adapted_terminal_setup_diagnostic
  trajectory count = 4
  handoff pass count = 0 / 4
  target contact present fraction = 1.0 for all rows
  force/x-y/diagnostic orientation gates = pass for all rows
  qdot saturation gates = fail for all rows
  path feasibility = false
  trajectory feasibility = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stage_a_target_handoff_report.md`
- `runs/stage_a_target_handoff_eval/20260524T144654/metrics.yaml`

The qdot-aware diagnostic handoff can additionally claim:

```text
ur10e_qdot_aware_diagnostic_handoff:
  selected target label = ur10e_adapted_terminal_setup_diagnostic
  trajectory count = 4
  handoff pass count = 4 / 4
  paper_time_scale = 0.01
  force_gain = 1e-4
  orientation_kp = 0.0
  target contact present fraction = 1.0 for all rows
  qdot saturation fraction = 0.0 for all rows
  Stage A path feasibility = false
  strict trajectory feasibility = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/qdot_aware_diagnostic_handoff_report.md`
- `runs/stage_a_target_handoff_eval/20260524T145433/metrics.yaml`

## Missing Or Weakly Verified Requirements

- Strict paper-equivalent full staged feasibility is not achieved.
- Paper-platform 7DOF Franka/Panda reproduction now has a separate executable
  diagnostic line, a capped-integral KKT variant that passes tail force, and a
  strict parity gate. The gate fails, so this is still not paper-equivalent
  numerical parity. v45 closes the duration-coverage gap, v46 closes the
  Fig.5 coverage gap, v47 closes the force-integral-cap assumption gap, and
  v48 shows the q7 landmark mismatch is insensitive to the current supported
  Python solver/orientation/cap variants. v49 shows the q7 mismatch is not a
  Python Panda FK/Jacobian porting error and ties the `2.5 rad` landmark to
  the legacy `admittance_proxy` figure-match line. v50 shows that line has
  explicit non-paper-faithful tuning, including q7 nullspace bias. v51 splits
  the claim levels so formula convergence can pass separately. v52 implements
  the tuned candidate and reproduces the legacy figure-match trajectory, but
  this remains tuned landmark evidence rather than formula-faithful parity.
- Section V `z0` is now verified undefined in the simulation text; future code
  still needs an explicit adapted convention if it implements Section V.
- UR10e MJCF, 85 mm TCP guess, payload, CoG, and contact geometry remain
  approximate or unverified for hardware use. v53 narrowed the TCP/contact
  issue: the 85 mm site is coincident with the colliding sphere center, while
  the simulated contact surface is one sphere radius away. v54 adds a separate
  contact-point model variant that resolves that convention in simulation, but
  it is still unmeasured and the strict terminal setup gate still fails.
- OnRobot/RTDE force-source reconciliation remains unresolved.
- Hardware gate report is not produced, and no real robot motion is authorized.
- The relaxed setup budget is an explicit adapted-simulation label, not a
  mathematical solution to the strict Stage A setup gate.
- The v55 broad terminal audit is still a local least-squares search. It
  closes self-collision false positives but does not prove global terminal
  infeasibility on the contact manifold.
- The v56 contact-manifold audit identifies a gate-definition conflict from
  target-contact neighborhoods, but it is still not a formal mathematical
  proof over all UR10e joint configurations.
- The v57 diagnostic terminal setup gate is only a bookkeeping label for
  terminal-state evidence. It does not prove path feasibility, trajectory
  feasibility, paper-equivalent feasibility, or hardware readiness.
- The v58 Stage A target selection only chooses the diagnostic terminal setup
  as the next simulation-controller target. It does not implement a
  controller and does not prove path feasibility, trajectory feasibility,
  paper-equivalent feasibility, or hardware readiness.
- The v59 diagnostic target handoff starts directly from the selected q and
  therefore still does not implement a Stage A path. It also fails all E1-E4
  trajectory rows on qdot saturation, so it does not prove trajectory
  feasibility.
- The v60 qdot-aware diagnostic handoff passes from the selected q, but it
  still does not implement a Stage A path to that q and it uses slowed timing
  plus lower force gain. It remains direct-target handoff evidence only, not a
  strict trajectory or paper-equivalent claim.
- The v61 contact path audit finds an offline quasi-static contact-manifold
  path from the ordinary initial q to the selected q, but it does not prove an
  online Stage A controller can track the path, does not prove robustness to
  contact/model transients, and does not authorize hardware use. It also does
  not keep the force-normal orientation under the terminal diagnostic threshold
  at every intermediate knot.
- The v43-v51 paper-platform line inherits unverified Panda DH parameters,
  uses a documented force-normal orientation interpretation, and passes
  force/contact with the current uncapped KKT candidate. It has Fig.5 r-sweep
  coverage but not Fig.5 numerical parity, and it has a
  measured q7-at-22 s mismatch against the figure-match legacy reference that
  persists across the v48 variant matrix. v49 verifies the Python kinematics
  port against legacy raw states, and v50 resolves that the tuned
  `admittance_proxy` line should not be a formula-faithful parity target.
  v51 splits the gate accordingly, and v52 reproduces the tuned landmark in a
  separate Python candidate. Full paper-equivalent numerical parity remains
  incomplete because the formula-faithful and tuned-landmark evidence are not
  the same claim.

## Audit Conclusion

The overall goal is not complete. The repository is now in a strong
simulation-audit state for a UR10e adapted result, but it has not achieved
strict paper-equivalent full staged feasibility or hardware readiness.

Do not mark the active goal complete from the current evidence.

## Next Executable Step

Track the v61 offline contact path with an online qdot-aware Stage A
controller, then connect that controller to the v60 slowed handoff under one
explicit timing and acceptance policy. Keep v61 labeled as offline path
evidence until an executable controller tracks it. Keep strict paper-equivalent
setup and v38 trajectory-after-relaxed-setup as separate labels. Any hardware
work still requires measured mounted-stack geometry and a separate approved SOP.
