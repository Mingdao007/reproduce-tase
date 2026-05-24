# Completion Audit

Date: 2026-05-24

Branch: `exp/tase-ur10e-v41-paper-7dof-line`

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
- `plans/HARDWARE_GATE_SOP.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Prompt-To-Artifact Checklist

| Requirement | Evidence | Status |
|---|---|---|
| Use `Mingdao007/reproduce-tase` as target repo | `origin` is `git@github.com:Mingdao007/reproduce-tase.git`; decisions D001-D003; v37-v40 branches pushed and GitHub-verified; v41 is the current iteration branch | Done |
| Keep work Git-backed with dedicated branches | Iteration branches through `exp/tase-ur10e-v41-paper-7dof-line`; latest local branch is `exp/tase-ur10e-v41-paper-7dof-line` | Done |
| Maintain mandatory plans | All required `plans/*.md` files exist: master, paper truth, math transfer, MuJoCo, controller, experiment matrix, hardware gate, rollback | Done |
| Maintain iteration log and decision record | `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`; decisions through D046 as of v41 | Done |
| Migrate reproduction code/configs/reports/lightweight metadata | Repo contains `src/tase_repro`, `scripts`, `configs`, `reports`, `runs/*` summaries, and `runs/RUN_ARTIFACTS_MANIFEST.md` | Done |
| Keep raw/heavy artifacts out of ordinary Git or manifest them | `.npz` raw arrays remain ignored; manifest documents tracked summaries and omitted raw artifacts | Done |
| Extract paper truth from PDF | `reports/paper_truth_extraction.md`, `reports/orientation_signal_ambiguity_audit.md`, `reports/section_v_z0_audit.md`, `configs/paper_truth.yaml` | Done for extraction fields; Section V orientation and `z0` remain paper ambiguities |
| Derive paper 7DOF method to UR10e 6DOF | `reports/math_derivation_ur10e_transfer.md` includes force-motion decomposition, orientation, slack/priority, and v38 implication | Done for current adapted line |
| Verify MuJoCo baseline | Smoke, force ladder, force-feedback, trajectory, tilted-plane, and staged reports in `reports/*`; run manifest lists artifacts | Done for approximate simulation baseline |
| Implement tests before trusting plots | `scripts/run_tests.sh` used throughout; latest v41 validation was `74 passed in 1.44s` | Done for current code |
| Run staged simulations | v29-v38 staged runs and reports; v33 slowed E1-E4 matrix; v35-v37 setup probes | Done |
| Separate UR10e adapted results from paper-platform reproduction | README claim boundary plus D043; relaxed label explicitly says not paper-equivalent | Done |
| Paper-platform 7DOF executable line | `src/tase_repro/panda_kinematics.py`, `src/tase_repro/paper_7dof.py`, `scripts/run_paper_7dof_section_v.py`, v41 run `20260524T113608` | Diagnostic line exists; not paper-faithful parity |
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

## Missing Or Weakly Verified Requirements

- Strict paper-equivalent full staged feasibility is not achieved.
- Paper-platform 7DOF Franka/Panda reproduction now has a separate executable
  diagnostic line, but it is not paper-faithful parity: v41 tail contact
  fraction is `0.0` and tail force error is `5.0 N`.
- Section V `z0` is now verified undefined in the simulation text; future code
  still needs an explicit adapted convention if it implements Section V.
- UR10e MJCF, 85 mm TCP guess, payload, CoG, and contact geometry remain
  approximate or unverified for hardware use.
- OnRobot/RTDE force-source reconciliation remains unresolved.
- Hardware gate report is not produced, and no real robot motion is authorized.
- The relaxed setup budget is an explicit adapted-simulation label, not a
  mathematical solution to the strict Stage A setup gate.
- The v41 paper-platform line inherits unverified Panda DH parameters and a
  documented force-normal orientation interpretation.

## Audit Conclusion

The overall goal is not complete. The repository is now in a strong
simulation-audit state for a UR10e adapted result, but it has not achieved
strict paper-equivalent full staged feasibility or hardware readiness.

Do not mark the active goal complete from the current evidence.

## Next Executable Step

Choose one of these before any real hardware work:

- debug the paper-platform 7DOF normal-force/contact loop until tail contact
  and force error pass without hard-bound violations; or
- validate or replace the approximate UR10e TCP/contact model and rerun the
  terminal setup audit.
