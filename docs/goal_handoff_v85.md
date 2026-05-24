# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V85

Date: 2026-05-24

This handoff is meant to be pasted into a fresh Codex Goal Mode session. It is
intentionally detailed and operational. The next Codex should use it as the
goal-level objective, then verify every claim from the repository state before
editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v84 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v85.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/weighted_orientation_model_sensitivity_report.md`
- `runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, and not
hardware-ready. The UR10e adapted line is diagnostic simulation only. The v84
audit attributes the remaining `+1.0 mm`, `0.119 rad` weighted-row miss to a
small orientation/model margin, not to Stage B qdot saturation. The next work
should make a v85 branch and tighten the terminal/contact orientation
definition, measured geometry assumptions, or contact/normal calibration before
more Stage B qdot tuning.

Concrete v85 objective:

Create a bounded, evidence-backed v85 calibration/definition audit that answers
what physical or modeling correction would be sufficient to close the remaining
`+1.0 mm`, `0.119 rad` diagnostic orientation miss, without claiming recovery,
robustness, hardware readiness, or strict paper-equivalent parity unless the
new evidence actually proves those claims.

Expected branch:

- `exp/tase-ur10e-v85-contact-orientation-calibration`

Expected deliverables:

- one new script under `scripts/`
- one new lightweight run folder under `runs/`
- one new report under `reports/`
- updates to `docs/goal.md`, `reports/completion_audit.md`,
  `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`, and
  `runs/RUN_ARTIFACTS_MANIFEST.md`
- validation with `python3 -m py_compile <new script>`,
  `scripts/run_tests.sh`, `git diff --check`, and an artifact-size audit
- commit, push, and remote-ref verification if the user wants the branch
  published

Do not move the real UR10e. Do not write TCP, payload, URCap, zero, bias,
filter, OnRobot, or RTDE configuration. Hardware work is read-only only unless
the user approves a separate SOP.
```

## Repository State To Assume, Then Verify

The authoritative local clone is:

```text
/home/andy/reproduce-tase
```

The target GitHub repository is:

```text
git@github.com:Mingdao007/reproduce-tase.git
https://github.com/Mingdao007/reproduce-tase
```

Current verified branch before v85:

```text
exp/tase-ur10e-v84-orientation-model-sensitivity
```

Verified v84 experiment baseline before this handoff:

```text
fc79ab02117bff74b14c54f73f59d2bdb7fc897c
```

If this handoff file has been committed on top of that SHA, treat the later
commit as documentation-only handoff metadata, not as a new experiment result.
The next Codex should still branch from current `HEAD` unless there are
unexpected local changes.

Expected recent experiment commits before this handoff:

```text
fc79ab0 Mark v84 branch verified
8289d25 Add v84 orientation model sensitivity audit
79c2dd7 Mark v83 branch verified
8c97fda Add v83 weighted gate time matrix audit
b72ecec Mark v82 branch verified
4844902 Add v82 weighted timing recovery audit
```

The worktree was clean at handoff creation:

```text
## exp/tase-ur10e-v84-orientation-model-sensitivity...origin/exp/tase-ur10e-v84-orientation-model-sensitivity
```

The next Codex must verify this again. Do not trust this handoff if local state
has changed.

## Why V85 Exists

The project has a lot of simulation evidence, but the full reproduction is not
complete.

There are two major claim levels:

1. Strict paper-equivalent full staged feasibility.
   This is not achieved.
2. UR10e adapted diagnostic simulation evidence.
   This has several successful diagnostic branches, but it is not robust,
   not calibrated to the actual hardware stack, and not hardware-ready.

The latest v84 result narrowed the remaining active simulation blocker:

```text
remaining row = +1.0 mm, 0.119 rad diagnostic orientation gate
source evidence = v83 weighted gate/time matrix + v69 positive terminal orientation
max critical Stage B excess over gate = 0.0005664520369604714 rad
max critical Stage B excess deg = 0.03245531101442353 deg
qdot saturation in critical weighted rows = 0.0
contact-point +1.0 mm terminal orientation = 0.11948560786548146 rad
legacy-center +1.0 mm terminal orientation = 0.09525838838593075 rad
contact-point minus legacy-center orientation delta = 0.024227219479550713 rad
recovery claim = false
contact calibration claim = false
paper-equivalent feasibility = false
hardware readiness = false
```

Interpretation:

- The remaining miss is tiny compared with known model-convention sensitivity.
- It is not worth doing more Stage B qdot tuning first.
- The next useful work is to quantify contact/orientation definition and
  measured-geometry effects clearly enough to decide whether the gate is a
  modeling artifact, a measurement-calibration requirement, or a legitimate
  unrecovered control failure.

## What Has Been Done

This section is a compressed map. The next Codex must verify details from
`reports/completion_audit.md` and the run metrics before relying on them.

### Repo, Plans, And Audit Infrastructure

Done:

- GitHub target is `Mingdao007/reproduce-tase`.
- Iteration branches v37 through v84 have been pushed and verified.
- Mandatory plans exist:
  - `plans/MASTER_PLAN.md`
  - `plans/PAPER_TRUTH_EXTRACTION.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `plans/MUJOCO_ENVIRONMENT_PLAN.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/HARDWARE_GATE_SOP.md`
  - `plans/ROLLBACK_AND_CHECKPOINTS.md`
- Main audit and handoff files exist:
  - `docs/goal.md`
  - `reports/completion_audit.md`
  - `reports/ITERATION_LOG.md`
  - `reports/DECISION_RECORD.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- The latest test record says:
  - `python3 -m py_compile scripts/audit_weighted_orientation_model_sensitivity.py`
    passed.
  - `scripts/run_tests.sh`: `115 passed in 2.72s`.
  - `git diff --check` passed.
  - v84 rerun reproduced identical `metrics.yaml` and `metrics.json`.

### Paper-Platform Line

Done, but not complete as paper-equivalent parity:

- `paper_platform_7dof_formula_convergence` passes the v51 split gate.
- `paper_platform_7dof_tuned_figure_match_candidate` reproduces the legacy
  Fig.6 q7 landmark in a separate tuned line.
- v49-v50 showed the legacy q7 figure-match landmark belongs to a tuned
  `admittance_proxy` path with non-paper-faithful knobs, including q7
  nullspace bias.
- The project must not merge formula-faithful convergence and tuned-landmark
  evidence into one strict paper-equivalent claim.

Important files:

- `src/tase_repro/paper_7dof.py`
- `src/tase_repro/paper_platform_parity.py`
- `reports/paper_platform_split_claim_report.md`
- `reports/paper_7dof_tuned_figure_match_candidate_report.md`
- `reports/paper_7dof_tuned_figure_match_provenance_report.md`
- `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml`

### UR10e Adapted Simulation Line

Done:

- A relaxed diagnostic tilted-plane E1-E4 simulation line passes.
- v63 stitched diagnostic Stage A plus Stage B passes nominally.
- v72 recovers the full positive E1-E4 stitched matrix through `+1.0 mm` under
  a relaxed `0.12 rad` orientation envelope and slowed timing.
- v75 recovers the qdot012 positive stitched matrix after extending Stage A
  to `18.035 s`.
- v80 recovers the full positive planar-priority matrix under `0.11995 rad`.
- v82 and v83 show weighted zero-angular-command priority recovers the faster
  timing face through the full positive-delta `paper_time_scale = 0.01`,
  `0.11995 rad` matrix.

Still not done:

- The tighter `0.119 rad` orientation gate still fails at `+1.0 mm`.
- The current successful UR10e path is diagnostic simulation only.
- It is not robust, not strict paper-equivalent, not contact-calibrated, and
  not hardware-ready.

Important files:

- `src/tase_repro/stage_a_target_handoff.py`
- `src/tase_repro/stage_a_contact_path.py`
- `src/tase_repro/stage_a_contact_path_tracking.py`
- `src/tase_repro/base_z_recovery.py`
- `src/tase_repro/contact.py`
- `src/tase_repro/contact_manifold_gate_audit.py`
- `src/tase_repro/tcp_contact_model_audit.py`
- `src/tase_repro/force_feedback.py`
- `src/tase_repro/kinematics.py`
- `src/tase_repro/orientation.py`

### Contact And Orientation Evidence

Key v53-v56 evidence:

- The old 85 mm site was coincident with the colliding `contact_tip` sphere
  center.
- The contact-point variant offsets the sphere center so the 85 mm site
  represents the contact point.
- The strict terminal setup gates still fail after the convention fix.
- Contact-manifold audits show force, x/y, contact, and orientation gates are
  in tension under the current setup definition.

Key v69 evidence:

- In the contact-point model, positive terminal force/x-y/contact passes
  `8 / 8`.
- Diagnostic orientation passes `0 / 8`.
- Full-rotation and force-normal-only orientation errors are numerically
  identical, so yaw is not the limiting convention.
- Positive force/x-y/contact terminal cases need about `0.1195 rad`
  orientation margin through `+1.0 mm`.

Key v84 evidence:

- The critical v83 weighted rows miss the `0.119 rad` gate by less than
  `0.00057 rad`.
- The same critical rows have `0.0` qdot saturation.
- The contact-point versus legacy-center convention shifts +1.0 mm terminal
  orientation by about `0.024 rad`, much larger than the residual miss.

Important files:

- `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
- `configs/mujoco_ur10e_tilted_plane.yaml`
- `configs/ur10e_adapted_acceptance.yaml`
- `configs/ur10e_adapted_stage_a_target.yaml`
- `reports/tcp_contact_model_audit_report.md`
- `reports/tcp_contact_point_model_variant_report.md`
- `reports/positive_terminal_orientation_report.md`
- `reports/weighted_orientation_model_sensitivity_report.md`
- `runs/positive_terminal_orientation/20260524T171705/metrics.yaml`
- `runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml`
- `runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml`

## What Is Still Missing

The next Codex must not claim any of these as done unless it produces and
audits evidence:

- strict paper-equivalent full staged feasibility
- full paper-platform numerical parity
- robust UR10e adapted controller across contact/model perturbations
- measured mounted-stack TCP/contact geometry
- plane/contact normal calibration
- OnRobot/RTDE force-source reconciliation
- hardware gate report
- real robot motion authorization
- calibrated contact model
- accepted diagnostic gate definition that replaces the current ambiguity

The current highest-value missing item is the contact/orientation calibration
question around the remaining `+1.0 mm`, `0.119 rad` row.

## Recommended V85 Branch

Create a new branch from the verified v84 tip:

```bash
cd /home/andy/reproduce-tase
git status --short --branch
git switch -c exp/tase-ur10e-v85-contact-orientation-calibration
```

If the branch already exists, inspect it instead of overwriting it:

```bash
git branch --list 'exp/tase-ur10e-v85-contact-orientation-calibration'
git status --short --branch
git log --oneline --decorate -6
```

Do not use `git reset --hard` or discard any user changes.

## Concrete V85 Objective

V85 should be a bounded audit, not a broad controller rewrite.

The audit should answer:

1. What exact orientation margin remains at the hardest currently known row?
2. How large a contact normal angular correction would be required to close
   that margin?
3. How large an equivalent contact-point/TCP/base-z correction would be
   required under the current terminal slope proxy?
4. Which correction sizes are plausibly below measurement/calibration noise,
   and which require actual model changes?
5. Which specific physical measurements must be collected before any hardware
   claim is allowed?
6. Does any existing metric already justify accepting `0.119 rad`, `0.11955 rad`,
   `0.1196 rad`, or `0.11995 rad` as the diagnostic gate? If not, say so.
7. Does the result support more Stage B qdot tuning? The expected answer from
   v84 is no, unless the new audit finds contrary evidence.

Suggested v85 deliverable names:

```text
scripts/audit_contact_orientation_calibration_margin.py
runs/contact_orientation_calibration_margin/<timestamp>/metrics.yaml
runs/contact_orientation_calibration_margin/<timestamp>/metrics.json
runs/contact_orientation_calibration_margin/<timestamp>/summary.md
runs/contact_orientation_calibration_margin/<timestamp>/git_state.md
reports/contact_orientation_calibration_margin_report.md
```

If a better name emerges from reading the code, use it, but keep the names
specific and diagnostic. Avoid vague names like `next_audit.py`.

## Suggested V85 Computations

This is a suggested design. The next Codex should inspect existing scripts and
reuse local helpers instead of inventing incompatible patterns.

### Inputs

Read these YAML files:

```text
runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml
runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml
runs/positive_terminal_orientation/20260524T171705/metrics.yaml
runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml
configs/ur10e_adapted_acceptance.yaml
configs/ur10e_adapted_stage_a_target.yaml
configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml
```

Optionally read:

```text
reports/positive_terminal_orientation_report.md
reports/positive_orientation_gate_boundary_report.md
reports/weighted_gate_time_matrix_report.md
reports/weighted_orientation_model_sensitivity_report.md
```

### Metrics To Produce

Produce a top-level `metrics.yaml` with at least:

```yaml
run_source: v85 contact orientation calibration margin
source_runs:
  weighted_gate_time_matrix: ...
  weighted_orientation_model_sensitivity: ...
  positive_terminal_orientation: ...
  positive_orientation_gate_boundary: ...
current_gate_rad: 0.119
critical_rows:
  - group: ...
    paper_time_scale: ...
    scenario: ...
    base_z_offset_delta_mm: 1.0
    stage_a_terminal_orientation_rad: ...
    stage_b_max_orientation_rad: ...
    stage_b_excess_over_gate_rad: ...
    stage_b_excess_over_gate_deg: ...
    max_stage_b_qdot_saturation_fraction: ...
    max_stage_b_tail_qdot_utilization: ...
equivalent_corrections:
  required_normal_rotation_rad: ...
  required_normal_rotation_deg: ...
  terminal_slope_rad_per_mm: ...
  equivalent_base_z_or_contact_point_mm: ...
  equivalent_base_z_or_contact_point_um: ...
gate_options:
  current_0p119:
    recovered: false
  v83_min_passing_time0p0075:
    gate_rad: 0.11955
    recovered: true
  v83_min_passing_time0p01:
    gate_rad: 0.1196
    recovered: true
  diagnostic_0p11995:
    gate_rad: 0.11995
    recovered: true
claim_boundary:
  recovery_claim: false
  contact_calibration_claim: false
  paper_equivalent_feasibility: false
  hardware_readiness: false
next_measurements:
  - measured mounted stack TCP/contact point from flange
  - contact sphere or contact patch convention
  - plane normal in robot base frame
  - force sensor zero/frame reconciliation
```

The exact schema can differ, but it must be structured enough for future
audits to consume without parsing prose.

### Useful Existing Helper Patterns

Reuse these patterns:

- `scripts/audit_weighted_orientation_model_sensitivity.py`
  for post-hoc source-run loading, compact summaries, and git state writing.
- `scripts/audit_positive_terminal_orientation.py`
  for contact-point versus legacy-center terminal comparisons.
- `scripts/audit_weighted_gate_time_matrix.py`
  for the weighted matrix source structure.
- `audit_stage_a_base_z_recovery.write_git_state`
  if still appropriate for writing run provenance.

Do not duplicate large blocks blindly. Extract a small helper only if it
reduces real duplication and matches existing repo style.

## V85 Validation Requirements

At minimum:

```bash
python3 -m py_compile scripts/audit_contact_orientation_calibration_margin.py
python3 scripts/audit_contact_orientation_calibration_margin.py
scripts/run_tests.sh
git diff --check
```

Also audit the new run folder:

```bash
find runs/contact_orientation_calibration_margin/<timestamp> -type f | wc -l
du -sh runs/contact_orientation_calibration_margin/<timestamp>
find runs/contact_orientation_calibration_margin/<timestamp> -type f \
  \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' \
     -o -name '*.gz' -o -name '*.zip' \) -print
```

The run folder should contain lightweight text artifacts only:

- `metrics.yaml`
- `metrics.json`
- `summary.md`
- `git_state.md`

If extra files are needed, explain them in `runs/RUN_ARTIFACTS_MANIFEST.md`.

If any generated artifact is large, binary, or raw array data, do not commit it
unless Git LFS is explicitly configured. Prefer a manifest entry and local
path documentation.

## V85 Reporting Requirements

Create:

```text
reports/contact_orientation_calibration_margin_report.md
```

The report should include:

- objective
- source runs
- exact command
- parent commit before v85 changes
- table of critical rows
- table of equivalent corrections
- interpretation
- explicit claim boundary
- validation results
- next executable step

Update:

```text
reports/ITERATION_LOG.md
reports/DECISION_RECORD.md
reports/completion_audit.md
runs/RUN_ARTIFACTS_MANIFEST.md
docs/goal.md
```

The updates must say exactly what v85 proves and what it does not prove.

Suggested decision title:

```text
D090: Treat The Remaining 0.119 Rad Miss As A Calibration-Definition Margin
```

Use a different title if the data says something else.

## Completion Criteria For V85

V85 is complete only if all of these are true:

- A dedicated branch exists or the work is otherwise clearly scoped.
- The new script runs from a clean command and writes a reproducible run folder.
- The new metrics answer the seven questions in the V85 objective.
- The new report describes the result without overstating claims.
- The iteration log, decision record, completion audit, run manifest, and goal
  handoff are updated.
- `python3 -m py_compile <new script>` passes.
- `scripts/run_tests.sh` passes.
- `git diff --check` passes.
- The new artifact folder is lightweight and documented.
- The worktree has no unrelated changes.
- If pushed, the remote ref is verified with `git ls-remote`.

Do not mark the overall T-ASE reproduction complete unless the repository
audit proves:

- strict paper-equivalent full staged feasibility, or an explicitly accepted
  revised paper-equivalent criterion
- formula-faithful paper-platform parity, not just tuned Fig.6 landmark
  reproduction
- robust UR10e adapted performance under the selected perturbation matrix
- measured and accepted contact/TCP/normal/force-source calibration
- approved hardware gate and SOP if hardware readiness is claimed

## Recommended Final Response Shape For Next Codex

After finishing v85, report:

- branch
- commit SHA
- run folder
- report path
- key numeric conclusion
- validation commands and results
- whether the broader reproduction is still incomplete
- next executable step

Keep the final answer honest. It is acceptable, and likely correct, to say:

```text
v85 improves the evidence boundary, but the overall reproduction is still not
strict paper-equivalent, not robust, and not hardware-ready.
```

## Safety Rules

These are non-negotiable unless the user explicitly starts a separate hardware
SOP:

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP.
- Do not write payload.
- Do not write CoG.
- Do not write URCap settings.
- Do not zero, bias, or filter the OnRobot sensor.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if they are relevant and safe.

Known hardware facts from `docs/goal.md`:

```text
UR10e IP: 192.168.1.18
URSoftware: 5.11.9.1010452
OnRobot Compute Box IP: 192.168.1.1
URCap: FT-OnRobot 4.1.7
Compute Box observed web version: 4.1.8
temporary payload readback: 0.44 kg
temporary CoG readback: [0.005, -0.005, 0.025] m
temporary TCP readback: [0, 0, 0.12254, 0, 0, 0]
EOAT v13 candidate contact point: 85.0 mm from design flange face
OnRobot direct TCP DAQ disagreement: about -32 N against PolyScope/RTDE
```

These facts are not permission to write configuration.

## Practical First 15 Minutes For Next Codex

Run:

```bash
cd /home/andy/reproduce-tase
git status --short --branch
git log --oneline --decorate -6
git remote -v
sed -n '1,290p' docs/goal.md
sed -n '1,230p' reports/completion_audit.md
sed -n '1,120p' reports/weighted_orientation_model_sensitivity_report.md
sed -n '1,180p' runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml
sed -n '1,220p' scripts/audit_weighted_orientation_model_sensitivity.py
```

Then create the branch:

```bash
git switch -c exp/tase-ur10e-v85-contact-orientation-calibration
```

Then inspect the source structures:

```bash
sed -n '1,220p' scripts/audit_weighted_gate_time_matrix.py
sed -n '1,260p' scripts/audit_positive_terminal_orientation.py
sed -n '1,220p' runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml
sed -n '1,220p' runs/positive_terminal_orientation/20260524T171705/metrics.yaml
```

Do not run broad expensive sweeps until the post-hoc audit design is clear.

## Handoff Completion Audit

This handoff itself was created from the following local evidence:

- `git status --short --branch` showed a clean v84 branch tracking origin.
- `git log --oneline --decorate -6` showed v84 verified at `fc79ab0`.
- `docs/goal.md` identified v84 as the current state and named the next
  executable step.
- `reports/completion_audit.md` stated that the overall reproduction is not
  complete, strict paper-equivalent feasibility is not achieved, and hardware
  readiness is false.
- `reports/completion_audit.md` also recorded the latest v84 validation:
  `scripts/run_tests.sh` reported `115 passed in 2.72s`, `git diff --check`
  passed, and the v84 metrics were reproducible.

If any of that evidence changes before the next Codex starts, the next Codex
must update this handoff or treat it as historical rather than current.
