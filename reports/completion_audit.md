# Completion Audit

Date: 2026-05-24

Branch: `exp/tase-ur10e-v45-paper-7dof-30s-candidate`

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
- `reports/paper_platform_parity_gate_report.md`
- `runs/paper_platform_parity_eval/20260524T120503/metrics.yaml`
- `plans/HARDWARE_GATE_SOP.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Prompt-To-Artifact Checklist

| Requirement | Evidence | Status |
|---|---|---|
| Use `Mingdao007/reproduce-tase` as target repo | `origin` is `git@github.com:Mingdao007/reproduce-tase.git`; decisions D001-D003; v37-v44 branches pushed and GitHub-verified; v45 is the current iteration branch | Done |
| Keep work Git-backed with dedicated branches | Iteration branches through `exp/tase-ur10e-v45-paper-7dof-30s-candidate`; latest local branch is `exp/tase-ur10e-v45-paper-7dof-30s-candidate` | Done |
| Maintain mandatory plans | All required `plans/*.md` files exist: master, paper truth, math transfer, MuJoCo, controller, experiment matrix, hardware gate, rollback | Done |
| Maintain iteration log and decision record | `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`; decisions through D050 as of v45 | Done |
| Migrate reproduction code/configs/reports/lightweight metadata | Repo contains `src/tase_repro`, `scripts`, `configs`, `reports`, `runs/*` summaries, and `runs/RUN_ARTIFACTS_MANIFEST.md` | Done |
| Keep raw/heavy artifacts out of ordinary Git or manifest them | `.npz` raw arrays remain ignored; manifest documents tracked summaries and omitted raw artifacts | Done |
| Extract paper truth from PDF | `reports/paper_truth_extraction.md`, `reports/orientation_signal_ambiguity_audit.md`, `reports/section_v_z0_audit.md`, `configs/paper_truth.yaml` | Done for extraction fields; Section V orientation and `z0` remain paper ambiguities |
| Derive paper 7DOF method to UR10e 6DOF | `reports/math_derivation_ur10e_transfer.md` includes force-motion decomposition, orientation, slack/priority, and v38 implication | Done for current adapted line |
| Verify MuJoCo baseline | Smoke, force ladder, force-feedback, trajectory, tilted-plane, and staged reports in `reports/*`; run manifest lists artifacts | Done for approximate simulation baseline |
| Implement tests before trusting plots | `scripts/run_tests.sh` used throughout; latest v45 full-suite validation was `80 passed in 2.11s`; `git diff --check` passed | Done for current code |
| Run staged simulations | v29-v38 staged runs and reports; v33 slowed E1-E4 matrix; v35-v37 setup probes | Done |
| Separate UR10e adapted results from paper-platform reproduction | README claim boundary plus D043; relaxed label explicitly says not paper-equivalent | Done |
| Paper-platform 7DOF executable line | `src/tase_repro/panda_kinematics.py`, `src/tase_repro/paper_7dof.py`, `scripts/run_paper_7dof_section_v.py`, v41 KKT run `20260524T113608`, v42 pinv run `20260524T114244`, v43 capped-integral KKT run `20260524T114736` | Diagnostic line exists and capped-integral KKT contact passes; not paper-equivalent parity |
| Paper-platform parity gate | `configs/paper_platform_parity.yaml`, `src/tase_repro/paper_platform_parity.py`, `scripts/evaluate_paper_platform_parity.py`, `runs/paper_platform_parity_eval/20260524T120503/metrics.yaml` | Gate exists; v45 30 s candidate has duration and tail convergence agreement with formula-faithful reference but strict parity fails |
| Strict full staged feasibility | v33 strict full staged `0 / 4`; v35 setup gate `0 / 10`; v36 setup gate `0 / 10`; v37 terminal IK `0 / 65` | Not achieved |
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

The strict parity gate can additionally claim:

```text
paper_platform_7dof_strict_parity:
  parity pass = false
  tail convergence against formula-faithful legacy reference = pass
  duration coverage = true
  Fig.6 q7-at-22 s landmark = false
  Python Fig.5 r-sweep coverage = false
  force-integral assumption compatibility = false
```

Evidence:

- `reports/paper_platform_parity_gate_report.md`
- `runs/paper_platform_parity_eval/20260524T120503/metrics.yaml`

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

## Missing Or Weakly Verified Requirements

- Strict paper-equivalent full staged feasibility is not achieved.
- Paper-platform 7DOF Franka/Panda reproduction now has a separate executable
  diagnostic line, a capped-integral KKT variant that passes tail force, and a
  strict parity gate. The gate fails, so this is still not paper-equivalent
  numerical parity. v45 closes the duration-coverage gap but exposes a q7
  landmark mismatch.
- Section V `z0` is now verified undefined in the simulation text; future code
  still needs an explicit adapted convention if it implements Section V.
- UR10e MJCF, 85 mm TCP guess, payload, CoG, and contact geometry remain
  approximate or unverified for hardware use.
- OnRobot/RTDE force-source reconciliation remains unresolved.
- Hardware gate report is not produced, and no real robot motion is authorized.
- The relaxed setup budget is an explicit adapted-simulation label, not a
  mathematical solution to the strict Stage A setup gate.
- The v43-v45 paper-platform line inherits unverified Panda DH parameters,
  uses a documented force-normal orientation interpretation, and passes
  force/contact only with an explicit capped-integral anti-windup assumption.
  It still lacks Fig.5 r-sweep parity evidence and has a measured q7-at-22 s
  mismatch against the figure-match legacy reference.

## Audit Conclusion

The overall goal is not complete. The repository is now in a strong
simulation-audit state for a UR10e adapted result, but it has not achieved
strict paper-equivalent full staged feasibility or hardware readiness.

Do not mark the active goal complete from the current evidence.

## Next Executable Step

Choose one of these before any real hardware work:

- investigate the v45 q7-at-22 s mismatch, add Python Fig.5 r-sweep outputs,
  then address the capped-integral assumption or verify Panda/Franka DH model
  provenance; or
- validate or replace the approximate UR10e TCP/contact model and rerun the
  terminal setup audit.
