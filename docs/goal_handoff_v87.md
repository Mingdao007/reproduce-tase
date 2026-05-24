# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V87

Date: 2026-05-25

Use this after the v86 measured-geometry readiness audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v86 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v87.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/measured_geometry_readiness_report.md`
- `runs/measured_geometry_readiness/20260525T000739/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V85 quantified the remaining weighted `+1.0 mm`,
`0.119 rad` miss as `0.0005664520369604714 rad`
(`0.03245531101442353 deg`) of normal-orientation margin, equivalent to
`0.014963398168061883 mm` (`14.963398168061882 um`) under the terminal slope
proxy. V86 found current local records insufficient to accept that margin:
the `85.0 mm` contact point is CAD/design metadata, current UR TCP
`[0, 0, 0.12254, 0, 0, 0]` is temporary and not contact-validated, the KSM
contact patch is unverified, the plane normal is analytic MuJoCo geometry,
and direct TCP DAQ force values still disagree with RTDE/PolyScope by about
`32 N`.

Concrete v87 objective:

Create a read-only measurement/SOP artifact that defines exactly how to
collect the missing calibration evidence for mounted-stack TCP/contact point,
KSM contact patch convention, plane normal in robot base frame,
force-source/frame reconciliation, and accepted orientation-gate semantics.
The SOP must include pass/fail gates, expected artifacts, safety boundaries,
and rollback/abort conditions. It must not move the real UR10e or write TCP,
payload, URCap, zero, bias, filter, OnRobot, or RTDE configuration unless the
user separately approves that exact hardware step.
```

## Current Verified V86 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v86-measured-geometry-readiness
```

V86 formal run:

```text
runs/measured_geometry_readiness/20260525T000739
```

Key result:

```text
records_sufficient_for_v85_margin = false
supports_accepting_v85_margin = false
supports_gate_relaxation = false
supports_hardware_claim = false
supports_more_stage_b_qdot_tuning = false
hardware_access_mode = read-only local record inspection
```

## Recommended V87 Work

Highest-value next question:

```text
What exact read-only measurement/SOP would produce the missing evidence needed
to decide whether the v85 `0.03246 deg` / `14.96 um` margin is a calibrated
physical correction or only a simulation artifact?
```

Suggested deliverables:

- one new report/SOP under `reports/`
- optionally one verifier script under `scripts/` if the SOP can be checked
  mechanically
- updates to `docs/goal.md`, `reports/completion_audit.md`,
  `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`, and
  `runs/RUN_ARTIFACTS_MANIFEST.md`

The SOP should cover:

1. Mounted-stack TCP/contact point measurement from a named flange/sensor/tool
   datum.
2. KSM-8N contact patch or ball datum convention, including loaded/unloaded
   state.
3. Plane normal measurement in robot base frame, with angle uncertainty
   compared to `0.03245531101442353 deg`.
4. Force-source/frame reconciliation between OnRobot URCap variables, UR RTDE,
   and direct TCP DAQ, without using direct TCP DAQ as control truth until
   reconciled.
5. Orientation-gate semantics: force-normal-only versus full-frame rotation,
   and the uncertainty budget required before any gate relaxation.
6. Required artifacts: photos, raw logs, measurement worksheets, command
   outputs, git state, and pass/fail summary.
7. Abort gates: any robot motion, any write to TCP/payload/CoG/URCap/OnRobot
   settings, any force-control attempt, or any force-source mismatch left
   unresolved.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zero/bias/filter, OnRobot
  configuration, or RTDE registers unless the user approves a separate exact
  SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant and safe.
