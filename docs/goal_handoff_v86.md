# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V86

Date: 2026-05-24

Use this after the v85 contact-orientation calibration-margin audit. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v85 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v86.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/contact_orientation_calibration_margin_report.md`
- `runs/contact_orientation_calibration_margin/20260524T235723/metrics.yaml`

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
proxy. Existing metrics show scoped recovery at `0.11955`, `0.1196`, and
`0.11995 rad`, but none of those gates is accepted without calibrated
geometry/contact-normal evidence.

Concrete v86 objective:

Create a bounded measured-geometry/contact-normal readiness audit that answers
which existing local records already constrain the mounted-stack TCP/contact
point, contact patch convention, plane normal, and force-source/frame
definition tightly enough to support or reject the v85 calibration margin.
If the records are insufficient, produce a measurement checklist and do not
claim recovery, robustness, hardware readiness, or strict paper-equivalent
parity.

Do not move the real UR10e. Do not write TCP, payload, URCap, zero, bias,
filter, OnRobot, or RTDE configuration. Hardware work is read-only only unless
the user approves a separate SOP.
```

## Current Verified V85 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v85-contact-orientation-calibration
```

V85 formal run:

```text
runs/contact_orientation_calibration_margin/20260524T235723
```

Key result:

```text
hardest row = time0p01_gate0p119:weighted_kp0_normal1
current gate = 0.119 rad
required normal rotation = 0.0005664520369604714 rad
required normal rotation = 0.03245531101442353 deg
equivalent base-z/contact-point correction = 0.014963398168061883 mm
equivalent base-z/contact-point correction = 14.963398168061882 um
accepted replacement gate = false
recovery claim = false
contact calibration claim = false
paper-equivalent feasibility = false
hardware readiness = false
```

## Recommended V86 Work

Highest-value next question:

```text
Do existing local geometry/CAD/hardware records constrain the TCP/contact
point, contact patch, plane normal, and force-source frame tightly enough to
make the v85 `0.0325 deg` / `15 um` margin meaningful?
```

Suggested deliverables:

- one new script under `scripts/`
- one lightweight run folder under `runs/`
- one report under `reports/`
- updates to `docs/goal.md`, `reports/completion_audit.md`,
  `reports/ITERATION_LOG.md`, `reports/DECISION_RECORD.md`, and
  `runs/RUN_ARTIFACTS_MANIFEST.md`

Suggested local records to inspect read-only:

- `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/current_hardware_state.md`
- `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/EOAT_TCP_NOTE.md`
- `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/v13_ksm8n_receiver_5p3mm_side_window_85mm/`
- `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
- `assets/mjcf/ur10e_tilted_plane_10deg_tcp_contact_point.xml`

Questions to answer:

1. Is there a measured mounted-stack TCP/contact point, or only a CAD/design
   candidate?
2. Is the `85.0 mm` EOAT datum a contact surface, a sphere center, or a
   design-reference point?
3. Is the plane/contact normal measured in the robot base frame, or only an
   analytic MuJoCo assumption?
4. Is the force source/frame reconciled between UR RTDE/PolyScope and OnRobot
   direct TCP DAQ?
5. Is any existing measurement uncertainty small enough to justify accepting a
   `0.0325 deg` or `15 um` correction? If not, say so.
6. What exact measurement/SOP is required before any gate relaxation or
   hardware claim?
7. Does the result support more Stage B qdot tuning? The expected answer from
   v85 is still no unless new evidence contradicts it.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zero/bias/filter, or OnRobot
  configuration.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant and safe.
