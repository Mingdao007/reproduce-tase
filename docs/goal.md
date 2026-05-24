# Goal: TASE Finite-Time UR10e Reproduction

Use this file as the long-form goal instructions for the next Codex thread.
The short thread goal should reference this file instead of pasting the full
instructions into the goal text.

## Short Thread Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in `/home/andy/reproduce-tase`. First read `docs/goal.md`, `reports/completion_audit.md`, `reports/ITERATION_LOG.md`, and `reports/DECISION_RECORD.md`; then inspect git status before changing anything. Preserve the current v71 claim boundary: the formula-faithful Python paper-platform line passes formula-convergence evidence; the separate tuned Python figure-match line reproduces the legacy Fig.6 q7 landmark; full paper-equivalent parity is still not achieved. The v57 UR10e diagnostic terminal setup gate passes `1 / 513` terminal candidates, v58 selects that target, v59 shows default direct handoff fails `0 / 4` on qdot saturation, v60 shows a slowed low-gain diagnostic handoff from the selected target passes `4 / 4`, v61 finds an offline 128-knot quasi-static contact path to that target, v62 tracks that path over `15.0 s`, v63 stitches the v62 Stage A tracker to the v60 slowed handoff with a `4 / 4` Stage B pass count, v64 sensitivity passes only `4 / 9` cases, v65 recovers the qdot/timing failure side with explicit margins, v66 recovers only the `-1 mm` base-z side when Stage A is extended to `16.0 s`, v67 brackets the base-z sensitivity, v68 shows positive base-z start contact is recoverable through `+1.0 mm`, v69 shows yaw is not the positive terminal limiter and the current model needs about `0.1195 rad` orientation margin, v70 shows a run-local `0.12 rad` diagnostic orientation envelope recovers positive start, terminal, and path feasibility through `+1.0 mm` but stitched recovery is still `0` because Stage B handoff remains `3 / 4` with E2 qdot saturation, and v71 shows E2 timing recovers at `paper_time_scale = 0.005` for all positive deltas while qdot-limit-only relaxation at `+1.0 mm` does not recover original `0.01` timing because orientation stays just above `0.12 rad`. This is diagnostic-label simulation evidence: it is not strict paper-equivalent, not robust to contact/model perturbations, and not hardware-ready. The next branch should run the full positive E1-E4 stitched matrix with the v70 relaxed terminal/path setup and `paper_time_scale = 0.005`. Keep strict paper-equivalent setup, v38 relaxed trajectory-after-setup, and v63-v71 diagnostic staged labels separate. Do not move or configure the real UR10e; real hardware work is read-only unless a separate approved SOP exists.
```

## Objective

Continue the UR10e + OnRobot force/torque sensor project from the current
`v71` repository state. The project goal is to reproduce the T-ASE finite-time
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
  `exp/tase-ur10e-v71-stage-b-e2-margin`
- Current v71 formal run:
  `runs/positive_stage_b_e2_margin/20260524T192129`
- Paper PDF:
  `/home/andy/Zotero/storage/UZRF97KG/Xu 等 - 2026 - Finite-Time Convergence Neural Network-Based Force-Motion Control for Unknown Surface With Orientati.pdf`
- Legacy source workspace that has been migrated/audited into the repo:
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/`
- Required repository entry points:
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

The v49-v50 provenance audits found that the legacy Fig.6 q7 landmark belongs
to a tuned `admittance_proxy` figure-match line with explicit q7 nullspace
bias, not the formula-faithful controller path. v52 implements that tuned line
in Python and matches the legacy figure-match raw trajectory to numerical
precision. Future work must still keep these claim levels separate.

Current next executable step:

- Continue UR10e adapted work by running the full positive E1-E4 stitched
  matrix with the v70 relaxed terminal/path setup and
  `paper_time_scale = 0.005`. Keep strict paper-equivalent setup, v38
  trajectory-after-relaxed-setup, and v63-v71 diagnostic staged labels
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
