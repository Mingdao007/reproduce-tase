# Paper 7DOF Executable Diagnostic Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v41-paper-7dof-line`

## Scope

This branch creates the first separate paper-platform 7DOF executable line in
this repo. It is deliberately separate from the UR10e adapted MuJoCo line.

The line covers the paper Section V 7DOF diagnostic setup:

- Panda/Franka-style 7 joint kinematics and 6x7 geometric Jacobian.
- Section V q0, circular desired trajectory, 5 N normal force target, joint
  limits, velocity limits, and finite-time inner-loop projection.
- Explicit `z0` convention: `q0` forward-kinematics height, because v40
  verified that Section V uses `z0` without defining it.

## Added Executable Surface

- `src/tase_repro/panda_kinematics.py`
- `src/tase_repro/paper_7dof.py`
- `scripts/run_paper_7dof_section_v.py`
- `tests/test_panda_kinematics.py`
- `tests/test_paper_7dof.py`

The Panda kinematics are ported from the legacy MATLAB files:

- `forward_panda.m`
- `getJacobian_panda.m`

The inherited DH parameters are still treated as audit-derived and need vendor
or manual confirmation before any paper-faithful platform claim.

## Command

```bash
scripts/run_paper_7dof_section_v.py \
  --duration-s 5.0 \
  --dt-s 0.002 \
  --solver-mode kkt_projection \
  --orientation-mode force_shortest_arc
```

Run:

`runs/paper_7dof_section_v/20260524T113608`

Git state recorded by run:

- commit: `bf7209d52476d951e99f6ed7cbce1c7acc3db0e8`
- dirty status before output creation: clean

## Metrics

| Metric | Value |
|---|---:|
| execution success | `true` |
| contact-force tail success | `false` |
| duration | `5.0 s` |
| sample count | `2501` |
| max abs q | `2.4995864840253907 rad` |
| max abs qdot | `0.6318376969546269 rad/s` |
| q bound violations | `0` |
| qdot bound violations | `0` |
| velocity clamp fraction | `0.5613754498200719` |
| contact fraction | `0.273890443822471` |
| tail contact fraction | `0.0` |
| task residual RMS | `0.08147063929087314` |
| tail position error mean | `0.0030910509183547244 m` |
| tail orientation error mean | `0.00018635025045757645 rad` |
| tail force error mean | `5.0 N` |

## Interpretation

The v41 line proves the repo now has a separate executable 7DOF paper-platform
diagnostic path. It does not prove paper-faithful Fig.5/Fig.6 parity.

The hard joint and velocity bounds are respected, and the run remains finite.
However, the paper-literal force loop loses contact in the tail window:
`tail_contact_fraction = 0.0` and `tail_force_error_mean_N = 5.0`.

The correct claim after v41 is:

```text
paper_platform_7dof_executable_diagnostic exists
contact_force_tail_success = false
paper-faithful numerical parity = false
hardware readiness = false
```

## Limits

- The DH model is inherited from legacy MATLAB audit files, not independently
  verified against Franka/Panda vendor data.
- The paper's desired-rotation equation is dimensionally ambiguous; this
  branch uses the documented shortest-arc force-normal interpretation.
- No real robot commands were run.
- This branch does not change the accepted UR10e adapted result.

## Next Step

For the paper-platform line, debug the normal-force/contact loop before using
it for any paper-equivalent claim. The first target is to make the 7DOF
diagnostic maintain tail contact and reduce tail force error without violating
the paper Section V joint or velocity bounds.
