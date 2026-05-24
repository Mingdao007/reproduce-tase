# TCP Contact-Point Model Variant Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v54-tcp-contact-point-model`

## Scope

This iteration replaces the ambiguous v53 TCP/contact convention with a
simulation-only variant where the EOAT 85 mm site is treated as the intended
contact point when TCP local `+z` is aligned with the surface normal.

No real UR10e motion, TCP writes, payload writes, URCap writes, ROS config
writes, or OnRobot configuration changes were performed.

## Model Change

Added:

- `assets/mjcf/ur10e_tilted_plane_10deg_tcp_contact_point.xml`
- `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`

The variant keeps:

- `tcp_guess_m = [0, 0, -0.085]`
- `tcp_site_unverified_85mm` at the EOAT candidate contact point
- `contact_tip` sphere radius `0.045 m`

The variant changes:

- `contact_tip` sphere center from site-coincident to local
  `pos="0 0 0.045"`
- calibrated 5 N initial-posture base-z offset to
  `-0.04612594095298278 m`

This means the colliding sphere sits behind the TCP site, so the sphere surface
is near the 85 mm site when TCP local `+z` aligns with the surface normal.

## TCP/Contact Audit

Run:

- `runs/tcp_contact_model_audit/20260524T140535`

Command:

```bash
scripts/audit_tcp_contact_model.py \
  --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml
```

Result:

- config TCP guess matches model body offset: `True`
- config TCP guess matches EOAT note distance: `True`
- site coincident with contact geom center: `False`
- contact surface offset requires model decision: `False`
- contact geom local position: `[0.0, 0.0, 0.045]`
- normal force at audited posture: `4.9999999999967395 N`
- site-to-sphere-surface projection on normal:
  `0.0006836511144550518 m`
- parent-to-sphere-surface distance: `0.0846776706744086 m`
- surface extension beyond declared TCP: `-0.00068365111445505 m`

The residual `0.684 mm` projection is expected for the initial posture because
TCP local `+z` is still `10 deg` away from the tilted plane normal.

## Terminal IK Rerun

Run:

- `runs/setup_terminal_ik_audit/20260524T140539`

Command:

```bash
scripts/run_setup_terminal_ik_probe.py \
  --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml \
  --random-seed-count 64 \
  --random-seed-std-rad 0.15 \
  --random-seed 37 \
  --max-nfev 300 \
  --posture-weight 0.0001
```

Result:

- terminal candidates: `65`
- terminal setup passes: `0 / 65`
- initial force error: `3.2605029787191597e-12 N`
- initial x/y error: `0.0 m`
- initial orientation error: `0.17453292523412012 rad`
- best seed: `random_006`
- best force error: `0.0050975519688662985 N`
- best x/y error: `0.0030075788240061675 m`
- best orientation error: `0.07240603253666981 rad`
- best failed criteria: `tangential_error_m;orientation_error_rad`

## Conclusion

The v54 replacement resolves the v53 center/site coincidence for a named
contact-point convention, but it does not solve the strict setup terminal
gate. Under the same local seed set, the strict terminal audit remains
`0 / 65`, with the best candidate farther outside the x/y and orientation
gates than the v53 center-site model.

The next useful simulation step is a broader terminal feasibility audit or a
gate-definition audit, not more scalar phase scheduling. Hardware use still
requires measured mounted-stack geometry and an explicit hardware SOP.

## Verification

- `scripts/run_tests.sh tests/test_tcp_contact_model_audit.py` -> `3 passed`
- `scripts/run_tests.sh` -> `88 passed in 2.25s`
- `git diff --check` passed
