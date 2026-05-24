# TCP Contact Model Audit Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v53-tcp-contact-model-audit`

## Scope

This iteration validates the current approximate UR10e + OnRobot + EOAT
MuJoCo TCP/contact convention before any further Stage A controller work. It
does not move the real UR10e and does not write TCP, payload, URCap, ROS, or
OnRobot settings.

The audit compares three points in the current tilted-plane MJCF:

- the configured TCP guess from `configs/mujoco_ur10e_tilted_plane.yaml`
- the model site `tcp_site_unverified_85mm`
- the colliding sphere `contact_tip` and its actual plane-contact surface

## Artifacts

- TCP/contact audit run:
  `runs/tcp_contact_model_audit/20260524T135607`
- Terminal IK rerun:
  `runs/setup_terminal_ik_audit/20260524T135619`

## Command

```bash
scripts/audit_tcp_contact_model.py
```

## Result

- Config TCP guess matches model body offset: `True`
- Config TCP guess matches EOAT note distance: `True`
- Site coincident with contact geom center: `True`
- Contact surface offset requires model decision: `True`
- Parent-to-site distance: `0.085 m`
- Contact sphere radius: `0.045 m`
- Contact count at audited posture: `1`
- Normal force at audited posture: `5.000000003321885 N`
- Site-to-sphere-surface projection on contact normal: `0.04500000000000001 m`
- Parent-to-sphere-surface distance: `0.12955222618906498 m`
- Surface extension beyond declared TCP: `0.04431634888554499 m`

## Interpretation

The current model is internally consistent with the written 85 mm TCP guess:
the config vector `[0, 0, -0.085]` matches the MJCF body offset and the EOAT
note distance.

The contact convention is not resolved. The TCP site is at the center of the
colliding sphere, not at the simulated contact surface. MuJoCo contact with
the plane occurs about one sphere radius away from that site. In the audited
5 N posture, that makes the simulated surface point about `129.55 mm` from the
OnRobot primitive origin rather than `85 mm`.

That means the current model is one of two unverified conventions:

- `85 mm` means sphere center or tool frame, in which case the physical
  contact point is not the configured TCP; or
- `85 mm` means the actual contact point from the EOAT note, in which case the
  current sphere collision model adds about `45 mm` of extra reach.

## Terminal IK Rerun

The terminal setup audit was rerun after the TCP/contact audit:

```bash
scripts/run_setup_terminal_ik_probe.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --random-seed-count 64 \
  --random-seed-std-rad 0.15 \
  --random-seed 37 \
  --max-nfev 300 \
  --posture-weight 0.0001
```

The rerun reproduces the previous result:

- terminal candidates: `65`
- terminal setup passes: `0 / 65`
- initial force error: `3.3218849893046354e-09 N`
- initial x/y error: `0.0 m`
- initial orientation error: `0.17453292523412012 rad`
- best force error: `0.004835673570861232 N`
- best x/y error: `0.002178947478445584 m`
- best orientation error: `0.05199834145021794 rad`
- best failed criteria: `tangential_error_m;orientation_error_rad`

## Conclusion

The current approximate TCP/contact model is not hardware-ready. It is good
enough to explain why the terminal setup gate should not be trusted as a
hardware statement: the model has not decided whether the 85 mm EOAT note is a
TCP/contact point or a sphere-center/tool-frame point.

The next model step should create an explicit replacement variant with a named
contact-point convention, or measure the mounted stack and update the MJCF,
URDF, and config from that measurement before attempting any hardware gate.

## Verification

- `scripts/run_tests.sh tests/test_tcp_contact_model_audit.py` -> `2 passed`
- `scripts/run_tests.sh` -> `87 passed in 2.25s`
- `git diff --check` passed
