# Goal: TASE Finite-Time UR10e Reproduction

Use this file as the long-form goal instructions for the next Codex thread.
The short thread goal should reference this file instead of pasting the full
instructions into the goal text.

## Short Thread Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in `/home/andy/reproduce-tase`. First read `docs/goal.md`, `reports/completion_audit.md`, `reports/ITERATION_LOG.md`, and `reports/DECISION_RECORD.md`; then inspect git status before changing anything. Preserve the current v54 claim boundary: the formula-faithful Python paper-platform line passes formula-convergence evidence; the separate tuned Python figure-match line reproduces the legacy Fig.6 q7 landmark; full paper-equivalent parity is still not achieved. The v54 UR10e TCP contact-point model separates the 85 mm site from the colliding sphere center, but the strict terminal setup audit still fails `0 / 65`; this is simulation-only and not hardware evidence. Choose the next branch deliberately: run a broader terminal feasibility or gate-definition audit on the v54 contact-point model before designing another Stage A controller. Do not move or configure the real UR10e; real hardware work is read-only unless a separate approved SOP exists.
```

## Objective

Continue the UR10e + OnRobot force/torque sensor project from the current
`v54` repository state. The project goal is to reproduce the T-ASE finite-time
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
  `exp/tase-ur10e-v54-tcp-contact-point-model`
- Current v54 code commit:
  `1725f4c28796fc844dc1d350236755e6c4d59c28`
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

The v49-v50 provenance audits found that the legacy Fig.6 q7 landmark belongs
to a tuned `admittance_proxy` figure-match line with explicit q7 nullspace
bias, not the formula-faithful controller path. v52 implements that tuned line
in Python and matches the legacy figure-match raw trajectory to numerical
precision. Future work must still keep these claim levels separate.

Current next executable step:

- Continue UR10e adapted work with a broader terminal feasibility or
  gate-definition audit on the v54 contact-point model before designing
  another Stage A controller.

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
