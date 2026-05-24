# Completion Audit

Date: 2026-05-24

Branch: `exp/tase-ur10e-v79-stage-b-priority-posture-probe`

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
- `reports/stage_a_contact_path_audit_report.md`
- `runs/stage_a_contact_path_audit/20260524T151201/metrics.yaml`
- `reports/stage_a_contact_path_tracking_report.md`
- `runs/stage_a_contact_path_tracking/20260524T152346/metrics.yaml`
- `reports/stitched_stage_a_handoff_report.md`
- `runs/stitched_stage_a_handoff_eval/20260524T152807/metrics.yaml`
- `reports/stitched_stage_a_handoff_sensitivity_report.md`
- `runs/stitched_stage_a_handoff_sensitivity/20260524T161111/metrics.yaml`
- `reports/stitched_stage_a_handoff_timing_margin_report.md`
- `runs/stitched_stage_a_handoff_timing_margin/20260524T162005/metrics.yaml`
- `reports/stage_a_base_z_recovery_report.md`
- `runs/stage_a_base_z_recovery/20260524T163746/metrics.yaml`
- `reports/stage_a_base_z_bracket_report.md`
- `runs/stage_a_base_z_bracket/20260524T165411/metrics.yaml`
- `reports/positive_base_z_start_contact_report.md`
- `runs/positive_base_z_start_contact/20260524T170350/metrics.yaml`
- `reports/positive_terminal_orientation_report.md`
- `runs/positive_terminal_orientation/20260524T171705/metrics.yaml`
- `reports/positive_relaxed_orientation_recovery_report.md`
- `runs/positive_relaxed_orientation_recovery/20260524T172909/metrics.yaml`
- `reports/positive_stage_b_e2_margin_report.md`
- `runs/positive_stage_b_e2_margin/20260524T192129/metrics.yaml`
- `reports/positive_full_stitched_recovery_report.md`
- `runs/positive_full_stitched_recovery/20260524T192854/metrics.yaml`
- `reports/positive_stitched_sensitivity_report.md`
- `runs/positive_stitched_sensitivity/20260524T193845/metrics.yaml`
- `reports/qdot012_stage_a_margin_report.md`
- `runs/qdot012_stage_a_margin/20260524T194817/metrics.yaml`
- `reports/qdot012_positive_stitched_matrix_report.md`
- `runs/positive_full_stitched_recovery/20260524T195501/metrics.yaml`
- `reports/positive_timing_boundary_report.md`
- `runs/positive_timing_boundary/20260524T200236/metrics.yaml`
- `reports/positive_orientation_gate_boundary_report.md`
- `runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml`
- `reports/stage_b_orientation_kp_probe_report.md`
- `runs/stage_b_orientation_kp_probe/20260524T222953/metrics.yaml`
- `reports/stage_b_priority_recovery_report.md`
- `runs/stage_b_priority_recovery/20260524T224404/metrics.yaml`
- `reports/paper_platform_parity_gate_report.md`
- `runs/paper_platform_parity_eval/20260524T121542/metrics.yaml`
- `plans/HARDWARE_GATE_SOP.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Prompt-To-Artifact Checklist

| Requirement | Evidence | Status |
|---|---|---|
| Use `Mingdao007/reproduce-tase` as target repo | `origin` is `git@github.com:Mingdao007/reproduce-tase.git`; decisions D001-D003; v37-v78 branches pushed and GitHub-verified; v79 is the current iteration branch pending push | Done |
| Keep work Git-backed with dedicated branches | Iteration branches through `exp/tase-ur10e-v79-stage-b-priority-posture-probe`; latest local branch is `exp/tase-ur10e-v79-stage-b-priority-posture-probe` | Done |
| Maintain mandatory plans | All required `plans/*.md` files exist: master, paper truth, math transfer, MuJoCo, controller, experiment matrix, hardware gate, rollback | Done |
| Preserve next-thread goal prompt | `docs/goal.md` includes the short prompt, authoritative local clone, v79 branch/run, claim boundary, and next executable full-positive/stress-test target | Done |
| Maintain iteration log and decision record | `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`; decisions through D084 as of v79 | Done |
| Migrate reproduction code/configs/reports/lightweight metadata | Repo contains `src/tase_repro`, `scripts`, `configs`, `reports`, `runs/*` summaries, and `runs/RUN_ARTIFACTS_MANIFEST.md` | Done |
| Keep raw/heavy artifacts out of ordinary Git or manifest them | `.npz` raw arrays remain ignored; manifest documents tracked summaries and omitted raw artifacts | Done |
| Extract paper truth from PDF | `reports/paper_truth_extraction.md`, `reports/orientation_signal_ambiguity_audit.md`, `reports/section_v_z0_audit.md`, `configs/paper_truth.yaml` | Done for extraction fields; Section V orientation and `z0` remain paper ambiguities |
| Derive paper 7DOF method to UR10e 6DOF | `reports/math_derivation_ur10e_transfer.md` includes force-motion decomposition, orientation, slack/priority, and v38 implication | Done for current adapted line |
| Verify MuJoCo baseline | Smoke, force ladder, force-feedback, trajectory, tilted-plane, and staged reports in `reports/*`; run manifest lists artifacts | Done for approximate simulation baseline |
| Implement tests before trusting plots | `scripts/run_tests.sh` used throughout; latest v79 validation was `115 passed in 2.54s`; `python3 -m py_compile scripts/evaluate_stitched_stage_a_handoff.py scripts/audit_stage_b_priority_recovery.py` and `git diff --check` passed | Done for current code |
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
| Stage A contact path tracking | `src/tase_repro/stage_a_contact_path_tracking.py`, `scripts/track_stage_a_contact_path.py`, `reports/stage_a_contact_path_tracking_report.md`, `runs/stage_a_contact_path_tracking/20260524T152346/metrics.yaml` | v62 tracks the v61 path over `15.0 s`; tracking gate and terminal diagnostic gate pass with max qdot `0.14332635022814824 rad/s`, zero qdot saturation, and target contact throughout; still not connected to Stage B |
| Stitched diagnostic Stage A plus handoff | `scripts/evaluate_stitched_stage_a_handoff.py`, `reports/stitched_stage_a_handoff_report.md`, `runs/stitched_stage_a_handoff_eval/20260524T152807/metrics.yaml` | v63 executes the v62 Stage A tracker and v60 slowed handoff in one script; stitched gate passes and Stage B is `4 / 4`; still diagnostic-label simulation evidence only |
| Stitched diagnostic sensitivity audit | `src/tase_repro/stitched_sensitivity.py`, `scripts/audit_stitched_stage_a_handoff_sensitivity.py`, `reports/stitched_stage_a_handoff_sensitivity_report.md`, `runs/stitched_stage_a_handoff_sensitivity/20260524T161111/metrics.yaml` | v64 evaluates nine sensitivity cases around v63; stitched pass count is `4 / 9`, failing 1 mm base-z/contact perturbations, `stage_a_14s`, `qdot_limit_0p12`, and `paper_time_scale_0p02`; robustness is not achieved |
| Stitched diagnostic timing-margin audit | `scripts/audit_stitched_stage_a_handoff_sensitivity.py --case-set timing-margin`, `reports/stitched_stage_a_handoff_timing_margin_report.md`, `runs/stitched_stage_a_handoff_timing_margin/20260524T162005/metrics.yaml` | v65 evaluates seven timing-margin cases; `stage_a_14p5_recovery`, `qdot012_stage_a_18p0_recovery`, and `paper_time_scale_0p012_recovery` pass, while nearby reference-fail cases still fail; base-z/contact recovery remains unaddressed |
| Stage A base-z recovery audit | `src/tase_repro/base_z_recovery.py`, `scripts/audit_stage_a_base_z_recovery.py`, `reports/stage_a_base_z_recovery_report.md`, `runs/stage_a_base_z_recovery/20260524T163746/metrics.yaml` | v66 evaluates perturbation-aware start rebalance, terminal search, path reoptimization, and stitched handoff for three base-z cases; `base_z_minus_1mm_stage_a_16s_recovery` passes, while the exact `15.0 s` `base_z_minus_1mm` reference and `base_z_plus_1mm` remain unresolved |
| Stage A base-z bracket audit | `scripts/audit_stage_a_base_z_bracket.py`, `reports/stage_a_base_z_bracket_report.md`, `runs/stage_a_base_z_bracket/20260524T165411/metrics.yaml` | v67 evaluates 13 compact base-z bracket cases; nominal, `-0.25 mm`, and `-0.5 mm` recover at `15.0 s`, `-1.0 mm` recovers only at `16.0 s`, `-0.75 mm` exposes a path anomaly, and no positive delta from `+0.05 mm` through `+1.0 mm` has start plus terminal feasibility |
| Positive base-z start-contact audit | `scripts/audit_positive_base_z_start_contact.py`, `reports/positive_base_z_start_contact_report.md`, `runs/positive_base_z_start_contact/20260524T170350/metrics.yaml` | v68 uses deterministic and random start-contact seed sweeps for eight positive deltas; start contact passes `8 / 8` through `+1.0 mm`, terminal passes `0 / 8`, and every positive terminal row still fails orientation |
| Positive terminal orientation audit | `scripts/audit_positive_terminal_orientation.py`, `reports/positive_terminal_orientation_report.md`, `runs/positive_terminal_orientation/20260524T171705/metrics.yaml` | v69 compares the current contact-point model with the legacy sphere-center model; in the current model force/x-y/contact passes `8 / 8` positive terminal cases but diagnostic orientation passes `0 / 8`, full-rotation and force-normal-only errors are numerically identical, and all positive force/x-y/contact cases require about `0.1195 rad` orientation margin |
| Positive relaxed-orientation recovery audit | `scripts/audit_positive_relaxed_orientation_recovery.py`, `reports/positive_relaxed_orientation_recovery_report.md`, `runs/positive_relaxed_orientation_recovery/20260524T172909/metrics.yaml` | v70 uses a run-local `0.12 rad` diagnostic orientation envelope; positive start, terminal, and path geometry pass `8 / 8` through `+1.0 mm`, but stitched recovery is `0` because Stage B handoff is `3 / 4` with E2 qdot saturation |
| Positive Stage B E2 margin audit | `scripts/audit_positive_stage_b_e2_margin.py`, `reports/positive_stage_b_e2_margin_report.md`, `runs/positive_stage_b_e2_margin/20260524T192129/metrics.yaml` | v71 reuses the v70 relaxed terminal/path setup and shows E2 passes `0 / 8` positive deltas at `paper_time_scale = 0.01`, `7 / 8` at `0.0075`, and `8 / 8` at `0.005`; qdot-limit-only relaxation on `+1.0 mm` at original timing still fails because orientation remains just above `0.12 rad` |
| Positive full stitched recovery audit | `scripts/audit_positive_full_stitched_recovery.py`, `reports/positive_full_stitched_recovery_report.md`, `runs/positive_full_stitched_recovery/20260524T192854/metrics.yaml` | v72 combines the v70 relaxed terminal/path setup with `paper_time_scale = 0.005`; the full positive E1-E4 stitched matrix passes `8 / 8` through `+1.0 mm`, with Stage B handoff `4 / 4` for every row |
| Positive stitched sensitivity audit | `scripts/audit_positive_stitched_sensitivity.py`, `reports/positive_stitched_sensitivity_report.md`, `runs/positive_stitched_sensitivity/20260524T193845/metrics.yaml` | v73 stress-tests the v72 recovered policy across five scenarios and eight positive deltas; the compact matrix passes `37 / 40`, with failures at `qdot012_stage_a18s` `+0.2 mm`, `paper_time_scale_0p0075` `+1.0 mm`, and `orientation_gate_0p119` `+1.0 mm` |
| Qdot012 Stage A margin audit | `scripts/audit_qdot012_stage_a_margin.py`, `reports/qdot012_stage_a_margin_report.md`, `runs/qdot012_stage_a_margin/20260524T194817/metrics.yaml` | v74 isolates the v73 qdot012 `+0.2 mm` failure; Stage B passes `4 / 4` throughout, Stage A fails through `18.03 s`, and stitched recovery starts at `18.035 s` |
| Qdot012 positive stitched matrix | `scripts/audit_positive_full_stitched_recovery.py --stage-a-duration-s 18.035 --qdot-limit-rad-s 0.12 --paper-time-scale 0.005 --max-orientation-error-rad 0.12`, `reports/qdot012_positive_stitched_matrix_report.md`, `runs/positive_full_stitched_recovery/20260524T195501/metrics.yaml` | v75 folds the v74 duration margin into all positive deltas; stitched recovery passes `8 / 8` through `+1.0 mm`, with Stage B `4 / 4` for every row |
| Positive timing boundary audit | `scripts/audit_positive_timing_boundary.py`, `reports/positive_timing_boundary_report.md`, `runs/positive_timing_boundary/20260524T200236/metrics.yaml` | v76 isolates the v73 `paper_time_scale_0p0075` `+1.0 mm` failure; Stage A passes all timing cases, `paper_time_scale = 0.0052` still passes, and `0.0054` first fails on E2 orientation just above the `0.12 rad` diagnostic gate |
| Positive orientation-gate boundary audit | `scripts/audit_positive_orientation_gate_boundary.py`, `reports/positive_orientation_gate_boundary_report.md`, `runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml` | v77 isolates the v73 `orientation_gate_0p119` `+1.0 mm` failure; Stage A passes once the gate reaches `0.1195 rad`, while full stitched recovery first passes at `0.11998 rad` because E2 reaches `0.1199788204275829 rad` |
| Stage B orientation-kp probe | `scripts/audit_stage_b_orientation_kp_probe.py`, `reports/stage_b_orientation_kp_probe_report.md`, `runs/stage_b_orientation_kp_probe/20260524T222953/metrics.yaml` | v78 tests existing Stage B `orientation_kp` feedback on the localized E2 `+1.0 mm` tightened-orientation row; Stage A passes all `30 / 30` cells, but stitched recovery passes `0 / 30` because low gains miss orientation while higher gains fail qdot saturation and/or tail qdot utilization |
| Stage B priority recovery | `scripts/evaluate_stitched_stage_a_handoff.py`, `scripts/audit_stage_b_priority_recovery.py`, `reports/stage_b_priority_recovery_report.md`, `runs/stage_b_priority_recovery/20260524T224404/metrics.yaml` | v79 recovers the localized `+1.0 mm`, `0.11995 rad` tightened-gate E1-E4 row with planar-primary Stage B priority and normal-axis weight `30`; passing scenarios are `planar_normal30_kp0p001` and `planar_normal30_kp0p002`, each with Stage B `4 / 4` |
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

The Stage A contact path and tracking line can additionally claim:

```text
ur10e_stage_a_contact_path_and_tracking:
  offline contact path pass = true
  tracking gate pass = true
  Stage A duration = 15.0 s
  Stage A max qdot = 0.14332635022814824 rad/s
  qdot saturation fraction = 0.0
  connected Stage B trajectory = false until v63
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stage_a_contact_path_audit_report.md`
- `runs/stage_a_contact_path_audit/20260524T151201/metrics.yaml`
- `reports/stage_a_contact_path_tracking_report.md`
- `runs/stage_a_contact_path_tracking/20260524T152346/metrics.yaml`

The stitched diagnostic Stage A plus handoff can additionally claim:

```text
ur10e_stitched_diagnostic_stage_a_handoff:
  selected target label = ur10e_adapted_terminal_setup_diagnostic
  stitched gate pass = true
  Stage A gate pass = true
  Stage B handoff pass count = 4 / 4
  Stage A max qdot = 0.14332635022814824 rad/s
  qdot saturation fraction = 0.0
  robustness to perturbations = false until v64 sensitivity is considered
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stitched_stage_a_handoff_report.md`
- `runs/stitched_stage_a_handoff_eval/20260524T152807/metrics.yaml`

The stitched sensitivity audit can additionally claim:

```text
ur10e_stitched_diagnostic_sensitivity:
  case count = 9
  stitched pass count = 4 / 9
  passing cases = nominal, stage_a_16s, force_gain_5e-5, force_gain_2e-4
  failing cases = base_z_minus_1mm, base_z_plus_1mm, stage_a_14s, qdot_limit_0p12, paper_time_scale_0p02
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stitched_stage_a_handoff_sensitivity_report.md`
- `runs/stitched_stage_a_handoff_sensitivity/20260524T161111/metrics.yaml`

The stitched timing-margin audit can additionally claim:

```text
ur10e_stitched_diagnostic_timing_margin:
  case count = 7
  stitched pass count = 4 / 7
  passing cases = nominal, stage_a_14p5_recovery, qdot012_stage_a_18p0_recovery, paper_time_scale_0p012_recovery
  failing cases = stage_a_14s_reference_fail, qdot012_stage_a_17p5_reference_fail, paper_time_scale_0p0125_reference_fail
  base-z/contact perturbation recovery = false
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stitched_stage_a_handoff_timing_margin_report.md`
- `runs/stitched_stage_a_handoff_timing_margin/20260524T162005/metrics.yaml`

The Stage A base-z recovery audit can additionally claim:

```text
ur10e_stage_a_base_z_recovery:
  case count = 3
  recovered cases = base_z_minus_1mm_stage_a_16s_recovery
  unresolved cases = base_z_minus_1mm, base_z_plus_1mm
  exact 15.0 s -1 mm recovery = false
  +1 mm recovery = false
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stage_a_base_z_recovery_report.md`
- `runs/stage_a_base_z_recovery/20260524T163746/metrics.yaml`

The Stage A base-z bracket audit can additionally claim:

```text
ur10e_stage_a_base_z_bracket:
  case count = 13
  start pass count = 5 / 13
  terminal pass count = 5 / 13
  path geometry pass count = 4 / 13
  recovered durations = delta_m1p000mm@16.0, delta_m0p500mm@15.0,
    delta_m0p500mm@16.0, delta_m0p250mm@15.0,
    delta_m0p250mm@16.0, delta_p0p000mm@15.0,
    delta_p0p000mm@16.0
  max positive terminal-pass delta = none
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stage_a_base_z_bracket_report.md`
- `runs/stage_a_base_z_bracket/20260524T165411/metrics.yaml`

The positive base-z start-contact audit can additionally claim:

```text
ur10e_positive_base_z_start_contact:
  case count = 8
  start pass count = 8 / 8
  terminal pass count = 0 / 8
  max start-pass delta = +1.0 mm
  max terminal-pass delta = none
  terminal orientation failures = 8 / 8
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_base_z_start_contact_report.md`
- `runs/positive_base_z_start_contact/20260524T170350/metrics.yaml`

The positive terminal orientation audit can additionally claim:

```text
ur10e_positive_terminal_orientation:
  current contact-point model case count = 8
  current contact-point force/x-y/contact pass count = 8 / 8
  current contact-point diagnostic orientation pass count = 0 / 8
  current contact-point max positive diagnostic-pass delta = none
  full-rotation versus force-normal-only yaw gap <= 4.884981308350689e-15 rad
  orientation threshold needed for all current force/x-y/contact cases = 0.11948560786548146 rad
  legacy sphere-center comparison diagnostic pass count = 6 / 8 through +0.5 mm
  legacy sphere-center model is a known flawed comparison = true
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_terminal_orientation_report.md`
- `runs/positive_terminal_orientation/20260524T171705/metrics.yaml`

The positive relaxed-orientation recovery audit can additionally claim:

```text
ur10e_positive_relaxed_orientation_recovery:
  relaxed terminal orientation envelope = 0.12 rad
  run-local relaxed config only = true
  start pass count = 8 / 8
  terminal pass count = 8 / 8
  path geometry pass count = 8 / 8
  stitched recovery count = 0
  max positive terminal/path delta = +1.0 mm
  Stage B handoff count for tested rows = 3 / 4
  consistent failing trajectory = e2-figure-eight
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_relaxed_orientation_recovery_report.md`
- `runs/positive_relaxed_orientation_recovery/20260524T172909/metrics.yaml`

The positive Stage B E2 margin audit can additionally claim:

```text
ur10e_positive_stage_b_e2_margin:
  source setup = v70 run-local relaxed terminal/path setup
  stage_b trajectory = e2-figure-eight
  E2 pass count at paper_time_scale 0.01 = 0 / 8
  E2 pass count at paper_time_scale 0.0075 = 7 / 8
  E2 pass count at paper_time_scale 0.005 = 8 / 8
  fastest all-positive E2 pass scale tested = 0.005
  qdot-limit-only recovery at +1.0 mm and original 0.01 timing = false
  full E1-E4 stitched recovery claim = false
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_stage_b_e2_margin_report.md`
- `runs/positive_stage_b_e2_margin/20260524T192129/metrics.yaml`

The positive full stitched recovery audit can additionally claim:

```text
ur10e_positive_full_stitched_recovery:
  source setup = v70 run-local relaxed terminal/path setup
  stage_b paper_time_scale = 0.005
  positive stitched pass count = 8 / 8
  max positive stitched-pass delta = +1.0 mm
  Stage B handoff count for every row = 4 / 4
  max Stage B qdot saturation fraction = 0.006
  max Stage B orientation error = 0.1199788204275829 rad
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_full_stitched_recovery_report.md`
- `runs/positive_full_stitched_recovery/20260524T192854/metrics.yaml`

The positive stitched sensitivity audit can additionally claim:

```text
ur10e_positive_stitched_sensitivity:
  source setup = v70 run-local relaxed terminal/path setup
  nominal recovered policy = v72
  scenario count = 5
  matrix stitched pass count = 37 / 40
  all-pass scenarios = nominal_v72, stage_a_14p5s
  failing scenarios = qdot012_stage_a18s, paper_time_scale_0p0075, orientation_gate_0p119
  qdot012_stage_a18s failure = +0.2 mm Stage A final_tracking_error_norm_rad
  paper_time_scale_0p0075 failure = +1.0 mm E2 qdot/orientation
  orientation_gate_0p119 failure = +1.0 mm Stage A terminal and Stage B orientation
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_stitched_sensitivity_report.md`
- `runs/positive_stitched_sensitivity/20260524T193845/metrics.yaml`

The qdot012 Stage A margin audit can additionally claim:

```text
ur10e_qdot012_stage_a_margin:
  source setup = v70 run-local relaxed terminal/path setup
  inherited failing cell = v73 qdot012_stage_a18s +0.2 mm
  qdot limit = 0.12 rad/s
  paper_time_scale = 0.005
  Stage B pass count at every duration = 4 / 4
  last failing Stage A duration = 18.03 s
  first passing Stage A duration = 18.035 s
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/qdot012_stage_a_margin_report.md`
- `runs/qdot012_stage_a_margin/20260524T194817/metrics.yaml`

The qdot012 positive stitched matrix can additionally claim:

```text
ur10e_qdot012_positive_stitched_matrix:
  source setup = v70 run-local relaxed terminal/path setup
  qdot limit = 0.12 rad/s
  Stage A duration = 18.035 s
  paper_time_scale = 0.005
  positive stitched pass count = 8 / 8
  max positive stitched-pass delta = +1.0 mm
  Stage B handoff count for every row = 4 / 4
  max Stage B qdot saturation fraction = 0.001
  max Stage B orientation error = 0.11997895388586574 rad
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/qdot012_positive_stitched_matrix_report.md`
- `runs/positive_full_stitched_recovery/20260524T195501/metrics.yaml`

The positive timing-boundary audit can additionally claim:

```text
ur10e_positive_timing_boundary:
  source setup = v70 run-local relaxed terminal/path setup
  inherited failing cell = v73 paper_time_scale_0p0075 +1.0 mm
  Stage A duration = 15.0 s
  qdot limit = 0.15 rad/s
  diagnostic orientation gate = 0.12 rad
  timing sweep case count = 9
  stitched pass count = 2 / 9
  max passing paper_time_scale = 0.0052
  first failing paper_time_scale = 0.0054
  first failing criterion = E2 max_orientation_error_rad
  Stage A passed every timing case = true
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_timing_boundary_report.md`
- `runs/positive_timing_boundary/20260524T200236/metrics.yaml`

The positive orientation-gate boundary audit can additionally claim:

```text
ur10e_positive_orientation_gate_boundary:
  source setup = v70 run-local relaxed terminal/path setup
  inherited failing cell = v73 orientation_gate_0p119 +1.0 mm
  Stage A duration = 15.0 s
  paper_time_scale = 0.005
  qdot limit = 0.15 rad/s
  orientation gate sweep case count = 9
  stitched pass count = 2 / 9
  max failing orientation gate = 0.11997 rad
  first passing orientation gate = 0.11998 rad
  Stage A first passes at orientation gate = 0.1195 rad
  max Stage B orientation error = 0.1199788204275829 rad
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/positive_orientation_gate_boundary_report.md`
- `runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml`

The Stage B orientation-kp probe can additionally claim:

```text
ur10e_stage_b_orientation_kp_probe:
  source setup = v70 run-local relaxed terminal/path setup
  inherited boundary = v77 tightened-orientation +1.0 mm E2 row
  Stage A duration = 15.0 s
  paper_time_scale = 0.005
  orientation gate = 0.11995 rad
  qdot limits tested = [0.15, 0.16, 0.18, 0.2, 0.25] rad/s
  orientation_kp values tested = [0, 0.001, 0.002, 0.003, 0.005, 0.01]
  E2 probe case count = 30
  stitched pass count = 0 / 30
  Stage A pass count = 30 / 30
  orientation-ok count = 13 / 30
  min E2 orientation error = 0.11990689588867036 rad
  best qdot-preserving row still fails orientation = true
  orientation-correcting rows fail qdot gates = true
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stage_b_orientation_kp_probe_report.md`
- `runs/stage_b_orientation_kp_probe/20260524T222953/metrics.yaml`

The Stage B priority recovery audit can additionally claim:

```text
ur10e_stage_b_priority_recovery:
  source setup = v70 run-local relaxed terminal/path setup
  inherited boundary = v77/v78 tightened-orientation +1.0 mm row
  Stage A duration = 15.0 s
  paper_time_scale = 0.005
  qdot limit = 0.15 rad/s
  orientation gate = 0.11995 rad
  scenario count = 7
  stitched pass count = 2 / 7
  passing scenarios = [planar_normal30_kp0p001, planar_normal30_kp0p002]
  Stage A passed every scenario = true
  recovered E1-E4 Stage B count in passing scenarios = 4 / 4
  linear-primary controls still fail = true
  robustness claim = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

Evidence:

- `reports/stage_b_priority_recovery_report.md`
- `runs/stage_b_priority_recovery/20260524T224404/metrics.yaml`

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
- The v62 contact path tracking audit follows the v61 path with a qdot-limited
  joint-path replay and passes the tracking gate, but it does not connect that
  tracked Stage A path to the v60 Stage B handoff and is not a force-feedback
  recovery or hardware-readiness claim.
- The v63 stitched audit connects the v62 Stage A tracker to the v60 slowed
  handoff in one script and passes the diagnostic stitched gate, but it remains
  nominal diagnostic-label simulation evidence. It does not prove strict
  paper-equivalent feasibility, robustness to perturbations, or hardware
  readiness.
- The v64 sensitivity audit passes only `4 / 9` stitched cases. It shows the
  nominal v63 policy is fragile to 1 mm base-z/contact perturbations, tighter
  qdot budget, shorter Stage A timing, and faster Stage B timing. It therefore
  bounds the nominal claim but does not establish robustness.
- The v65 timing-margin audit recovers the qdot/timing side under explicit
  margins, but it does not recover the 1 mm base-z/contact perturbation
  failures and therefore still does not establish robustness.
- The v66 base-z recovery audit recovers only the `-1 mm` side with a
  rebalanced start, reoptimized path, and `16.0 s` Stage A duration. The exact
  `15.0 s` `base_z_minus_1mm` reference remains qdot-limited, and
  `base_z_plus_1mm` still lacks a passing start plus terminal target pair under
  this diagnostic search. It therefore still does not establish robustness.
- The v67 base-z bracket audit shows no tested positive delta from `+0.05 mm`
  through `+1.0 mm` has a passing start plus terminal pair under that compact
  local search, so the positive side is not a timing-only problem. It also
  shows a `-0.75 mm` path anomaly. It therefore still does not establish
  robustness.
- The v68 positive base-z start-contact audit corrects the v67 start-contact
  interpretation: with broader deterministic and random seeds, positive-side
  start contact passes through `+1.0 mm`. Terminal orientation still fails all
  `8 / 8` positive deltas, so this does not prove terminal recovery, path
  recovery, robustness, contact-model calibration, or hardware readiness.
- The v69 positive terminal orientation audit shows the current contact-point
  model has force/x-y/contact terminal feasibility for all `8 / 8` positive
  deltas, but the `0.08 rad` diagnostic orientation gate passes `0 / 8`.
  Full-rotation and force-normal-only errors are numerically identical, so yaw
  is not the limiter. The current model needs about `0.1195 rad` orientation
  margin to cover all positive force/x-y/contact terminal cases. This still
  does not prove path recovery, robustness, contact-model calibration, or
  hardware readiness.
- The v70 positive relaxed-orientation recovery audit shows a run-local
  `0.12 rad` diagnostic orientation envelope recovers positive-side start,
  terminal, and path geometry through `+1.0 mm`, but it still does not recover
  stitched Stage A plus Stage B. All tested stitched rows have Stage B handoff
  `3 / 4`, with E2 failing on qdot saturation. This does not prove robustness,
  strict paper-equivalent feasibility, or hardware readiness.
- The v71 positive Stage B E2 margin audit shows E2 recovers for all positive
  deltas at `paper_time_scale = 0.005`, but it does not yet prove the full
  E1-E4 stitched positive matrix at that timing. The qdot-limit-only probe at
  original `0.01` timing also does not recover the hardest `+1.0 mm` row
  because orientation remains just above `0.12 rad`.
- The v72 positive full stitched recovery audit closes that specific full
  positive E1-E4 stitched gap under the relaxed diagnostic label, but it still
  does not prove robustness, strict paper-equivalent feasibility, contact-model
  calibration, or hardware readiness. It depends on the run-local `0.12 rad`
  orientation gate and slowed `paper_time_scale = 0.005`.
- The v73 positive stitched sensitivity audit stress-tests the v72 recovered
  policy and passes `37 / 40` compact matrix cells. It preserves all eight
  positive passes for nominal v72 and `stage_a_14p5s`, but fails
  `qdot012_stage_a18s` at `+0.2 mm`, `paper_time_scale_0p0075` at `+1.0 mm`,
  and `orientation_gate_0p119` at `+1.0 mm`. This bounds the v72 recovery and
  still prevents a robustness claim.
- The v74 qdot012 Stage A margin audit shows the v73 qdot012 `+0.2 mm` failure
  is a narrow Stage A duration margin: `18.03 s` still fails on final tracking,
  while `18.035 s` passes and Stage B remains `4 / 4` for every tested
  duration. This does not recover the faster-timing or tighter-orientation
  `+1.0 mm` sensitivity limits.
- The v75 qdot012 positive stitched matrix folds the `18.035 s` Stage A
  duration into all positive deltas with `qdot_limit_rad_s = 0.12`. It recovers
  `8 / 8` stitched rows through `+1.0 mm`, with Stage B `4 / 4` for every row.
  This closes the qdot012 branch of the v73 compact sensitivity failure but
  still leaves faster-timing and tighter-orientation `+1.0 mm` limits.
- The v76 positive timing-boundary audit isolates the faster-timing
  `+1.0 mm` limit. Stage A passes all nine timing cases; the row still passes
  at `paper_time_scale = 0.0052` and first fails at `0.0054` on E2 orientation
  just above `0.12 rad`. Qdot saturation becomes severe only at `0.007` and
  above. This bounds the v73 `paper_time_scale_0p0075` failure but does not
  recover it under the same diagnostic gate, and it leaves the separate
  `orientation_gate_0p119` `+1.0 mm` limit unresolved.
- The v77 positive orientation-gate boundary audit isolates the remaining
  tightened-orientation `+1.0 mm` limit. Stage A terminal orientation first
  passes once the gate reaches `0.1195 rad`, but full stitched recovery first
  passes at `0.11998 rad` because E2 reaches
  `0.1199788204275829 rad` under v72 timing. This localizes the gate margin,
  but it is still not a robustness proof or hardware-ready control claim.
- The v78 Stage B orientation-kp probe tests the existing
  `orientation_kp` feedback hook as a direct fix for that v77 boundary. Stage A
  passes all `30 / 30` E2 probe cells at a `0.11995 rad` gate, but stitched
  recovery passes `0 / 30`. Low gains preserve qdot while still failing
  orientation; gains that satisfy orientation fail qdot saturation and/or tail
  qdot utilization, including with qdot limits up to `0.25 rad/s`. This
  rules out a simple single-gain Stage B orientation-feedback recovery under
  the current formulation, but it is still not a robustness proof or
  hardware-ready control claim.
- The v79 Stage B priority recovery audit recovers the localized `+1.0 mm`,
  `0.11995 rad` tightened-gate E1-E4 diagnostic row with planar-primary Stage B
  priority and normal-axis weight `30`. The two passing scenarios,
  `planar_normal30_kp0p001` and `planar_normal30_kp0p002`, each report Stage A
  pass and Stage B handoff `4 / 4`. Linear-primary controls still fail, and
  neighboring planar-primary controls show the tradeoff: low normal weighting
  gives up E2 force tracking, while high normal weighting moves back toward the
  E2 orientation/qdot boundary. This is a localized diagnostic recovery, not a
  full positive-delta matrix, robustness proof, or hardware-ready control
  claim.
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

Run the recovered planar-primary formulation across the full positive-delta
matrix, or stress it against faster timing/tighter gates, before claiming
anything stronger than localized diagnostic recovery. Keep strict
paper-equivalent setup, v38 trajectory-after-relaxed-setup, and v63-v79
diagnostic staged labels separate.
Any hardware work still requires measured mounted-stack geometry and a separate
approved SOP.
